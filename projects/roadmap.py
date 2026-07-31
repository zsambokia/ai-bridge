"""Governed, project-scoped roadmap lifecycle and AKB feedback service."""

from __future__ import annotations

import re

from django.db import transaction

from .knowledge import create_or_upsert_candidate
from .models import GovernanceApproval, Project, RoadmapItem, RoadmapUpdateCandidate


def _string_list(value: object, error: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(entry, str) and entry for entry in value
    ):
        raise ValueError(error)
    return value


def create_item(project: Project, data: dict[str, object]) -> RoadmapItem:
    """Register a proposed roadmap item; only governed review may progress it."""
    item_key = str(data["item_key"])
    item, created = RoadmapItem.objects.get_or_create(
        project=project,
        item_key=item_key,
        defaults={
            "title": str(data["title"]),
            "epic_reference": str(data.get("epic_reference", "")),
            "sprint_reference": str(data.get("sprint_reference", "")),
            "dependencies": _string_list(
                data.get("dependencies", []), "ROADMAP_DEPENDENCIES_INVALID"
            ),
        },
    )
    if not created and item.title != str(data["title"]):
        raise ValueError("ROADMAP_ITEM_IDENTITY_CONFLICT")
    return item


def propose_update(
    project: Project, item_key: str, data: dict[str, object]
) -> RoadmapUpdateCandidate:
    """Persist an automatic delivery signal as a candidate, never as completion."""
    item = RoadmapItem.objects.get(project=project, item_key=item_key)
    state = str(data["proposed_state"])
    if state not in RoadmapItem.State.values:
        raise ValueError("ROADMAP_STATE_INVALID")
    evidence = _string_list(
        data.get("evidence_references", []), "ROADMAP_EVIDENCE_REQUIRED"
    )
    if not evidence:
        raise ValueError("ROADMAP_EVIDENCE_REQUIRED")
    final_sha = str(data.get("final_commit_sha", ""))
    if final_sha and not re.fullmatch(r"[0-9a-f]{40}", final_sha):
        raise ValueError("ROADMAP_FINAL_SHA_INVALID")
    candidate, created = RoadmapUpdateCandidate.objects.get_or_create(
        idempotency_key=str(data["idempotency_key"]),
        defaults={
            "item": item,
            "proposed_state": state,
            "engineering_status": str(data.get("engineering_status", "PENDING")),
            "operational_status": str(data.get("operational_status", "PENDING")),
            "evidence_references": evidence,
            "final_commit_sha": final_sha,
            "source_reference": str(data["source_reference"]),
        },
    )
    if not created and candidate.item_id != item.pk:
        raise ValueError("ROADMAP_IDEMPOTENCY_CONFLICT")
    return candidate


def _approval(project: Project, reference: str) -> GovernanceApproval:
    approval = GovernanceApproval.objects.filter(
        reference=reference, project=project, revoked_at__isnull=True
    ).first()
    if approval is None:
        raise ValueError("APPROVAL_REQUIRED")
    if approval.approved_action not in {
        "roadmap.review_update_candidate",
        "ROADMAP_PROGRESS",
        "ALL_GOVERNED_MUTATIONS",
        "ALL",
    }:
        raise ValueError("APPROVAL_ACTION_NOT_AUTHORIZED")
    return approval


def review_update(
    project: Project,
    candidate_id: int,
    decision: str,
    actor: str,
    approval_reference: str = "",
) -> RoadmapUpdateCandidate:
    """Review a delivery signal and create a governed AKB feedback candidate."""
    with transaction.atomic():
        candidate = (
            RoadmapUpdateCandidate.objects.select_for_update()
            .select_related("item")
            .get(pk=candidate_id, item__project=project)
        )
        if candidate.status != RoadmapUpdateCandidate.Status.CANDIDATE:
            raise ValueError("ROADMAP_REVIEW_STATE_INVALID")
        if decision == "REJECT":
            candidate.status = RoadmapUpdateCandidate.Status.REJECTED
            candidate.save(update_fields=["status", "updated_at"])
            return candidate
        if decision != "APPROVE":
            raise ValueError("ROADMAP_REVIEW_DECISION_INVALID")
        _approval(project, approval_reference)
        if candidate.proposed_state == RoadmapItem.State.COMPLETED and (
            candidate.engineering_status != "PASS"
            or candidate.operational_status != "PASS"
            or not candidate.final_commit_sha
        ):
            raise ValueError("ROADMAP_COMPLETION_ACCEPTANCE_REQUIRED")
        item = candidate.item
        item.state = candidate.proposed_state
        item.engineering_status = candidate.engineering_status
        item.operational_status = candidate.operational_status
        item.evidence_references = candidate.evidence_references
        item.final_commit_sha = candidate.final_commit_sha
        item.save()
        candidate.status = RoadmapUpdateCandidate.Status.ACTIVE
        candidate.approval_reference = approval_reference
        candidate.save(update_fields=["status", "approval_reference", "updated_at"])
        create_or_upsert_candidate(
            project,
            {
                "entry_key": (
                    f"roadmap-feedback:{project.project_id}:{item.item_key}:"
                    f"{candidate.pk}"
                ),
                "scope": "PROJECT",
                "knowledge_type": "ROADMAP",
                "title": f"Accepted roadmap update: {item.title}",
                "content": (
                    f"{item.item_key} is {item.state}; engineering="
                    f"{item.engineering_status}; operational="
                    f"{item.operational_status}."
                ),
                "source_type": "ROADMAP_LIFECYCLE",
                "source_reference": candidate.source_reference,
                "evidence_references": candidate.evidence_references,
                "work_context_id": f"roadmap:{item.item_key}",
                "source_version": str(candidate.updated_at.timestamp()),
            },
            actor,
        )
    return candidate

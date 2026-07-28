"""Provider-neutral AKB domain service used by MCP and the Orchestrator."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import GovernanceApproval, KnowledgeEntry, KnowledgeRevision, Project
from .orchestration_context import PLATFORM_CONTEXT_ID, bind

PROTECTED_TYPES = {"CONSTITUTION", "ROADMAP", "UI_PLAN", "SYSTEM_DESIGN"}
ALLOWED_TYPES = PROTECTED_TYPES | {
    "INCIDENT_LESSON",
    "RUNBOOK",
    "POLICY",
    "ARCHITECTURE_DECISION",
    "GENERAL",
}


def _context(project: Project, work_context_id: str) -> dict[str, str]:
    return bind(project, work_context_id).as_dict()


def _metadata(entry: KnowledgeEntry) -> dict[str, Any]:
    return {
        "entry_id": entry.pk,
        "entry_key": entry.entry_key,
        "scope": entry.scope,
        "knowledge_type": entry.knowledge_type,
        "title": entry.title,
        "status": entry.status,
        "verification_status": entry.verification_status,
        "freshness_status": freshness(entry),
        "version": entry.version,
        "source_reference": entry.source_reference,
        "evidence_references": entry.evidence_references,
        "platform_context_id": entry.platform_context_id,
        "project_context_id": entry.project_context_id,
        "work_context_id": entry.work_context_id,
        "role_context": entry.role_context,
        "is_must_know": entry.is_must_know,
    }


def freshness(entry: KnowledgeEntry) -> str:
    if entry.review_due_at and entry.review_due_at <= timezone.now():
        return "STALE"
    return entry.freshness_status


def _validate_input(data: dict[str, Any]) -> None:
    if data.get("knowledge_type") not in ALLOWED_TYPES:
        raise ValueError("AKB_KNOWLEDGE_TYPE_INVALID")
    for key, maximum in (
        ("entry_key", 160),
        ("title", 255),
        ("content", 12000),
        ("source_reference", 255),
    ):
        if (
            not isinstance(data.get(key), str)
            or not data[key].strip()
            or len(data[key]) > maximum
        ):
            raise ValueError("AKB_ENTRY_INVALID")
    if not isinstance(data.get("evidence_references", []), list) or not all(
        isinstance(item, str) and item for item in data.get("evidence_references", [])
    ):
        raise ValueError("AKB_EVIDENCE_INVALID")
    if not isinstance(data.get("role_context", []), list) or not all(
        isinstance(item, str) for item in data.get("role_context", [])
    ):
        raise ValueError("AKB_ROLE_CONTEXT_INVALID")


def _approval(project: Project, reference: str, action: str) -> GovernanceApproval:
    try:
        approval = GovernanceApproval.objects.get(
            reference=reference, project=project, revoked_at__isnull=True
        )
    except GovernanceApproval.DoesNotExist as exc:
        raise ValueError("APPROVAL_REQUIRED") from exc
    if approval.approved_action not in {
        action,
        "AKB_PUBLISH",
        "ALL_GOVERNED_MUTATIONS",
        "ALL",
    }:
        raise ValueError("APPROVAL_ACTION_NOT_AUTHORIZED")
    return approval


def create_or_upsert_candidate(
    project: Project, data: dict[str, Any], actor: str, *, upsert: bool = False
) -> KnowledgeEntry:
    """Create or revise only a non-published candidate; project isolation is binding."""
    _validate_input(data)
    scope = data.get("scope", KnowledgeEntry.Scope.PROJECT)
    if scope not in {KnowledgeEntry.Scope.PLATFORM, KnowledgeEntry.Scope.PROJECT}:
        raise ValueError("AKB_SCOPE_INVALID")
    if scope == KnowledgeEntry.Scope.PLATFORM and project.project_id != "ai-bridge":
        raise ValueError("AKB_PLATFORM_WRITE_DENIED")
    context = _context(project, data.get("work_context_id") or "akb:authoring")
    with transaction.atomic():
        entry = (
            KnowledgeEntry.objects.select_for_update()
            .filter(entry_key=data["entry_key"])
            .first()
        )
        if entry is not None:
            if (
                entry.scope == KnowledgeEntry.Scope.PROJECT
                and entry.project_id != project.pk
            ):
                raise ValueError("AKB_CROSS_PROJECT_DENIED")
            if not upsert:
                raise ValueError("AKB_ENTRY_EXISTS")
            if entry.status not in {
                KnowledgeEntry.Status.CANDIDATE,
                KnowledgeEntry.Status.IN_REVIEW,
                KnowledgeEntry.Status.REJECTED,
            }:
                raise ValueError("AKB_PUBLISHED_ENTRY_REQUIRES_REVIEW")
            previous = entry.version
            for name in (
                "title",
                "content",
                "source_reference",
                "verification_status",
                "freshness_status",
                "knowledge_owner_role",
                "is_must_know",
                "evidence_references",
                "role_context",
            ):
                if name in data:
                    setattr(entry, name, data[name])
            entry.work_context_id = context["work_context_id"]
            entry.status = KnowledgeEntry.Status.CANDIDATE
            entry.version += 1
            entry.save()
            reason = "UPSERT_CANDIDATE"
        else:
            entry = KnowledgeEntry.objects.create(
                project=None if scope == KnowledgeEntry.Scope.PLATFORM else project,
                scope=scope,
                platform_context_id=PLATFORM_CONTEXT_ID,
                project_context_id=""
                if scope == KnowledgeEntry.Scope.PLATFORM
                else context["project_context_id"],
                work_context_id=context["work_context_id"],
                entry_key=data["entry_key"],
                knowledge_type=data["knowledge_type"],
                title=data["title"],
                content=data["content"],
                source_type=data.get("source_type", "MCP"),
                source_reference=data["source_reference"],
                evidence_references=data.get("evidence_references", []),
                role_context=data.get("role_context", []),
                verification_status=data.get("verification_status", "UNVERIFIED"),
                freshness_status=data.get("freshness_status", "CURRENT"),
                knowledge_owner_role=data.get("knowledge_owner_role", "ENGINEERING"),
                is_must_know=bool(data.get("is_must_know", False)),
                status=KnowledgeEntry.Status.CANDIDATE,
            )
            previous, reason = 0, "CREATE_CANDIDATE"
        KnowledgeRevision.objects.create(
            entry=entry,
            actor=actor,
            previous_version=previous,
            new_version=entry.version,
            source_reference=entry.source_reference,
            linked_work=entry.work_context_id,
            reason=reason,
            content_snapshot=entry.content,
            metadata_snapshot=_metadata(entry),
        )
    return entry


def review_candidate(
    project: Project,
    entry_id: int,
    decision: str,
    actor: str,
    approval_reference: str = "",
) -> KnowledgeEntry:
    with transaction.atomic():
        entry = entry_for_project(project, entry_id, include_non_active=True, lock=True)
        if entry.status not in {
            KnowledgeEntry.Status.CANDIDATE,
            KnowledgeEntry.Status.IN_REVIEW,
            KnowledgeEntry.Status.REJECTED,
        }:
            raise ValueError("AKB_REVIEW_STATE_INVALID")
        if decision == "REQUEST_REVIEW":
            entry.status = KnowledgeEntry.Status.IN_REVIEW
        elif decision == "REJECT":
            entry.status = KnowledgeEntry.Status.REJECTED
        elif decision == "APPROVE":
            if not approval_reference:
                raise ValueError("APPROVAL_REQUIRED")
            _approval(project, approval_reference, "akb.review_candidate")
            entry.status = KnowledgeEntry.Status.ACTIVE
            entry.approval_reference = approval_reference
            entry.verified_at = timezone.now()
            entry.verification_status = "APPROVED"
        else:
            raise ValueError("AKB_REVIEW_DECISION_INVALID")
        entry.version += 1
        entry.save()
        KnowledgeRevision.objects.create(
            entry=entry,
            actor=actor,
            previous_version=entry.version - 1,
            new_version=entry.version,
            source_reference=entry.source_reference,
            approval_reference=entry.approval_reference,
            linked_work=entry.work_context_id,
            reason=f"REVIEW_{decision}",
            content_snapshot=entry.content,
            metadata_snapshot=_metadata(entry),
        )
    return entry


def entry_for_project(
    project: Project,
    entry_id: int,
    *,
    include_non_active: bool = False,
    lock: bool = False,
) -> KnowledgeEntry:
    query = (
        KnowledgeEntry.objects.select_for_update() if lock else KnowledgeEntry.objects
    )
    query = query.filter(pk=entry_id)
    if not include_non_active:
        query = query.filter(status=KnowledgeEntry.Status.ACTIVE)
    entry = query.first()
    if entry is None or (
        entry.scope == KnowledgeEntry.Scope.PROJECT and entry.project_id != project.pk
    ):
        raise ValueError("AKB_ENTRY_NOT_FOUND")
    if (
        entry.scope == KnowledgeEntry.Scope.PLATFORM
        and entry.platform_context_id != PLATFORM_CONTEXT_ID
    ):
        raise ValueError("AKB_ENTRY_NOT_FOUND")
    return entry


def search(
    project: Project, query: str, filters: dict[str, Any]
) -> list[dict[str, Any]]:
    _context(project, filters.get("work_context_id") or "akb:search")
    entries = (
        KnowledgeEntry.objects.filter(
            status=filters.get("status", KnowledgeEntry.Status.ACTIVE)
        )
        .filter(project__in=[None, project])
        .order_by("entry_key")
    )
    results = []
    needle = query.lower()
    for entry in entries:
        if filters.get("scope") and entry.scope != filters["scope"]:
            continue
        if (
            filters.get("knowledge_type")
            and entry.knowledge_type != filters["knowledge_type"]
        ):
            continue
        if (
            filters.get("verification_status")
            and entry.verification_status != filters["verification_status"]
        ):
            continue
        if (
            filters.get("freshness_status")
            and freshness(entry) != filters["freshness_status"]
        ):
            continue
        role = filters.get("role_context")
        if role and role not in entry.role_context:
            continue
        if needle and needle not in (entry.title + "\n" + entry.content).lower():
            continue
        results.append({**_metadata(entry), "snippet": entry.content[:500]})
    return results[: filters.get("limit", 10)]


def context_package(
    project: Project, work_context_id: str, role_context_id: str
) -> dict[str, Any]:
    context = _context(project, work_context_id)
    entries = list(
        KnowledgeEntry.objects.filter(
            status=KnowledgeEntry.Status.ACTIVE, project__in=[None, project]
        ).order_by("entry_key")
    )
    platform = [
        entry
        for entry in entries
        if entry.scope == KnowledgeEntry.Scope.PLATFORM and entry.is_must_know
    ]
    project_entries = [
        entry
        for entry in entries
        if entry.scope == KnowledgeEntry.Scope.PROJECT and entry.is_must_know
    ]
    task = [entry for entry in entries if entry.work_context_id == work_context_id]
    role = [
        entry
        for entry in entries
        if role_context_id and role_context_id in entry.role_context
    ]
    selected = {
        entry.pk: entry for entry in [*platform, *project_entries, *task, *role]
    }
    ordered = [selected[key] for key in sorted(selected)]
    sources = [
        _metadata(entry)
        | {
            "content": entry.content[:4000],
            "stale_warning": freshness(entry) == "STALE",
        }
        for entry in ordered
    ]
    stable = {**context, "role_context_id": role_context_id, "source_entries": sources}
    package_hash = hashlib.sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        **stable,
        "platform_must_know": [entry.pk for entry in platform],
        "project_must_know": [entry.pk for entry in project_entries],
        "task_entries": [entry.pk for entry in task],
        "role_entries": [entry.pk for entry in role],
        "entry_ids": [entry.pk for entry in ordered],
        "hash": package_hash,
    }

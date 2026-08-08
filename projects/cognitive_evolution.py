"""Governed Cognitive & Behaviour Evolution without Runtime or Reasoning authority."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from projects.models import (
    BehaviourCandidate,
    CognitiveExperience,
    CognitiveGuidancePackage,
    GovernanceApproval,
    Project,
    RuntimeReflectionCandidate,
)

_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class CognitiveGuidance:
    """Structured evidence returned to a future Reasoning consumer, never a decision."""

    package_id: int
    candidate_ids: tuple[int, ...]
    patterns: tuple[dict[str, Any], ...]
    metrics: dict[str, float | int]
    evidence: tuple[dict[str, Any], ...]


def _text(value: object, error: str) -> str:
    if not isinstance(value, str):
        raise ValueError(error)
    normalized = _SPACE.sub(" ", value).strip()
    if not normalized:
        raise ValueError(error)
    return normalized


def _score(reflection: RuntimeReflectionCandidate) -> float:
    """Explainable reflection quality, not a business or execution decision."""
    evidence = len(reflection.evidence_references)
    text_signal = min(len(reflection.reflection_text) / 500, 1.0)
    evidence_signal = min(evidence / 3, 1.0)
    return round(
        (reflection.confidence * 0.6) + (text_signal * 0.2) + (evidence_signal * 0.2), 6
    )


def _fingerprint(value: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _project_for(reflection: RuntimeReflectionCandidate) -> Project:
    return reflection.execution.plan.goal.project


def record_experience(
    project: Project,
    reflection: RuntimeReflectionCandidate,
) -> CognitiveExperience:
    """Record exactly one verified, project-scoped experience from a reflection."""
    if _project_for(reflection).pk != project.pk:
        raise ValueError("COGNITIVE_EXPERIENCE_PROJECT_MISMATCH")
    if reflection.verification_result.get("passed") is not True:
        raise ValueError("COGNITIVE_EXPERIENCE_VERIFICATION_REQUIRED")
    if not reflection.evidence_references:
        raise ValueError("COGNITIVE_EXPERIENCE_EVIDENCE_REQUIRED")
    outcome = {
        "execution_id": reflection.execution_id,
        "goal_id": str(reflection.goal_id),
        "summary": _text(reflection.summary, "COGNITIVE_EXPERIENCE_SUMMARY_REQUIRED"),
        "verification": reflection.verification_result,
    }
    fingerprint = _fingerprint(
        {
            "reflection_id": reflection.pk,
            "schema_version": reflection.schema_version,
            "outcome": outcome,
            "evidence": reflection.evidence_references,
        }
    )
    experience, created = CognitiveExperience.objects.get_or_create(
        reflection_candidate=reflection,
        defaults={
            "project": project,
            "experience_key": f"reflection:{reflection.pk}",
            "fingerprint": fingerprint,
            "outcome": outcome,
            "reflection_quality": _score(reflection),
            "evidence_references": list(reflection.evidence_references),
        },
    )
    if experience.project_id != project.pk or experience.fingerprint != fingerprint:
        raise ValueError("COGNITIVE_EXPERIENCE_CONFLICT")
    if not created and experience.reflection_candidate_id != reflection.pk:
        raise ValueError("COGNITIVE_EXPERIENCE_CONFLICT")
    return experience


def propose_behaviour(
    project: Project,
    experience: CognitiveExperience,
    *,
    strategy_key: str,
    guidance: str,
    applicability: list[str],
    actor: str,
) -> BehaviourCandidate:
    """Create an idempotent, non-active candidate; it cannot self-approve."""
    if experience.project_id != project.pk:
        raise ValueError("BEHAVIOUR_CANDIDATE_PROJECT_MISMATCH")
    strategy = _text(strategy_key, "BEHAVIOUR_CANDIDATE_STRATEGY_REQUIRED")
    instruction = _text(guidance, "BEHAVIOUR_CANDIDATE_GUIDANCE_REQUIRED")
    if not isinstance(applicability, list) or not applicability:
        raise ValueError("BEHAVIOUR_CANDIDATE_APPLICABILITY_REQUIRED")
    tags = sorted(
        {
            _text(tag, "BEHAVIOUR_CANDIDATE_APPLICABILITY_REQUIRED").lower()
            for tag in applicability
        }
    )
    actor_name = _text(actor, "BEHAVIOUR_CANDIDATE_ACTOR_REQUIRED")
    candidate_key = _fingerprint(
        {
            "experience": experience.fingerprint,
            "strategy": strategy,
            "guidance": instruction,
            "applicability": tags,
        }
    )[:48]
    candidate, created = BehaviourCandidate.objects.get_or_create(
        project=project,
        candidate_key=candidate_key,
        defaults={
            "experience": experience,
            "strategy_key": strategy,
            "guidance": instruction,
            "applicability": tags,
            "reflection_quality": experience.reflection_quality,
            "audit_trail": [
                {
                    "event": "CANDIDATE_CREATED",
                    "actor": actor_name,
                    "experience_id": experience.pk,
                    "experience_fingerprint": experience.fingerprint,
                }
            ],
        },
    )
    if candidate.experience_id != experience.pk:
        raise ValueError("BEHAVIOUR_CANDIDATE_CONFLICT")
    if not created and candidate.status == BehaviourCandidate.Status.REJECTED:
        return candidate
    return candidate


def govern_behaviour(
    project: Project,
    candidate: BehaviourCandidate,
    *,
    decision: str,
    actor: str,
    approval_reference: str = "",
) -> BehaviourCandidate:
    """Apply an explicit attributable governance result, never autonomous promotion."""
    if candidate.project_id != project.pk:
        raise ValueError("BEHAVIOUR_GOVERNANCE_PROJECT_MISMATCH")
    if decision not in {"APPROVE", "REJECT"}:
        raise ValueError("BEHAVIOUR_GOVERNANCE_DECISION_INVALID")
    actor_name = _text(actor, "BEHAVIOUR_GOVERNANCE_ACTOR_REQUIRED")
    reference = _text(approval_reference, "BEHAVIOUR_GOVERNANCE_APPROVAL_REQUIRED")
    approval = GovernanceApproval.objects.filter(
        project=project, reference=reference, revoked_at__isnull=True
    ).first()
    if approval is None:
        raise ValueError("BEHAVIOUR_GOVERNANCE_APPROVAL_REQUIRED")
    if approval.approved_action not in {
        "cognitive_evolution.govern_behaviour",
        "ALL_GOVERNED_MUTATIONS",
        "ALL",
    }:
        raise ValueError("BEHAVIOUR_GOVERNANCE_ACTION_NOT_AUTHORIZED")
    with transaction.atomic():
        locked = BehaviourCandidate.objects.select_for_update().get(pk=candidate.pk)
        if locked.status == BehaviourCandidate.Status.CANDIDATE:
            locked.status = (
                BehaviourCandidate.Status.APPROVED
                if decision == "APPROVE"
                else BehaviourCandidate.Status.REJECTED
            )
            locked.approval_reference = reference
            locked.audit_trail = [
                *locked.audit_trail,
                {
                    "event": locked.status,
                    "actor": actor_name,
                    "approval_reference": reference,
                },
            ]
            locked.save(
                update_fields=[
                    "status",
                    "approval_reference",
                    "audit_trail",
                    "updated_at",
                ]
            )
        elif (
            locked.status == BehaviourCandidate.Status.APPROVED
            and decision != "APPROVE"
        ):
            raise ValueError("BEHAVIOUR_GOVERNANCE_TERMINAL_CONFLICT")
        elif (
            locked.status == BehaviourCandidate.Status.REJECTED and decision != "REJECT"
        ):
            raise ValueError("BEHAVIOUR_GOVERNANCE_TERMINAL_CONFLICT")
        elif locked.approval_reference != reference:
            raise ValueError("BEHAVIOUR_GOVERNANCE_TERMINAL_CONFLICT")
    return locked


def cognitive_metrics(project: Project) -> dict[str, float | int]:
    """Return transparent, project-isolated MVP evolution measurements."""
    experiences = CognitiveExperience.objects.filter(project=project)
    candidates = BehaviourCandidate.objects.filter(project=project)
    total = experiences.count()
    average = (
        sum(experience.reflection_quality for experience in experiences) / total
        if total
        else 0.0
    )
    return {
        "experience_count": total,
        "candidate_count": candidates.count(),
        "approved_pattern_count": candidates.filter(
            status=BehaviourCandidate.Status.APPROVED
        ).count(),
        "rejected_candidate_count": candidates.filter(
            status=BehaviourCandidate.Status.REJECTED
        ).count(),
        "average_reflection_quality": round(average, 6),
    }


def build_guidance(project: Project, *, query: str = "") -> CognitiveGuidance:
    """Package approved patterns without invoking Reasoning or Runtime."""
    normalized_query = _SPACE.sub(" ", query).strip()
    candidates = list(
        BehaviourCandidate.objects.filter(
            project=project, status=BehaviourCandidate.Status.APPROVED
        )
        .select_related("experience")
        .order_by("candidate_key")
    )
    # This package is deliberately a complete, approved project view.  Semantic
    # retrieval remains the sole owner of relevance filtering and ranking.
    metrics = cognitive_metrics(project)
    evidence = [
        {
            "candidate_id": candidate.pk,
            "experience_id": candidate.experience_id,
            "experience_fingerprint": candidate.experience.fingerprint,
            "approval_reference": candidate.approval_reference,
            "reflection_quality": candidate.reflection_quality,
        }
        for candidate in candidates
    ]
    patterns = [
        {
            "candidate_id": candidate.pk,
            "strategy_key": candidate.strategy_key,
            "guidance": candidate.guidance,
            "applicability": candidate.applicability,
        }
        for candidate in candidates
    ]
    package_hash = _fingerprint(
        {
            "project": project.pk,
            "query": normalized_query,
            "candidate_ids": [candidate.pk for candidate in candidates],
            "patterns": patterns,
            "metrics": metrics,
        }
    )
    package, _ = CognitiveGuidancePackage.objects.get_or_create(
        package_hash=package_hash,
        defaults={
            "project": project,
            "query": normalized_query,
            "candidate_ids": [candidate.pk for candidate in candidates],
            "patterns": patterns,
            "metrics": metrics,
            "evidence": evidence,
        },
    )
    if package.project_id != project.pk:
        raise ValueError("COGNITIVE_GUIDANCE_PROJECT_CONFLICT")
    return CognitiveGuidance(
        package_id=package.pk,
        candidate_ids=tuple(package.candidate_ids),
        patterns=tuple(package.patterns),
        metrics=package.metrics,
        evidence=tuple(package.evidence),
    )

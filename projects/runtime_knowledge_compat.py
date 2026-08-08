"""Deprecated compatibility bridge for pre-Sprint-05 Runtime knowledge writes.

New canonical executions must only create RuntimeKnowledgeCandidate records.  This
adapter preserves the legacy Factory Runtime behaviour until Sprint 06 owns
knowledge promotion and AKB mutation.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .knowledge import create_or_upsert_candidate
from .models import OrkiExecution, OrkiKnowledgeIntegration, OrkiReflection


def integrate_legacy_reflection(
    execution: OrkiExecution,
    reflection: OrkiReflection,
    result: Mapping[str, Any],
    actor: str,
    emit_event: Callable[..., object],
) -> OrkiKnowledgeIntegration:
    """Maintain legacy AKB-candidate creation behind one isolated adapter."""
    evidence = list(reflection.evidence_references)
    candidate = result.get("knowledge_candidate")
    if not isinstance(candidate, Mapping):
        integration = OrkiKnowledgeIntegration.objects.create(
            reflection=reflection,
            status=OrkiKnowledgeIntegration.Status.NOT_REQUIRED,
            evidence_references=evidence,
        )
        emit_event(
            execution,
            "knowledge.rejected",
            actor=actor,
            payload={"reason": "not_required"},
            evidence_references=evidence,
        )
        return integration
    required = {"entry_key", "knowledge_type", "title", "content"}
    if not required.issubset(candidate) or not evidence:
        integration = OrkiKnowledgeIntegration.objects.create(
            reflection=reflection,
            status=OrkiKnowledgeIntegration.Status.REJECTED,
            evidence_references=evidence,
        )
        emit_event(
            execution,
            "knowledge.rejected",
            actor=actor,
            payload={"reason": "candidate_invalid"},
            evidence_references=evidence,
        )
        return integration
    entry = create_or_upsert_candidate(
        execution.plan.goal.project,
        {
            **dict(candidate),
            "scope": "PROJECT",
            "source_type": "RUNTIME_REFLECTION",
            "source_reference": f"runtime-execution:{execution.token}",
            "evidence_references": evidence,
            "work_context_id": f"runtime:{execution.token}",
        },
        actor,
    )
    integration = OrkiKnowledgeIntegration.objects.create(
        reflection=reflection,
        knowledge_entry=entry,
        status=OrkiKnowledgeIntegration.Status.ACCEPTED_FOR_REVIEW,
        evidence_references=evidence,
        embedding_reference=f"pending-governance:{entry.entry_key}",
    )
    emit_event(
        execution,
        "knowledge.candidate.created",
        actor=actor,
        payload={"knowledge_entry_id": entry.pk},
        evidence_references=evidence,
    )
    emit_event(
        execution,
        "knowledge.accepted",
        actor=actor,
        payload={"knowledge_entry_id": entry.pk, "status": entry.status},
        evidence_references=evidence,
    )
    emit_event(
        execution,
        "knowledge.integrated",
        actor=actor,
        payload={"integration_id": integration.pk},
        evidence_references=evidence,
    )
    return integration

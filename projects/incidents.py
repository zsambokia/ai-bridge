"""Provider-neutral durable incident and deterministic ownership services."""

from __future__ import annotations

from typing import Any

from django.db import IntegrityError, transaction

from .engineering_memory import ingest_lifecycle_event
from .knowledge import create_or_upsert_candidate
from .models import (
    FailureIncident,
    IncidentEvidence,
    KnowledgeEntry,
    OrchestrationSession,
    OwnershipAssessment,
    Project,
    RepositoryDependency,
)
from .orchestration_context import bind, for_incident
from .orchestrator import PolicyDecision

_SECRET_MARKERS = ("openai_api_key", "authorization:", "private_key", "password=")


def record_incident(
    project: Project,
    summary: str,
    idempotency_key: str,
    *,
    session: OrchestrationSession | None = None,
    causal_classification: str = "",
) -> FailureIncident:
    """Create one durable incident per key; retries never duplicate it."""
    if not summary or not idempotency_key:
        raise ValueError("INCIDENT_INPUT_REQUIRED")
    bind(project, f"incident-request:{idempotency_key}")
    if session is not None and session.project_id != project.pk:
        raise ValueError("CONTEXT_SESSION_PROJECT_MISMATCH")
    try:
        existing = FailureIncident.objects.get(idempotency_key=idempotency_key)
        if existing.project_id != project.pk:
            raise ValueError("INCIDENT_IDEMPOTENCY_CONFLICT")
        return existing
    except FailureIncident.DoesNotExist:
        pass
    correlation_id = session.correlation_id if session else idempotency_key
    try:
        with transaction.atomic():
            return FailureIncident.objects.create(
                project=project,
                session=session,
                idempotency_key=idempotency_key,
                correlation_id=correlation_id[:128],
                summary=summary[:1000],
                causal_classification=causal_classification[:64],
                timeline=[
                    {"event": "RECORDED", "correlation_id": correlation_id[:128]}
                ],
            )
    except IntegrityError:
        existing = FailureIncident.objects.get(idempotency_key=idempotency_key)
        if existing.project_id != project.pk:
            raise ValueError("INCIDENT_IDEMPOTENCY_CONFLICT")
        return existing


def add_evidence(
    incident: FailureIncident,
    reference: str,
    kind: str,
    summary: str,
    provenance: str,
) -> IncidentEvidence:
    """Store an evidence reference only after bounded, secret-safe validation."""
    for_incident(incident)
    values = (reference, kind, summary, provenance)
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise ValueError("INCIDENT_EVIDENCE_INVALID")
    if any(marker in summary.lower() for marker in _SECRET_MARKERS):
        raise ValueError("INCIDENT_EVIDENCE_SECRET_REJECTED")
    if (
        len(reference) > 255
        or len(kind) > 64
        or len(summary) > 1000
        or len(provenance) > 255
    ):
        raise ValueError("INCIDENT_EVIDENCE_BOUNDS_EXCEEDED")
    evidence, _ = IncidentEvidence.objects.get_or_create(
        incident=incident,
        reference=reference,
        defaults={"kind": kind, "summary": summary, "provenance": provenance},
    )
    return evidence


def assess_ownership(
    incident: FailureIncident, candidates: list[dict[str, Any]]
) -> OwnershipAssessment:
    """Rank only registered, evidence-backed candidates; ambiguity fails closed."""
    for_incident(incident)
    if not isinstance(candidates, list) or len(candidates) > 10:
        raise ValueError("OWNERSHIP_CANDIDATES_INVALID")
    evidence_refs = set(incident.evidence.values_list("reference", flat=True))
    normalized: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("OWNERSHIP_CANDIDATES_INVALID")
        repository = candidate.get("repository")
        component = candidate.get("component", "")
        confidence = candidate.get("confidence")
        refs = candidate.get("evidence_references")
        if (
            not isinstance(repository, str)
            or not isinstance(component, str)
            or not isinstance(confidence, (int, float))
            or not 0 <= confidence <= 1
            or not isinstance(refs, list)
            or not refs
            or not all(isinstance(ref, str) and ref in evidence_refs for ref in refs)
        ):
            raise ValueError("OWNERSHIP_CANDIDATES_INVALID")
        try:
            project = Project.objects.get(repository_full_name=repository)
        except Project.DoesNotExist:
            continue
        normalized.append(
            {
                "repository": project.repository_full_name,
                "project_id": project.project_id,
                "component": component[:255],
                "confidence": round(float(confidence), 4),
                "evidence_references": sorted(set(refs)),
            }
        )
    normalized.sort(key=lambda item: (-item["confidence"], item["project_id"]))
    selected = normalized[0] if normalized else None
    ambiguous = bool(
        selected
        and len(normalized) > 1
        and normalized[1]["confidence"] == selected["confidence"]
    )
    selected_project = (
        Project.objects.get(project_id=selected["project_id"])
        if selected and selected["confidence"] >= 0.8 and not ambiguous
        else None
    )
    if selected_project is None:
        decision, reason = (
            PolicyDecision.REQUIRE_MORE_EVIDENCE,
            "Ownership is unknown, ambiguous, or below the 0.80 confidence threshold.",
        )
    elif (
        selected_project != incident.project
        and not RepositoryDependency.objects.filter(
            project=incident.project,
            depends_on=selected_project,
            autonomous_remediation_approved=True,
        ).exists()
    ):
        decision, reason = (
            PolicyDecision.DENY,
            "Cross-project ownership lacks an approved dependency relationship.",
        )
    else:
        decision, reason = (
            PolicyDecision.ALLOW,
            "Registered repository ownership is evidence-backed; "
            "no execution is authorized.",
        )
    assessment, _ = OwnershipAssessment.objects.update_or_create(
        incident=incident,
        defaults={
            "selected_project": selected_project,
            "selected_component": (
                selected["component"] if selected_project and selected else ""
            ),
            "confidence": selected["confidence"] if selected else 0,
            "policy_decision": decision,
            "reason": reason,
            "candidates": normalized,
        },
    )
    incident.status = FailureIncident.Status.ASSESSED
    incident.timeline = [
        *incident.timeline,
        {"event": "OWNERSHIP_ASSESSED", "policy": decision},
    ][-20:]
    incident.save(update_fields=["status", "timeline", "updated_at"])
    return assessment


def close_incident(incident: FailureIncident, actor: str = "system") -> KnowledgeEntry:
    """Close an incident and record its bounded lesson as a reviewable AKB candidate.

    This intentionally does not activate knowledge: a separately approved AKB
    review is required before an Orchestrator can consume the lesson.
    """
    for_incident(incident)
    evidence = list(incident.evidence.values_list("reference", flat=True))[:20]
    entry = create_or_upsert_candidate(
        incident.project,
        {
            "entry_key": f"incident:{incident.token}",
            "scope": "PROJECT",
            "knowledge_type": "INCIDENT_LESSON",
            "title": f"Incident lesson: {incident.summary[:180]}",
            "content": (
                f"Incident: {incident.summary}\n"
                "Causal classification: "
                f"{incident.causal_classification or 'UNCLASSIFIED'}\n"
                "Status: closed; lesson requires review before activation."
            ),
            "source_type": "INCIDENT",
            "source_reference": f"incident:{incident.token}",
            "evidence_references": evidence,
            "work_context_id": f"incident:{incident.token}",
            "role_context": ["ENGINEERING"],
            "knowledge_owner_role": "ENGINEERING",
        },
        actor,
        upsert=True,
    )
    incident.status = FailureIncident.Status.CLOSED
    incident.timeline = [*incident.timeline, {"event": "CLOSED", "actor": actor}][-20:]
    incident.save(update_fields=["status", "timeline", "updated_at"])
    ingest_lifecycle_event(
        incident.project,
        event_type="INCIDENT_RESOLVED",
        event_key=str(incident.token),
        source_reference=f"incident:{incident.token}",
        evidence_references=evidence,
        attributes={"causal_classification": incident.causal_classification},
        actor=actor,
    )
    return entry

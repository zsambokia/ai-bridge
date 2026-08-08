"""Canonical Cognitive State services for Orki Sprint ORKI-001."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.db import transaction

from .models import CognitiveState, CognitiveStateEntry, Project


def state_for(project: Project) -> CognitiveState:
    """Return the sole project-owned state container without creating authority."""
    return CognitiveState.objects.get_or_create(project=project)[0]


def record_entry(
    project: Project,
    *,
    kind: str,
    content: Mapping[str, object],
    provenance: Mapping[str, object],
    confidence: float | None = None,
    corrects: CognitiveStateEntry | None = None,
    supersedes: CognitiveStateEntry | None = None,
) -> CognitiveStateEntry:
    """Record one attributable state update and close only same-project entries."""
    if kind not in CognitiveStateEntry.Kind.values:
        raise ValueError("Unsupported Cognitive State entry kind.")
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError("Confidence must be between 0 and 1.")
    state = state_for(project)
    for related in (corrects, supersedes):
        if related is not None and related.state_id != state.id:
            raise ValueError("Cognitive State entries cannot cross project boundaries.")
    with transaction.atomic():
        entry = CognitiveStateEntry.objects.create(
            state=state,
            kind=kind,
            content=dict(content),
            provenance=dict(provenance),
            confidence=confidence,
            corrects=corrects,
            supersedes=supersedes,
        )
        if corrects is not None:
            corrects.status = CognitiveStateEntry.Status.CORRECTED
            corrects.save(update_fields=["status", "updated_at"])
        if supersedes is not None:
            supersedes.status = CognitiveStateEntry.Status.SUPERSEDED
            supersedes.save(update_fields=["status", "updated_at"])
    return entry


def projection(project: Project) -> dict[str, list[dict[str, Any]]]:
    """Return stable, type-separated active state suitable for any interface."""
    state = state_for(project)
    result: dict[str, list[dict[str, Any]]] = {
        kind: [] for kind in CognitiveStateEntry.Kind.values
    }
    entries = state.entries.filter(status=CognitiveStateEntry.Status.ACTIVE)
    for entry in entries:
        result[entry.kind].append(
            {
                "id": entry.pk,
                "content": entry.content,
                "provenance": entry.provenance,
                "confidence": entry.confidence,
                "created_at": entry.created_at.isoformat(),
            }
        )
    return result


def record_snapshot(
    project: Project,
    *,
    kind: str,
    attribute: str,
    value: object,
    provenance: Mapping[str, object],
    confidence: float | None = None,
) -> CognitiveStateEntry | None:
    """Evolve one named state attribute without retaining duplicate snapshots."""
    state = state_for(project)
    content = {"attribute": attribute, "value": value}
    previous = (
        state.entries.filter(
            kind=kind,
            status=CognitiveStateEntry.Status.ACTIVE,
            content__attribute=attribute,
        )
        .order_by("-created_at", "-pk")
        .first()
    )
    if (
        previous is not None
        and previous.content == content
        and previous.confidence == confidence
    ):
        return None
    return record_entry(
        project,
        kind=kind,
        content=content,
        provenance=provenance,
        confidence=confidence,
        supersedes=previous,
    )


def record_factory_mission_state(
    project: Project,
    mission: Any,
    *,
    understanding: Mapping[str, object],
    provenance: Mapping[str, object],
) -> list[CognitiveStateEntry]:
    """Project structured conversation understanding into canonical state.

    ``FactoryChatMessage`` remains the transcript.  This service writes only
    structured, attributable knowledge and a non-reversible source reference.
    It deliberately accepts the provider's declared fields, rather than
    inferring state from arbitrary conversation text.
    """
    recorded: list[CognitiveStateEntry] = []

    def snapshot(
        kind: str, attribute: str, value: object, confidence: float | None = None
    ) -> None:
        entry = record_snapshot(
            project,
            kind=kind,
            attribute=attribute,
            value=value,
            provenance=provenance,
            confidence=confidence,
        )
        if entry is not None:
            recorded.append(entry)

    text_fields = (
        (CognitiveStateEntry.Kind.MISSION, "objective"),
        (CognitiveStateEntry.Kind.MISSION, "primary_workflow"),
        (CognitiveStateEntry.Kind.CONSTRAINT, "mvp_boundary"),
        (CognitiveStateEntry.Kind.CONSTRAINT, "persistence_requirements"),
    )
    for kind, attribute in text_fields:
        if attribute in understanding and getattr(mission, attribute):
            snapshot(kind, attribute, getattr(mission, attribute))

    list_fields = (
        (CognitiveStateEntry.Kind.BUSINESS_CONTEXT, "target_users"),
        (CognitiveStateEntry.Kind.BUSINESS_CONTEXT, "required_inputs"),
        (CognitiveStateEntry.Kind.GOAL, "required_outputs"),
        (CognitiveStateEntry.Kind.CONSTRAINT, "integrations"),
        (CognitiveStateEntry.Kind.CONSTRAINT, "cost_impacting_dependencies"),
        (CognitiveStateEntry.Kind.RISK, "risks"),
        (CognitiveStateEntry.Kind.ASSUMPTION, "assumptions"),
        (CognitiveStateEntry.Kind.OPEN_DECISION, "unresolved_decisions"),
    )
    for kind, attribute in list_fields:
        if attribute in understanding:
            snapshot(kind, attribute, getattr(mission, attribute))

    if "recommendations" in understanding:
        snapshot(
            CognitiveStateEntry.Kind.RECOMMENDATION,
            "recommendations",
            mission.recommendations,
            mission.recommendation_confidence,
        )

    # Evidence establishes source and time without copying Product Owner text.
    recorded.append(
        record_entry(
            project,
            kind=CognitiveStateEntry.Kind.EVIDENCE,
            content={
                "evidence_type": "PRODUCT_OWNER_CONVERSATION_STRUCTURED_UPDATE",
                "source_message_id": provenance["conversation_message_id"],
                "message_sha256": provenance["conversation_message_sha256"],
            },
            provenance=provenance,
        )
    )
    return recorded

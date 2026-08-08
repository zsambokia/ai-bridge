"""Canonical, evidence-bound Mission Understanding for ORKI-002.

The service deliberately accepts a structured observation rather than a chat
transcript.  Providers may propose the observation, but Orki owns validation,
normalisation, project isolation, lifecycle evolution and explainability.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .cognitive_state import record_entry, record_snapshot
from .models import CognitiveState, CognitiveStateEntry, Project


def _text(value: object, *, field: str, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError(f"MISSION_UNDERSTANDING_{field.upper()}_REQUIRED")
        return ""
    if not isinstance(value, str):
        raise ValueError(f"MISSION_UNDERSTANDING_{field.upper()}_INVALID")
    normalized = " ".join(value.split()).strip()
    if required and not normalized:
        raise ValueError(f"MISSION_UNDERSTANDING_{field.upper()}_REQUIRED")
    return normalized[:2000]


def _strings(value: object, *, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"MISSION_UNDERSTANDING_{field.upper()}_INVALID")
    # A canonical key makes semantically identical structured observations
    # stable across equivalent Product Owner formulations.
    unique: dict[str, str] = {}
    for item in value:
        text = _text(item, field=field)
        if text:
            canonical = text.casefold()
            unique.setdefault(canonical, canonical)
    return [unique[key] for key in sorted(unique)][:30]


def _confidence(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("MISSION_UNDERSTANDING_INFERENCE_CONFIDENCE_INVALID")
    confidence = float(value)
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("MISSION_UNDERSTANDING_INFERENCE_CONFIDENCE_INVALID")
    return confidence


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("MISSION_UNDERSTANDING_SOURCE_REQUIRED")
    # Store an allow-listed source reference only.  Raw transcript content and
    # arbitrary provider metadata can never enter Cognitive State through this
    # boundary.
    return {
        key: provenance[key]
        for key in (
            "source_type",
            "conversation_message_id",
            "conversation_message_sha256",
            "correlation_id",
            "provider_id",
            "model",
        )
        if key in provenance
    }


def mission_projection(project: Project) -> dict[str, Any]:
    """Return only the active, explainable proposed Mission State."""
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist:
        return {}
    entries = state.entries.filter(
        status=CognitiveStateEntry.Status.ACTIVE,
        kind__in=(
            CognitiveStateEntry.Kind.FACT,
            CognitiveStateEntry.Kind.INFERENCE,
            CognitiveStateEntry.Kind.ASSUMPTION,
            CognitiveStateEntry.Kind.OPEN_DECISION,
            CognitiveStateEntry.Kind.MISSION,
        ),
    ).order_by("created_at", "pk")
    result: dict[str, Any] = {}
    for entry in entries:
        attribute = entry.content.get("attribute")
        if isinstance(attribute, str):
            result[attribute] = {
                "kind": entry.kind,
                "value": entry.content.get("value"),
                "confidence": entry.confidence,
                "provenance": entry.provenance,
            }
    return result


def record_mission_understanding(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, Any]:
    """Validate and evolve an attributable proposed Mission State.

    This creates neither a recommendation, an accepted decision nor a plan.
    """
    source = _source(provenance)
    stated_intent = _text(
        observation.get("stated_intent"), field="stated_intent", required=True
    )
    business_goal = _text(
        observation.get("inferred_business_goal"),
        field="inferred_business_goal",
        required=True,
    )
    confidence = _confidence(observation.get("inference_confidence"))
    constraints = _strings(
        observation.get("stated_constraints"), field="stated_constraints"
    )
    solutions = _strings(
        observation.get("solution_proposals"), field="solution_proposals"
    )
    technology = _strings(
        observation.get("technology_preferences"), field="technology_preferences"
    )
    assumptions = _strings(
        observation.get("safe_assumptions"), field="safe_assumptions"
    )
    unknowns = _strings(observation.get("material_unknowns"), field="material_unknowns")
    question = observation.get("question")
    if question is not None and not isinstance(question, Mapping):
        raise ValueError("MISSION_UNDERSTANDING_QUESTION_INVALID")
    if question is None:
        question_value: dict[str, str] | None = None
    else:
        if not unknowns:
            raise ValueError("MISSION_UNDERSTANDING_QUESTION_NOT_MATERIAL")
        question_value = {
            "text": _text(question.get("text"), field="question_text", required=True),
            "purpose": _text(
                question.get("purpose"), field="question_purpose", required=True
            ),
            "material_effect": _text(
                question.get("material_effect"),
                field="question_material_effect",
                required=True,
            ),
        }

    snapshots = (
        (CognitiveStateEntry.Kind.FACT, "stated_intent", stated_intent, None),
        (CognitiveStateEntry.Kind.FACT, "stated_constraints", constraints, None),
        (CognitiveStateEntry.Kind.FACT, "solution_proposals", solutions, None),
        (CognitiveStateEntry.Kind.FACT, "technology_preferences", technology, None),
        (
            CognitiveStateEntry.Kind.INFERENCE,
            "inferred_business_goal",
            business_goal,
            confidence,
        ),
        (CognitiveStateEntry.Kind.ASSUMPTION, "safe_assumptions", assumptions, None),
        (CognitiveStateEntry.Kind.OPEN_DECISION, "material_unknowns", unknowns, None),
        (
            CognitiveStateEntry.Kind.OPEN_DECISION,
            "mission_question",
            question_value,
            None,
        ),
    )
    for kind, attribute, value, item_confidence in snapshots:
        record_snapshot(
            project,
            kind=kind,
            attribute=attribute,
            value=value,
            confidence=item_confidence,
            provenance=source,
        )
    proposed = {
        "state": "PROPOSED",
        "stated_intent": stated_intent,
        "inferred_business_goal": business_goal,
        "stated_constraints": constraints,
        "safe_assumptions": assumptions,
        "material_unknowns": unknowns,
    }
    record_snapshot(
        project,
        kind=CognitiveStateEntry.Kind.MISSION,
        attribute="proposed_mission",
        value=proposed,
        confidence=confidence,
        provenance=source,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "evidence_type": "MISSION_UNDERSTANDING_OBSERVATION",
            "source_message_id": source["conversation_message_id"],
            "message_sha256": source["conversation_message_sha256"],
        },
        provenance=source,
    )
    return mission_projection(project)

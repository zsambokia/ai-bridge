"""Canonical, evidence-bound Recommendation Intelligence for ORKI-003.

Providers may propose structured recommendation observations.  This module
alone validates their state references and evolves project-owned Cognitive
State.  It deliberately creates no decision, plan, governance, or execution
authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from .cognitive_state import record_entry, record_snapshot
from .models import CognitiveState, CognitiveStateEntry, Project

_KEY = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_PRIORITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
_EVIDENCE_KINDS = {
    CognitiveStateEntry.Kind.MISSION,
    CognitiveStateEntry.Kind.BUSINESS_CONTEXT,
    CognitiveStateEntry.Kind.GOAL,
    CognitiveStateEntry.Kind.CONSTRAINT,
    CognitiveStateEntry.Kind.FACT,
    CognitiveStateEntry.Kind.INFERENCE,
    CognitiveStateEntry.Kind.EVIDENCE,
    CognitiveStateEntry.Kind.RISK,
    CognitiveStateEntry.Kind.OPPORTUNITY,
}


def _text(value: object, *, field: str, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError(f"RECOMMENDATION_{field.upper()}_REQUIRED")
        return ""
    if not isinstance(value, str):
        raise ValueError(f"RECOMMENDATION_{field.upper()}_INVALID")
    result = " ".join(value.split()).strip()
    if required and not result:
        raise ValueError(f"RECOMMENDATION_{field.upper()}_REQUIRED")
    return result[:2000]


def _strings(value: object, *, field: str, required: bool = False) -> list[str]:
    if value is None:
        if required:
            raise ValueError(f"RECOMMENDATION_{field.upper()}_REQUIRED")
        return []
    if not isinstance(value, list):
        raise ValueError(f"RECOMMENDATION_{field.upper()}_INVALID")
    values = [_text(item, field=field, required=True) for item in value]
    unique = {item.casefold(): item for item in values}
    result = [unique[key] for key in sorted(unique)]
    if required and not result:
        raise ValueError(f"RECOMMENDATION_{field.upper()}_REQUIRED")
    return result[:30]


def _confidence(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("RECOMMENDATION_CONFIDENCE_INVALID")
    result = float(value)
    if not 0.0 <= result <= 1.0:
        raise ValueError("RECOMMENDATION_CONFIDENCE_INVALID")
    return result


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("RECOMMENDATION_SOURCE_REQUIRED")
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


def _items(
    value: object, *, field: str, required_keys: tuple[str, ...]
) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"RECOMMENDATION_{field.upper()}_INVALID")
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"RECOMMENDATION_{field.upper()}_INVALID")
        result.append(
            {
                key: _text(item.get(key), field=f"{field}_{key}", required=True)
                for key in required_keys
            }
        )
    if len(result) < 2:
        raise ValueError(f"RECOMMENDATION_{field.upper()}_INSUFFICIENT")
    return result[:10]


def _references(
    project: Project,
    *,
    attributes: list[str],
    allowed_kinds: set[str],
    error: str,
) -> list[CognitiveStateEntry]:
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError(error) from exc
    resolved: list[CognitiveStateEntry] = []
    for attribute in attributes:
        entry = (
            state.entries.filter(
                status=CognitiveStateEntry.Status.ACTIVE,
                content__attribute=attribute,
            )
            .order_by("-created_at", "-pk")
            .first()
        )
        if entry is None or entry.kind not in allowed_kinds:
            raise ValueError(error)
        resolved.append(entry)
    return resolved


def _entry_view(entry: CognitiveStateEntry) -> dict[str, object]:
    return {
        "id": entry.pk,
        "kind": entry.kind,
        "attribute": entry.content.get("attribute"),
        "value": entry.content.get("value"),
        "confidence": entry.confidence,
        "status": entry.status,
        "provenance": entry.provenance,
    }


def recommendation_projection(project: Project) -> dict[str, dict[str, object]]:
    """Return active recommendations with their durable explainability data."""
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist:
        return {}
    active = state.entries.filter(status=CognitiveStateEntry.Status.ACTIVE)
    alternatives = {
        entry.content.get("attribute"): entry
        for entry in active.filter(kind=CognitiveStateEntry.Kind.ALTERNATIVE)
        if isinstance(entry.content.get("attribute"), str)
    }
    trade_offs = {
        entry.content.get("attribute"): entry
        for entry in active.filter(kind=CognitiveStateEntry.Kind.TRADE_OFF)
        if isinstance(entry.content.get("attribute"), str)
    }
    result: dict[str, dict[str, object]] = {}
    for entry in active.filter(kind=CognitiveStateEntry.Kind.RECOMMENDATION):
        attribute = entry.content.get("attribute")
        value = entry.content.get("value")
        if not isinstance(attribute, str) or not isinstance(value, Mapping):
            continue
        source_ids = [
            *value.get("evidence_entry_ids", []),
            *value.get("assumption_entry_ids", []),
        ]
        sources = {
            source.pk: source
            for source in state.entries.filter(pk__in=source_ids).order_by("pk")
        }
        result[attribute] = {
            "recommendation": _entry_view(entry),
            "evidence": [
                _entry_view(sources[item])
                for item in value.get("evidence_entry_ids", [])
                if item in sources
            ],
            "assumptions": [
                _entry_view(sources[item])
                for item in value.get("assumption_entry_ids", [])
                if item in sources
            ],
            "alternatives": _entry_view(alternatives[attribute])
            if attribute in alternatives
            else None,
            "trade_offs": _entry_view(trade_offs[attribute])
            if attribute in trade_offs
            else None,
        }
    return result


def record_recommendation(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, dict[str, object]]:
    """Validate and evolve one evidence-based recommendation without authority."""
    source = _source(provenance)
    key = _text(
        observation.get("recommendation_key"), field="recommendation_key", required=True
    ).casefold()
    if not _KEY.fullmatch(key):
        raise ValueError("RECOMMENDATION_KEY_INVALID")
    priority = _text(
        observation.get("priority"), field="priority", required=True
    ).upper()
    if priority not in _PRIORITIES:
        raise ValueError("RECOMMENDATION_PRIORITY_INVALID")
    evidence_attributes = _strings(
        observation.get("evidence_attributes"),
        field="evidence_attributes",
        required=True,
    )
    assumption_attributes = _strings(
        observation.get("assumption_attributes"), field="assumption_attributes"
    )
    evidence = _references(
        project,
        attributes=evidence_attributes,
        allowed_kinds=_EVIDENCE_KINDS,
        error="RECOMMENDATION_EVIDENCE_UNAVAILABLE",
    )
    assumptions = _references(
        project,
        attributes=assumption_attributes,
        allowed_kinds={CognitiveStateEntry.Kind.ASSUMPTION},
        error="RECOMMENDATION_ASSUMPTION_UNAVAILABLE",
    )
    requires_decision = observation.get("requires_product_owner_decision")
    if not isinstance(requires_decision, bool):
        raise ValueError("RECOMMENDATION_DECISION_BOUNDARY_INVALID")
    attribute = f"recommendation:{key}"
    recommendation = {
        "key": key,
        "priority": priority,
        "recommendation": _text(
            observation.get("recommendation"), field="recommendation", required=True
        ),
        "rationale": _text(
            observation.get("rationale"), field="rationale", required=True
        ),
        "business_impact": _text(
            observation.get("business_impact"), field="business_impact", required=True
        ),
        "dependencies": _strings(observation.get("dependencies"), field="dependencies"),
        "next_safe_action": _text(
            observation.get("next_safe_action"), field="next_safe_action", required=True
        ),
        "requires_product_owner_decision": requires_decision,
        "evidence_entry_ids": [entry.pk for entry in evidence],
        "assumption_entry_ids": [entry.pk for entry in assumptions],
    }
    alternatives = _items(
        observation.get("alternatives"),
        field="alternatives",
        required_keys=("option", "summary"),
    )
    trade_offs = _items(
        observation.get("trade_offs"),
        field="trade_offs",
        required_keys=("option", "benefit", "cost"),
    )
    confidence = _confidence(observation.get("confidence"))
    record_snapshot(
        project,
        kind=CognitiveStateEntry.Kind.RECOMMENDATION,
        attribute=attribute,
        value=recommendation,
        confidence=confidence,
        provenance=source,
    )
    record_snapshot(
        project,
        kind=CognitiveStateEntry.Kind.ALTERNATIVE,
        attribute=attribute,
        value=alternatives,
        confidence=confidence,
        provenance=source,
    )
    record_snapshot(
        project,
        kind=CognitiveStateEntry.Kind.TRADE_OFF,
        attribute=attribute,
        value=trade_offs,
        confidence=confidence,
        provenance=source,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "evidence_type": "RECOMMENDATION_ENGINE_OBSERVATION",
            "source_message_id": source["conversation_message_id"],
            "message_sha256": source["conversation_message_sha256"],
            "recommendation_attribute": attribute,
            "evidence_entry_ids": [entry.pk for entry in evidence],
            "assumption_entry_ids": [entry.pk for entry in assumptions],
        },
        provenance=source,
    )
    return recommendation_projection(project)

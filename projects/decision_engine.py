"""Canonical, authority-bound Decision Intelligence for ORKI-004.

Providers may propose a material open decision from recommendation state. Only
an explicit, attributable Product Owner confirmation can accept an option.
Neither operation creates a plan, governance approval, or execution authority.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .cognitive_state import record_entry
from .models import CognitiveState, CognitiveStateEntry, Project
from .recommendation_engine import recommendation_projection

_KEY = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _text(value: object, *, field: str, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError(f"DECISION_{field.upper()}_REQUIRED")
        return ""
    if not isinstance(value, str):
        raise ValueError(f"DECISION_{field.upper()}_INVALID")
    result = " ".join(value.split()).strip()
    if required and not result:
        raise ValueError(f"DECISION_{field.upper()}_REQUIRED")
    return result[:2000]


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("DECISION_SOURCE_REQUIRED")
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


def _product_owner_source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "actor_type", "actor_id", "confirmation_reference"}
    if not required.issubset(provenance):
        raise ValueError("DECISION_ACCEPTANCE_SOURCE_REQUIRED")
    if provenance["source_type"] != "PRODUCT_OWNER_CONFIRMATION":
        raise ValueError("DECISION_ACCEPTANCE_SOURCE_INVALID")
    if provenance["actor_type"] != "PRODUCT_OWNER":
        raise ValueError("DECISION_ACCEPTANCE_ACTOR_INVALID")
    actor_id = _text(provenance["actor_id"], field="actor_id", required=True)
    reference = _text(
        provenance["confirmation_reference"],
        field="confirmation_reference",
        required=True,
    )
    return {
        "source_type": "PRODUCT_OWNER_CONFIRMATION",
        "actor_type": "PRODUCT_OWNER",
        "actor_id": actor_id,
        "confirmation_reference": reference,
    }


def _options(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or len(value) < 2:
        raise ValueError("DECISION_OPTIONS_INSUFFICIENT")
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("DECISION_OPTIONS_INVALID")
        option = _text(item.get("option"), field="option", required=True)
        summary = _text(item.get("summary"), field="option_summary", required=True)
        if any(
            existing["option"].casefold() == option.casefold() for existing in result
        ):
            raise ValueError("DECISION_OPTIONS_INVALID")
        result.append({"option": option, "summary": summary})
    return result[:10]


def _entry_view(entry: CognitiveStateEntry) -> dict[str, Any]:
    return {
        "id": entry.pk,
        "kind": entry.kind,
        "attribute": entry.content.get("attribute"),
        "value": entry.content.get("value"),
        "confidence": entry.confidence,
        "status": entry.status,
        "provenance": entry.provenance,
    }


def decision_projection(project: Project) -> dict[str, dict[str, Any]]:
    """Return active, explainable decision state without transcript content."""
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist:
        return {}
    result: dict[str, dict[str, Any]] = {}
    entries = state.entries.filter(
        status=CognitiveStateEntry.Status.ACTIVE,
        kind__in=(
            CognitiveStateEntry.Kind.OPEN_DECISION,
            CognitiveStateEntry.Kind.ACCEPTED_DECISION,
        ),
    ).order_by("created_at", "pk")
    for entry in entries:
        attribute = entry.content.get("attribute")
        value = entry.content.get("value")
        if not isinstance(attribute, str) or not attribute.startswith("decision:"):
            continue
        if not isinstance(value, Mapping):
            continue
        result[attribute] = _entry_view(entry)
    return result


def open_decision(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, dict[str, Any]]:
    """Open a material decision from an active recommendation, never accept it."""
    source = _source(provenance)
    key = _text(
        observation.get("decision_key"), field="decision_key", required=True
    ).casefold()
    if not _KEY.fullmatch(key):
        raise ValueError("DECISION_KEY_INVALID")
    recommendation_key = _text(
        observation.get("recommendation_key"), field="recommendation_key", required=True
    ).casefold()
    recommendation_attribute = f"recommendation:{recommendation_key}"
    recommendation = recommendation_projection(project).get(recommendation_attribute)
    if recommendation is None:
        raise ValueError("DECISION_RECOMMENDATION_UNAVAILABLE")
    recommendation_value = recommendation["recommendation"]["value"]
    if not isinstance(recommendation_value, Mapping) or not recommendation_value.get(
        "requires_product_owner_decision"
    ):
        raise ValueError("DECISION_NOT_MATERIAL")
    attribute = f"decision:{key}"
    options = _options(observation.get("options"))
    recommended_option = _text(
        observation.get("recommended_option"), field="recommended_option", required=True
    )
    if recommended_option.casefold() not in {
        item["option"].casefold() for item in options
    }:
        raise ValueError("DECISION_RECOMMENDED_OPTION_INVALID")
    alternatives = recommendation.get("alternatives")
    trade_offs = recommendation.get("trade_offs")
    decision = {
        "key": key,
        "question": _text(observation.get("question"), field="question", required=True),
        "materiality_reason": _text(
            observation.get("materiality_reason"),
            field="materiality_reason",
            required=True,
        ),
        "options": options,
        "recommended_option": recommended_option,
        "impact_if_decided": _text(
            observation.get("impact_if_decided"),
            field="impact_if_decided",
            required=True,
        ),
        "impact_if_deferred": _text(
            observation.get("impact_if_deferred"),
            field="impact_if_deferred",
            required=True,
        ),
        "recommendation_entry_id": recommendation["recommendation"]["id"],
        "evidence_entry_ids": recommendation_value.get("evidence_entry_ids", []),
        "assumption_entry_ids": recommendation_value.get("assumption_entry_ids", []),
        "alternatives": alternatives.get("value", [])
        if isinstance(alternatives, Mapping)
        else [],
        "trade_offs": trade_offs.get("value", [])
        if isinstance(trade_offs, Mapping)
        else [],
    }
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("DECISION_RECOMMENDATION_UNAVAILABLE") from exc
    if state.entries.filter(
        kind=CognitiveStateEntry.Kind.ACCEPTED_DECISION,
        status=CognitiveStateEntry.Status.ACTIVE,
        content__attribute=attribute,
    ).exists():
        raise ValueError("DECISION_ALREADY_ACCEPTED")
    previous = (
        state.entries.filter(
            kind=CognitiveStateEntry.Kind.OPEN_DECISION,
            status=CognitiveStateEntry.Status.ACTIVE,
            content__attribute=attribute,
        )
        .order_by("-created_at", "-pk")
        .first()
    )
    entry = record_entry(
        project,
        kind=CognitiveStateEntry.Kind.OPEN_DECISION,
        content={"attribute": attribute, "value": decision},
        provenance=source,
        confidence=recommendation["recommendation"]["confidence"],
        supersedes=previous,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "evidence_type": "DECISION_ENGINE_OBSERVATION",
            "source_message_id": source["conversation_message_id"],
            "message_sha256": source["conversation_message_sha256"],
            "decision_entry_id": entry.pk,
            "recommendation_entry_id": decision["recommendation_entry_id"],
        },
        provenance=source,
    )
    return decision_projection(project)


def accept_decision(
    project: Project,
    *,
    decision_key: str,
    open_decision_entry_id: int,
    selected_option: str,
    provenance: Mapping[str, object],
) -> dict[str, dict[str, Any]]:
    """Accept an active option only from explicit Product Owner confirmation."""
    source = _product_owner_source(provenance)
    key = _text(decision_key, field="decision_key", required=True).casefold()
    if not _KEY.fullmatch(key):
        raise ValueError("DECISION_KEY_INVALID")
    attribute = f"decision:{key}"
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("DECISION_OPEN_UNAVAILABLE") from exc
    accepted = state.entries.filter(
        kind=CognitiveStateEntry.Kind.ACCEPTED_DECISION,
        status=CognitiveStateEntry.Status.ACTIVE,
        content__attribute=attribute,
        content__value__confirmation_reference=source["confirmation_reference"],
    ).first()
    if accepted is not None:
        return decision_projection(project)
    open_entry = state.entries.filter(
        pk=open_decision_entry_id,
        kind=CognitiveStateEntry.Kind.OPEN_DECISION,
        status=CognitiveStateEntry.Status.ACTIVE,
        content__attribute=attribute,
    ).first()
    if open_entry is None:
        raise ValueError("DECISION_OPEN_STALE_OR_UNAVAILABLE")
    value = open_entry.content.get("value")
    if not isinstance(value, Mapping):
        raise ValueError("DECISION_OPEN_STALE_OR_UNAVAILABLE")
    selected = _text(selected_option, field="selected_option", required=True)
    options = value.get("options", [])
    if not isinstance(options, list) or selected.casefold() not in {
        item.get("option", "").casefold()
        for item in options
        if isinstance(item, Mapping) and isinstance(item.get("option"), str)
    }:
        raise ValueError("DECISION_SELECTED_OPTION_INVALID")
    accepted_value = {
        "key": key,
        "question": value.get("question"),
        "selected_option": selected,
        "recommended_option": value.get("recommended_option"),
        "options": value.get("options", []),
        "materiality_reason": value.get("materiality_reason"),
        "impact_if_decided": value.get("impact_if_decided"),
        "impact_if_deferred": value.get("impact_if_deferred"),
        "open_decision_entry_id": open_entry.pk,
        "confirmation_reference": source["confirmation_reference"],
        "actor_id": source["actor_id"],
        "recommendation_entry_id": value.get("recommendation_entry_id"),
        "evidence_entry_ids": value.get("evidence_entry_ids", []),
        "assumption_entry_ids": value.get("assumption_entry_ids", []),
        "alternatives": value.get("alternatives", []),
        "trade_offs": value.get("trade_offs", []),
    }
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.ACCEPTED_DECISION,
        content={"attribute": attribute, "value": accepted_value},
        provenance=source,
        confidence=open_entry.confidence,
        supersedes=open_entry,
    )
    return decision_projection(project)

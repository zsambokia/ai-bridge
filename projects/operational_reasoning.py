"""Canonical, evidence-driven Operational Reasoning Engine for ORKI-010.

An LLM may propose a reasoning observation.  This module validates every
state reference and is the only ORKI-010 path that derives a recommendation.
It writes no plan, accepted decision, governance approval or execution action.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from django.db import transaction

from .cognitive_state import record_entry, record_snapshot
from .models import CognitiveState, CognitiveStateEntry, Project
from .product_owner_model import product_owner_projection
from .recommendation_engine import recommendation_projection, record_recommendation

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
_MISSION_KINDS = _EVIDENCE_KINDS - {CognitiveStateEntry.Kind.EVIDENCE}


def _text(value: object, field: str, *, required: bool = False) -> str:
    if value is None:
        if required:
            raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_REQUIRED")
        return ""
    if not isinstance(value, str):
        raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_INVALID")
    result = " ".join(value.split()).strip()
    if required and not result:
        raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_REQUIRED")
    return result[:2000]


def _strings(value: object, field: str, *, required: bool = False) -> list[str]:
    if value is None:
        if required:
            raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_REQUIRED")
        return []
    if not isinstance(value, list):
        raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_INVALID")
    result = list(dict.fromkeys(_text(item, field, required=True) for item in value))
    if required and not result:
        raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_REQUIRED")
    return result[:30]


def _confidence(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("OPERATIONAL_REASONING_CONFIDENCE_INVALID")
    result = float(value)
    if not 0 <= result <= 1:
        raise ValueError("OPERATIONAL_REASONING_CONFIDENCE_INVALID")
    return result


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("OPERATIONAL_REASONING_SOURCE_REQUIRED")
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


def _references(
    project: Project,
    attributes: list[str],
    allowed_kinds: set[CognitiveStateEntry.Kind],
    error: str,
) -> list[CognitiveStateEntry]:
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError(error) from exc
    entries: list[CognitiveStateEntry] = []
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
        entries.append(entry)
    return entries


def _alternatives(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) < 3:
        raise ValueError("OPERATIONAL_REASONING_ALTERNATIVES_INSUFFICIENT")
    alternatives: list[dict[str, object]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("OPERATIONAL_REASONING_ALTERNATIVES_INVALID")
        option = _text(item.get("option"), "alternative_option", required=True)
        key = option.casefold()
        if key in seen:
            raise ValueError("OPERATIONAL_REASONING_ALTERNATIVES_DUPLICATE")
        seen.add(key)
        simplicity = item.get("simplicity_score")
        if (
            not isinstance(simplicity, int)
            or isinstance(simplicity, bool)
            or not 1 <= simplicity <= 10
        ):
            raise ValueError("OPERATIONAL_REASONING_SIMPLICITY_SCORE_INVALID")
        alternatives.append(
            {
                "option": option,
                "summary": _text(
                    item.get("summary"), "alternative_summary", required=True
                ),
                "cost": _text(item.get("cost"), "alternative_cost", required=True),
                "risk": _text(item.get("risk"), "alternative_risk", required=True),
                "long_term_effect": _text(
                    item.get("long_term_effect"),
                    "alternative_long_term_effect",
                    required=True,
                ),
                "simplicity_score": simplicity,
            }
        )
    return alternatives[:10]


def _per_option_items(
    value: object, field: str, options: set[str], required_keys: tuple[str, ...]
) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_INVALID")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_INVALID")
        parsed = {
            key: _text(item.get(key), f"{field}_{key}", required=True)
            for key in required_keys
        }
        option = parsed["option"].casefold()
        if option not in options or option in seen:
            raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_COVERAGE_INVALID")
        seen.add(option)
        result.append(parsed)
    if seen != options:
        raise ValueError(f"OPERATIONAL_REASONING_{field.upper()}_COVERAGE_INVALID")
    return result


def _profile_influences(
    project: Project, dimensions: list[str]
) -> list[dict[str, object]]:
    if not dimensions:
        return []
    projection = product_owner_projection(project)
    profiles = projection.get("profiles", {})
    conflicts = projection.get("conflicts", [])
    conflict_dimensions = {
        conflict.get("dimension")
        for conflict in conflicts
        if isinstance(conflict, Mapping) and isinstance(conflict.get("dimension"), str)
    }
    influences: list[dict[str, object]] = []
    for dimension in dimensions:
        if dimension in conflict_dimensions:
            raise ValueError("OPERATIONAL_REASONING_PRODUCT_OWNER_PROFILE_CONFLICT")
        detail = profiles.get(dimension) if isinstance(profiles, Mapping) else None
        if not isinstance(detail, Mapping) or not isinstance(
            detail.get("profile"), Mapping
        ):
            raise ValueError("OPERATIONAL_REASONING_PRODUCT_OWNER_PROFILE_UNAVAILABLE")
        profile = detail["profile"]
        influences.append(
            {
                "dimension": dimension,
                "profile_entry_id": profile.get("id"),
                "preference": profile.get("value"),
                "confidence": profile.get("confidence"),
                "evidence": detail.get("evidence", []),
            }
        )
    return influences


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


def operational_reasoning_projection(project: Project) -> dict[str, dict[str, Any]]:
    """Return active reasoning cycles and their state-derived recommendation."""
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist:
        return {}
    recommendations = recommendation_projection(project)
    result: dict[str, dict[str, Any]] = {}
    for entry in state.entries.filter(
        kind=CognitiveStateEntry.Kind.OPERATIONAL_REASONING,
        status=CognitiveStateEntry.Status.ACTIVE,
    ).order_by("created_at", "pk"):
        attribute = entry.content.get("attribute")
        value = entry.content.get("value")
        if not isinstance(attribute, str) or not isinstance(value, Mapping):
            continue
        source_ids = [
            *value.get("mission_entry_ids", []),
            *value.get("evidence_entry_ids", []),
            *value.get("assumption_entry_ids", []),
        ]
        sources = {item.pk: item for item in state.entries.filter(pk__in=source_ids)}
        recommendation_attribute = value.get("recommendation_attribute")
        result[attribute] = {
            "reasoning": _entry_view(entry),
            "mission": [
                _entry_view(sources[item])
                for item in value.get("mission_entry_ids", [])
                if item in sources
            ],
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
            "recommendation": recommendations.get(recommendation_attribute)
            if isinstance(recommendation_attribute, str)
            else None,
        }
    return result


def record_operational_reasoning(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, dict[str, Any]]:
    """Validate a full reasoning cycle and derive its recommendation atomically."""
    source = _source(provenance)
    key = _text(
        observation.get("reasoning_key"), "reasoning_key", required=True
    ).casefold()
    if not _KEY.fullmatch(key):
        raise ValueError("OPERATIONAL_REASONING_KEY_INVALID")
    mission_attributes = _strings(
        observation.get("mission_attributes"), "mission_attributes", required=True
    )
    evidence_attributes = _strings(
        observation.get("evidence_attributes"), "evidence_attributes", required=True
    )
    assumption_attributes = _strings(
        observation.get("assumption_attributes"), "assumption_attributes"
    )
    if "unknowns" not in observation:
        raise ValueError("OPERATIONAL_REASONING_UNKNOWNS_REQUIRED")
    mission = _references(
        project,
        mission_attributes,
        _MISSION_KINDS,
        "OPERATIONAL_REASONING_MISSION_UNAVAILABLE",
    )
    evidence = _references(
        project,
        evidence_attributes,
        _EVIDENCE_KINDS,
        "OPERATIONAL_REASONING_EVIDENCE_UNAVAILABLE",
    )
    assumptions = _references(
        project,
        assumption_attributes,
        {CognitiveStateEntry.Kind.ASSUMPTION},
        "OPERATIONAL_REASONING_ASSUMPTION_UNAVAILABLE",
    )
    alternatives = _alternatives(observation.get("alternatives"))
    options = {
        _text(item.get("option"), "alternative_option", required=True).casefold()
        for item in alternatives
    }
    trade_offs = _per_option_items(
        observation.get("trade_offs"),
        "trade_offs",
        options,
        ("option", "benefit", "cost"),
    )
    counter_arguments = _per_option_items(
        observation.get("counter_arguments"),
        "counter_arguments",
        options,
        ("option", "reason"),
    )
    recommendation_option = _text(
        observation.get("recommendation"), "recommendation", required=True
    )
    if recommendation_option.casefold() not in options:
        raise ValueError("OPERATIONAL_REASONING_RECOMMENDATION_OPTION_INVALID")
    priority = _text(observation.get("priority"), "priority", required=True).upper()
    if priority not in _PRIORITIES:
        raise ValueError("OPERATIONAL_REASONING_PRIORITY_INVALID")
    required_decision = observation.get("required_decision")
    if not isinstance(required_decision, Mapping) or not isinstance(
        required_decision.get("required"), bool
    ):
        raise ValueError("OPERATIONAL_REASONING_DECISION_BOUNDARY_INVALID")
    needs_decision = required_decision["required"]
    question = _text(
        required_decision.get("question"),
        "required_decision_question",
        required=needs_decision,
    )
    materiality = _text(
        required_decision.get("materiality_reason"),
        "required_decision_materiality_reason",
        required=needs_decision,
    )
    profile_dimensions = _strings(
        observation.get("product_owner_profile_dimensions"),
        "product_owner_profile_dimensions",
    )
    influences = _profile_influences(project, profile_dimensions)
    confidence = _confidence(observation.get("confidence"))
    recommendation_attribute = f"recommendation:{key}"
    attribute = f"operational-reasoning:{key}"
    reasoning = {
        "key": key,
        "mission_entry_ids": [entry.pk for entry in mission],
        "evidence_entry_ids": [entry.pk for entry in evidence],
        "assumption_entry_ids": [entry.pk for entry in assumptions],
        "unknowns": _strings(observation.get("unknowns"), "unknowns"),
        "alternatives": alternatives,
        "trade_offs": trade_offs,
        "counter_arguments": counter_arguments,
        "recommendation": recommendation_option,
        "reasoning": _text(observation.get("reasoning"), "reasoning", required=True),
        "expected_impact": _text(
            observation.get("expected_impact"), "expected_impact", required=True
        ),
        "priority": priority,
        "dependencies": _strings(observation.get("dependencies"), "dependencies"),
        "next_safe_action": _text(
            observation.get("next_safe_action"), "next_safe_action", required=True
        ),
        "required_decision": {
            "required": needs_decision,
            "question": question,
            "materiality_reason": materiality,
        },
        "product_owner_influences": influences,
        "recommendation_attribute": recommendation_attribute,
    }
    with transaction.atomic():
        record_recommendation(
            project,
            observation={
                "recommendation_key": key,
                "priority": priority,
                "recommendation": recommendation_option,
                "rationale": reasoning["reasoning"],
                "business_impact": reasoning["expected_impact"],
                "dependencies": reasoning["dependencies"],
                "next_safe_action": reasoning["next_safe_action"],
                "requires_product_owner_decision": needs_decision,
                "evidence_attributes": evidence_attributes,
                "assumption_attributes": assumption_attributes,
                "alternatives": [
                    {"option": item["option"], "summary": item["summary"]}
                    for item in alternatives
                ],
                "trade_offs": trade_offs,
                "confidence": confidence,
            },
            provenance=source,
        )
        record_snapshot(
            project,
            kind=CognitiveStateEntry.Kind.OPERATIONAL_REASONING,
            attribute=attribute,
            value=reasoning,
            confidence=confidence,
            provenance=source,
        )
        record_entry(
            project,
            kind=CognitiveStateEntry.Kind.EVIDENCE,
            content={
                "evidence_type": "OPERATIONAL_REASONING_OBSERVATION",
                "source_message_id": source["conversation_message_id"],
                "message_sha256": source["conversation_message_sha256"],
                "reasoning_attribute": attribute,
                "recommendation_attribute": recommendation_attribute,
                "evidence_entry_ids": [entry.pk for entry in evidence],
            },
            provenance=source,
        )
    return operational_reasoning_projection(project)

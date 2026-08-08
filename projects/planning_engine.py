"""Canonical, evidence-bound Planning Intelligence for ORKI-005.

A Cognitive Plan is an explainable reasoning artefact.  It is deliberately
separate from the legacy FactoryPlan delivery workflow and creates neither
governance authority nor executable work.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .cognitive_state import record_entry
from .models import CognitiveState, CognitiveStateEntry, Project

_KEY = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_SOURCE_KINDS = {
    CognitiveStateEntry.Kind.MISSION.value,
    CognitiveStateEntry.Kind.BUSINESS_CONTEXT.value,
    CognitiveStateEntry.Kind.GOAL.value,
    CognitiveStateEntry.Kind.CONSTRAINT.value,
    CognitiveStateEntry.Kind.FACT.value,
    CognitiveStateEntry.Kind.INFERENCE.value,
    CognitiveStateEntry.Kind.EVIDENCE.value,
    CognitiveStateEntry.Kind.RISK.value,
    CognitiveStateEntry.Kind.OPPORTUNITY.value,
    CognitiveStateEntry.Kind.RECOMMENDATION.value,
}


def _text(value: object, *, field: str, required: bool = True) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"PLAN_{field.upper()}_INVALID")
    result = " ".join(value.split()).strip()
    if required and not result:
        raise ValueError(f"PLAN_{field.upper()}_REQUIRED")
    return result[:2000]


def _strings(value: object, *, field: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"PLAN_{field.upper()}_INVALID")
    result: list[str] = []
    for item in value:
        text = _text(item, field=field)
        if text.casefold() not in {existing.casefold() for existing in result}:
            result.append(text)
    if len(result) < minimum:
        raise ValueError(f"PLAN_{field.upper()}_INSUFFICIENT")
    return result[:30]


def _items(value: object, *, field: str) -> list[dict[str, str]]:
    if not isinstance(value, list) or len(value) < 2:
        raise ValueError(f"PLAN_{field.upper()}_INSUFFICIENT")
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError(f"PLAN_{field.upper()}_INVALID")
        option = _text(item.get("option"), field=f"{field}_option")
        summary = _text(item.get("summary"), field=f"{field}_summary")
        if option.casefold() in {old["option"].casefold() for old in result}:
            raise ValueError(f"PLAN_{field.upper()}_INVALID")
        result.append({"option": option, "summary": summary})
    return result[:10]


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("PLAN_SOURCE_REQUIRED")
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


def _confidence(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError("PLAN_CONFIDENCE_INVALID")
    result = float(value)
    if not 0.0 <= result <= 1.0:
        raise ValueError("PLAN_CONFIDENCE_INVALID")
    return result


def _references(project: Project, attributes: list[str]) -> list[CognitiveStateEntry]:
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("PLAN_EVIDENCE_UNAVAILABLE") from exc
    result: list[CognitiveStateEntry] = []
    for attribute in attributes:
        # JSON lookup semantics vary across supported database backends; resolve
        # the small active Cognitive State explicitly so an evidence reference is
        # deterministic across SQLite and production engines.
        entry = next(
            (
                candidate
                for candidate in state.entries.filter(
                    status=CognitiveStateEntry.Status.ACTIVE
                ).order_by("-created_at", "-pk")
                if candidate.content.get("attribute") == attribute
                and candidate.kind in _SOURCE_KINDS
            ),
            None,
        )
        if entry is None:
            raise ValueError("PLAN_EVIDENCE_UNAVAILABLE")
        result.append(entry)
    return result


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


def planning_projection(project: Project) -> dict[str, dict[str, Any]]:
    """Return active plans with only durable explainability references."""
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist:
        return {}
    result: dict[str, dict[str, Any]] = {}
    for entry in state.entries.filter(
        kind=CognitiveStateEntry.Kind.PLAN, status=CognitiveStateEntry.Status.ACTIVE
    ):
        attribute, value = entry.content.get("attribute"), entry.content.get("value")
        if not isinstance(attribute, str) or not isinstance(value, Mapping):
            continue
        sources = {
            source.pk: source
            for source in state.entries.filter(
                pk__in=value.get("evidence_entry_ids", [])
            ).order_by("pk")
        }
        result[attribute] = {
            "plan": _entry_view(entry),
            "evidence": [
                _entry_view(sources[item])
                for item in value.get("evidence_entry_ids", [])
                if item in sources
            ],
        }
    return result


def record_plan(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, dict[str, Any]]:
    """Validate and evolve an evidence-backed plan; never create delivery work."""
    source = _source(provenance)
    key = _text(observation.get("plan_key"), field="plan_key").casefold()
    if not _KEY.fullmatch(key):
        raise ValueError("PLAN_KEY_INVALID")
    alternatives = _items(observation.get("alternatives"), field="alternatives")
    chosen = _text(observation.get("chosen_strategy"), field="chosen_strategy")
    rejected = _text(observation.get("rejected_strategy"), field="rejected_strategy")
    option_names = {item["option"].casefold() for item in alternatives}
    if (
        chosen.casefold() not in option_names
        or rejected.casefold() not in option_names
        or chosen.casefold() == rejected.casefold()
    ):
        raise ValueError("PLAN_STRATEGY_ALTERNATIVE_INVALID")
    evidence = _references(
        project,
        _strings(observation.get("evidence_attributes"), field="evidence_attributes"),
    )
    value = {
        "key": key,
        "objective": _text(observation.get("objective"), field="objective"),
        "business_value": _text(
            observation.get("business_value"), field="business_value"
        ),
        "architecture": _text(observation.get("architecture"), field="architecture"),
        "alternatives": alternatives,
        "chosen_strategy": chosen,
        "rejected_strategy": rejected,
        "risks": _strings(observation.get("risks"), field="risks"),
        "dependencies": _strings(observation.get("dependencies"), field="dependencies"),
        "acceptance": _strings(observation.get("acceptance"), field="acceptance"),
        "release_strategy": _text(
            observation.get("release_strategy"), field="release_strategy"
        ),
        "operational_strategy": _text(
            observation.get("operational_strategy"), field="operational_strategy"
        ),
        "recovery_strategy": _text(
            observation.get("recovery_strategy"), field="recovery_strategy"
        ),
        "future_evolution": _text(
            observation.get("future_evolution"), field="future_evolution"
        ),
        "evidence_entry_ids": [entry.pk for entry in evidence],
    }
    attribute = f"plan:{key}"
    state = project.cognitive_state
    previous = (
        state.entries.filter(
            kind=CognitiveStateEntry.Kind.PLAN,
            status=CognitiveStateEntry.Status.ACTIVE,
            content__attribute=attribute,
        )
        .order_by("-created_at", "-pk")
        .first()
    )
    entry = record_entry(
        project,
        kind=CognitiveStateEntry.Kind.PLAN,
        content={"attribute": attribute, "value": value},
        provenance=source,
        confidence=_confidence(observation.get("confidence")),
        supersedes=previous,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "evidence_type": "PLANNING_ENGINE_OBSERVATION",
            "source_message_id": source["conversation_message_id"],
            "message_sha256": source["conversation_message_sha256"],
            "plan_entry_id": entry.pk,
            "evidence_entry_ids": value["evidence_entry_ids"],
        },
        provenance=source,
    )
    return planning_projection(project)

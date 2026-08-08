"""Evidence-bound operational Product Owner model for ORKI-008 and ORKI-009.

This module deliberately models only project-scoped working preferences.  It
never reads a chat transcript, accepts personal attributes, or grants planning,
governance, or execution authority.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from .cognitive_state import record_entry
from .models import CognitiveState, CognitiveStateEntry, Project

_DIMENSIONS = frozenset(
    {
        "decision_style",
        "risk_tolerance",
        "planning_depth",
        "documentation_preference",
        "sprint_size_preference",
        "architecture_preference",
        "governance_preference",
        "evidence_preference",
        "communication_style",
        "preferred_technologies",
    }
)
_PROFILE_PREFIX = "product-owner:"
_SENSITIVE_MARKERS = re.compile(
    r"\b(?:email|e-mail|phone|address|password|secret|token|ssn|health|medical|"
    r"religion|political|ethnicity|date of birth)\b|@",
    re.IGNORECASE,
)


def _text(value: object, field: str, *, required: bool = True) -> str:
    if not isinstance(value, str):
        if required:
            raise ValueError(f"PRODUCT_OWNER_{field.upper()}_REQUIRED")
        return ""
    result = " ".join(value.split())
    if required and not result:
        raise ValueError(f"PRODUCT_OWNER_{field.upper()}_REQUIRED")
    if _SENSITIVE_MARKERS.search(result):
        raise ValueError("PRODUCT_OWNER_PERSONAL_DATA_FORBIDDEN")
    return result[:500]


def _confidence(value: object) -> float:
    if not isinstance(value, (float, int)) or isinstance(value, bool):
        raise ValueError("PRODUCT_OWNER_CONFIDENCE_INVALID")
    result = float(value)
    if not 0 <= result <= 1:
        raise ValueError("PRODUCT_OWNER_CONFIDENCE_INVALID")
    return result


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("PRODUCT_OWNER_SOURCE_REQUIRED")
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


def _correction_source(provenance: Mapping[str, object]) -> dict[str, object]:
    if provenance.get("source_type") != "PRODUCT_OWNER_PROFILE_CORRECTION":
        raise ValueError("PRODUCT_OWNER_CORRECTION_SOURCE_INVALID")
    if provenance.get("actor_type") != "PRODUCT_OWNER":
        raise ValueError("PRODUCT_OWNER_CORRECTION_ACTOR_INVALID")
    actor_id = _text(provenance.get("actor_id"), "actor_id")
    return {
        "source_type": "PRODUCT_OWNER_PROFILE_CORRECTION",
        "actor_type": "PRODUCT_OWNER",
        "actor_id": actor_id[:128],
    }


def _references(project: Project, attributes: list[str]) -> list[CognitiveStateEntry]:
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("PRODUCT_OWNER_EVIDENCE_UNAVAILABLE") from exc
    if len(attributes) < 2:
        raise ValueError("PRODUCT_OWNER_EVIDENCE_INSUFFICIENT")
    result: list[CognitiveStateEntry] = []
    for attribute in attributes:
        entry = (
            state.entries.filter(
                status=CognitiveStateEntry.Status.ACTIVE,
                content__attribute=attribute,
            )
            .exclude(kind__in=(
                CognitiveStateEntry.Kind.EVIDENCE,
                CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
            ))
            .order_by("-created_at", "-pk")
            .first()
        )
        if entry is None:
            raise ValueError("PRODUCT_OWNER_EVIDENCE_UNAVAILABLE")
        result.append(entry)
    return result


def _attributes(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("PRODUCT_OWNER_EVIDENCE_REQUIRED")
    attributes = list(
        dict.fromkeys(_text(item, "evidence_attribute") for item in value)
    )
    if len(attributes) < 2:
        raise ValueError("PRODUCT_OWNER_EVIDENCE_INSUFFICIENT")
    return attributes[:20]


def _entry_view(entry: CognitiveStateEntry) -> dict[str, Any]:
    return {
        "id": entry.pk,
        "attribute": entry.content.get("attribute"),
        "value": entry.content.get("value"),
        "confidence": entry.confidence,
        "status": entry.status,
        "provenance": entry.provenance,
    }


def _evidence_view(entries: list[CognitiveStateEntry]) -> list[dict[str, Any]]:
    """Expose state evidence, never conversation text, for profile review."""
    return [
        {
            "entry_id": entry.pk,
            "attribute": entry.content.get("attribute"),
            "confidence": entry.confidence,
            "conversation_message_id": entry.provenance.get("conversation_message_id"),
        }
        for entry in entries
    ]


def _weighted_confidence(
    declared: float, evidence: list[CognitiveStateEntry]
) -> tuple[float, dict[str, Any]]:
    scored_evidence = [
        entry.confidence for entry in evidence if entry.confidence is not None
    ]
    if not scored_evidence:
        return declared, {
            "declared_confidence": declared,
            "evidence_mean_confidence": None,
            "weights": {"declared": 1.0, "evidence": 0.0},
            "unscored_evidence_count": len(evidence),
            "result": declared,
        }
    evidence_mean = sum(scored_evidence) / len(scored_evidence)
    weighted = round((declared * 0.6) + (evidence_mean * 0.4), 4)
    return weighted, {
        "declared_confidence": declared,
        "evidence_mean_confidence": round(evidence_mean, 4),
        "weights": {"declared": 0.6, "evidence": 0.4},
        "unscored_evidence_count": len(evidence) - len(scored_evidence),
        "result": weighted,
    }


def product_owner_history(project: Project) -> dict[str, Any]:
    """Return revision history and explicit drift, without selecting a winner."""
    try:
        entries = project.cognitive_state.entries.filter(
            kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE
        ).order_by("created_at", "pk")
    except CognitiveState.DoesNotExist:
        return {"history": {}, "drift": []}
    history: dict[str, list[dict[str, Any]]] = defaultdict(list)
    drift: list[dict[str, Any]] = []
    for entry in entries:
        attribute = entry.content.get("attribute")
        value = entry.content.get("value")
        if not isinstance(attribute, str) or not attribute.startswith(_PROFILE_PREFIX):
            continue
        if not isinstance(value, Mapping):
            continue
        dimension = attribute.removeprefix(_PROFILE_PREFIX)
        revision = {
            "entry_id": entry.pk,
            "preference": value.get("preference"),
            "confidence": entry.confidence,
            "status": entry.status,
            "created_at": entry.created_at.isoformat(),
            "evidence_entry_ids": value.get("evidence_entry_ids", []),
            "confidence_explanation": value.get("confidence_explanation"),
        }
        previous = history[dimension][-1] if history[dimension] else None
        history[dimension].append(revision)
        if previous and previous["preference"] != revision["preference"]:
            drift.append({
                "dimension": dimension,
                "previous": previous,
                "current": revision,
                "reason": (
                    "Evidence-backed profile preference changed; "
                    "no prior revision was erased."
                ),
            }
        )
    return {"history": dict(history), "drift": drift}


def product_owner_projection(project: Project) -> dict[str, Any]:
    """Return explainable active preferences and fail closed on a conflict."""
    try:
        entries = project.cognitive_state.entries.filter(
            kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
            status=CognitiveStateEntry.Status.ACTIVE,
        ).order_by("created_at", "pk")
    except CognitiveState.DoesNotExist:
        return {"profiles": {}, "conflicts": [], "history": {}, "drift": []}
    grouped: dict[str, list[CognitiveStateEntry]] = defaultdict(list)
    for entry in entries:
        attribute = entry.content.get("attribute")
        if isinstance(attribute, str) and attribute.startswith(_PROFILE_PREFIX):
            grouped[attribute].append(entry)
    profiles: dict[str, dict[str, Any]] = {}
    conflicts: list[dict[str, Any]] = []
    for attribute, candidates in grouped.items():
        values = {
            str(entry.content.get("value", {}).get("preference", ""))
            for entry in candidates
            if isinstance(entry.content.get("value"), Mapping)
        }
        dimension = attribute.removeprefix(_PROFILE_PREFIX)
        if len(values) != 1 or not values:
            conflicts.append(
                {
                    "dimension": dimension,
                    "entries": [_entry_view(entry) for entry in candidates],
                    "active_inference": None,
                }
            )
            continue
        entry = candidates[-1]
        value = entry.content["value"]
        evidence_entries = list(project.cognitive_state.entries.filter(
            pk__in=value.get("evidence_entry_ids", [])
        ))
        profiles[dimension] = {
            "profile": _entry_view(entry),
            "evidence_entry_ids": value.get("evidence_entry_ids", []),
            "evidence_attributes": value.get("evidence_attributes", []),
            "evidence": _evidence_view(evidence_entries),
            "confidence_explanation": value.get("confidence_explanation"),
            "scope": "PROJECT",
            "authority": "NONE",
        }
    return {
        "profiles": profiles,
        "conflicts": conflicts,
        **product_owner_history(project),
    }


def record_product_owner_profile(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> dict[str, Any]:
    """Record one evidence-backed operational preference revision.

    A provider may propose it, but it is admitted only when at least two active
    project-state attributes support it.  The profile is deliberately project
    scoped: portable owner baselines need an explicit future policy.
    """
    source = _source(provenance)
    dimension = _text(observation.get("dimension"), "dimension").casefold()
    if dimension not in _DIMENSIONS:
        raise ValueError("PRODUCT_OWNER_DIMENSION_INVALID")
    preference = _text(observation.get("preference"), "preference")
    rationale = _text(observation.get("rationale"), "rationale")
    declared_confidence = _confidence(observation.get("confidence"))
    attributes = _attributes(observation.get("evidence_attributes"))
    evidence = _references(project, attributes)
    confidence, confidence_explanation = _weighted_confidence(
        declared_confidence, evidence
    )
    state = project.cognitive_state
    attribute = f"{_PROFILE_PREFIX}{dimension}"
    prior = (
        state.entries.filter(
            kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
            status=CognitiveStateEntry.Status.ACTIVE,
            content__attribute=attribute,
        )
        .order_by("-created_at", "-pk")
        .first()
    )
    value = {
        "dimension": dimension,
        "preference": preference,
        "rationale": rationale,
        "scope": "PROJECT",
        "evidence_entry_ids": [entry.pk for entry in evidence],
        "evidence_attributes": attributes,
        "confidence_explanation": confidence_explanation,
    }
    if prior and prior.content.get("value") == value and prior.confidence == confidence:
        return product_owner_projection(project)
    profile = record_entry(
        project,
        kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
        content={"attribute": attribute, "value": value},
        provenance=source,
        confidence=confidence,
        supersedes=prior,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "evidence_type": "PRODUCT_OWNER_PROFILE_OBSERVATION",
            "profile_entry_id": profile.pk,
            "source_entry_ids": [entry.pk for entry in evidence],
        },
        provenance=source,
        confidence=confidence,
    )
    return product_owner_projection(project)


def correct_product_owner_profile(
    project: Project,
    *,
    profile_entry_id: int,
    preference: object,
    reason: object,
    provenance: Mapping[str, object],
) -> dict[str, Any]:
    """Apply an attributable Product Owner correction without erasing evidence."""
    source = _correction_source(provenance)
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("PRODUCT_OWNER_PROFILE_UNAVAILABLE") from exc
    prior = state.entries.filter(
        pk=profile_entry_id,
        kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
        status=CognitiveStateEntry.Status.ACTIVE,
    ).first()
    if prior is None:
        raise ValueError("PRODUCT_OWNER_PROFILE_UNAVAILABLE")
    old_value = prior.content.get("value")
    if not isinstance(old_value, Mapping):
        raise ValueError("PRODUCT_OWNER_PROFILE_UNAVAILABLE")
    corrected_value = dict(old_value)
    corrected_value["preference"] = _text(preference, "preference")
    corrected_value["correction_reason"] = _text(reason, "correction_reason")
    corrected_value["scope"] = "PROJECT"
    corrected = record_entry(
        project,
        kind=CognitiveStateEntry.Kind.PRODUCT_OWNER_PROFILE,
        content={"attribute": prior.content.get("attribute"), "value": corrected_value},
        provenance=source,
        confidence=prior.confidence,
        corrects=prior,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "evidence_type": "PRODUCT_OWNER_PROFILE_CORRECTION",
            "profile_entry_id": corrected.pk,
            "corrects_entry_id": prior.pk,
        },
        provenance=source,
        confidence=corrected.confidence,
    )
    return product_owner_projection(project)

"""Evolutionary, evidence-bound Memory Intelligence for ORKI-006."""

from __future__ import annotations

import re
from collections.abc import Mapping

from .cognitive_state import record_entry
from .models import CognitiveState, CognitiveStateEntry, Project

_KEY = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not (result := " ".join(value.split())):
        raise ValueError(f"MEMORY_{field.upper()}_REQUIRED")
    return result[:2000]


def _strings(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"MEMORY_{field.upper()}_REQUIRED")
    return list(dict.fromkeys(_text(item, field) for item in value))[:20]


def _source(provenance: Mapping[str, object]) -> dict[str, object]:
    required = {"source_type", "conversation_message_id", "conversation_message_sha256"}
    if not required.issubset(provenance):
        raise ValueError("MEMORY_SOURCE_REQUIRED")
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


def _references(project: Project, attributes: list[str]) -> list[CognitiveStateEntry]:
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("MEMORY_EVIDENCE_UNAVAILABLE") from exc
    entries: list[CognitiveStateEntry] = []
    for attribute in attributes:
        entry = (
            state.entries.filter(
                status=CognitiveStateEntry.Status.ACTIVE,
                content__attribute=attribute,
            )
            .exclude(kind=CognitiveStateEntry.Kind.MEMORY)
            .order_by("-created_at", "-pk")
            .first()
        )
        if entry is None:
            raise ValueError("MEMORY_EVIDENCE_UNAVAILABLE")
        entries.append(entry)
    return entries


def record_memory(
    project: Project,
    *,
    observation: Mapping[str, object],
    provenance: Mapping[str, object],
) -> CognitiveStateEntry | None:
    """Record one reusable memory revision from attributable active evidence."""
    key = _text(observation.get("memory_key"), "key").lower()
    if not _KEY.fullmatch(key):
        raise ValueError("MEMORY_KEY_INVALID")
    statement = _text(observation.get("statement"), "statement")
    tags = _strings(observation.get("tags"), "tags")
    attributes = _strings(observation.get("evidence_attributes"), "evidence_attributes")
    confidence = observation.get("confidence")
    if not isinstance(confidence, (float, int)) or isinstance(confidence, bool):
        raise ValueError("MEMORY_CONFIDENCE_INVALID")
    confidence = float(confidence)
    if not 0 <= confidence <= 1:
        raise ValueError("MEMORY_CONFIDENCE_INVALID")
    sources = _references(project, attributes)
    state = project.cognitive_state
    prior = (
        state.entries.filter(
            kind=CognitiveStateEntry.Kind.MEMORY,
            status=CognitiveStateEntry.Status.ACTIVE,
            content__attribute=f"memory:{key}",
        )
        .order_by("-created_at", "-pk")
        .first()
    )
    content = {
        "attribute": f"memory:{key}",
        "value": statement,
        "tags": tags,
        "evidence_entry_ids": [entry.pk for entry in sources],
        "evidence_attributes": attributes,
    }
    if prior and prior.content == content and prior.confidence == confidence:
        return None
    memory = record_entry(
        project,
        kind=CognitiveStateEntry.Kind.MEMORY,
        content=content,
        provenance=_source(provenance),
        confidence=confidence,
        supersedes=prior,
    )
    record_entry(
        project,
        kind=CognitiveStateEntry.Kind.EVIDENCE,
        content={
            "attribute": f"memory-evidence:{key}",
            "value": {
                "memory_entry_id": memory.pk,
                "source_entry_ids": [e.pk for e in sources],
            },
        },
        provenance=_source(provenance),
    )
    return memory


def memory_projection(project: Project, query: str = "") -> list[dict[str, object]]:
    """Retrieve active memories deterministically, never from transcript."""
    try:
        entries = project.cognitive_state.entries.filter(
            kind=CognitiveStateEntry.Kind.MEMORY,
            status=CognitiveStateEntry.Status.ACTIVE,
        )
    except CognitiveState.DoesNotExist:
        return []
    tokens = set(re.findall(r"[a-z0-9-]+", query.lower()))
    result = []
    for entry in entries:
        content = entry.content
        haystack = " ".join(
            [str(content.get("value", "")), *content.get("tags", [])]
        ).lower()
        score = len(tokens.intersection(re.findall(r"[a-z0-9-]+", haystack)))
        result.append(
            {
                "id": entry.pk,
                "content": content,
                "confidence": entry.confidence,
                "provenance": entry.provenance,
                "relevance": score,
            }
        )
    return sorted(
        result,
        key=lambda item: (-item["relevance"], -(item["confidence"] or 0), -item["id"]),
    )

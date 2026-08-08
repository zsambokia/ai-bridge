"""Deterministic, bounded Initiative Engine for ORKI-007.

Initiative is a Cognitive State observation, not a provider suggestion and not
authority.  It deliberately reads only canonical project state, links every
observation to the state entry that caused it, and can be dismissed without
mutating its source evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.db import transaction

from .cognitive_state import record_entry, state_for
from .models import CognitiveState, CognitiveStateEntry, Project

_RULES: tuple[tuple[str, str, str, int], ...] = (
    (
        CognitiveStateEntry.Kind.RISK,
        "RISK",
        (
            "A kockázat kezelését még a következő tervezési vagy végrehajtási "
            "lépés előtt érdemes tisztázni."
        ),
        90,
    ),
    (
        CognitiveStateEntry.Kind.OPPORTUNITY,
        "OPPORTUNITY",
        (
            "Azonosítottam egy lehetőséget, amely egyszerűsítheti vagy javíthatja "
            "a következő biztonságos lépést."
        ),
        70,
    ),
    (
        CognitiveStateEntry.Kind.ASSUMPTION,
        "MISSING_EVIDENCE",
        (
            "Ez még feltételezés; a továbblépés előtt érdemes bizonyítékot szerezni "
            "vagy tudatosan elfogadni."
        ),
        65,
    ),
)
MAX_ACTIVE_INITIATIVES = 5


def _summary(entry: CognitiveStateEntry) -> str:
    value = entry.content.get("value")
    if isinstance(value, str):
        return " ".join(value.split())[:500]
    if isinstance(value, list):
        text = "; ".join(str(item) for item in value if isinstance(item, str))
        if text:
            return text[:500]
    return str(entry.content.get("attribute", entry.kind))[:500]


def _view(entry: CognitiveStateEntry) -> dict[str, Any]:
    return {
        "id": entry.pk,
        "attribute": entry.content.get("attribute"),
        "value": entry.content.get("value"),
        "confidence": entry.confidence,
        "status": entry.status,
        "provenance": entry.provenance,
    }


def initiative_projection(
    project: Project, *, include_dismissed: bool = False
) -> list[dict[str, Any]]:
    """Return prioritised initiative artefacts with source state, never transcript."""
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist:
        return []
    statuses = [CognitiveStateEntry.Status.ACTIVE]
    if include_dismissed:
        statuses.append(CognitiveStateEntry.Status.DISMISSED)
    entries = state.entries.filter(
        kind=CognitiveStateEntry.Kind.INITIATIVE, status__in=statuses
    ).order_by("-created_at", "-pk")
    result: list[dict[str, Any]] = []
    for entry in entries:
        value = entry.content.get("value")
        if not isinstance(value, Mapping):
            continue
        source_id = value.get("source_entry_id")
        source = (
            state.entries.filter(pk=source_id).first()
            if isinstance(source_id, (int, str))
            else None
        )
        priority = value.get("priority", 0)
        priority_value = priority if isinstance(priority, int) else 0
        result.append(
            {
                "initiative": _view(entry),
                "source": _view(source) if source is not None else None,
                "priority": priority_value,
            }
        )
    return sorted(
        result,
        key=lambda item: (-item["priority"], -(item["initiative"]["id"] or 0)),
    )


def derive_initiatives(project: Project) -> list[dict[str, Any]]:
    """Derive de-duplicated initiatives from active state without an owner prompt.

    Each rule is intentionally narrow and deterministic. It cannot infer a new
    business fact, change source state, ask a question, approve work, or execute
    anything. Re-running it is idempotent while the source remains active.
    """
    state = state_for(project)
    with transaction.atomic():
        active_count = state.entries.filter(
            kind=CognitiveStateEntry.Kind.INITIATIVE,
            status=CognitiveStateEntry.Status.ACTIVE,
        ).count()
        for source_kind, category, rationale, priority in _RULES:
            for source in state.entries.filter(
                kind=source_kind, status=CognitiveStateEntry.Status.ACTIVE
            ).order_by("created_at", "pk"):
                if active_count >= MAX_ACTIVE_INITIATIVES:
                    return initiative_projection(project)
                key = f"initiative:{category.lower()}:{source.pk}"
                if state.entries.filter(
                    kind=CognitiveStateEntry.Kind.INITIATIVE,
                    status__in=[
                        CognitiveStateEntry.Status.ACTIVE,
                        CognitiveStateEntry.Status.DISMISSED,
                    ],
                    content__attribute=key,
                ).exists():
                    continue
                statement = _summary(source)
                initiative = record_entry(
                    project,
                    kind=CognitiveStateEntry.Kind.INITIATIVE,
                    content={
                        "attribute": key,
                        "value": {
                            "key": key.removeprefix("initiative:"),
                            "category": category,
                            "priority": priority,
                            "observation": statement,
                            "recommendation": rationale,
                            "source_entry_id": source.pk,
                            "source_attribute": source.content.get("attribute"),
                            "dismissible": True,
                            "authority": "NONE",
                        },
                    },
                    provenance={
                        "source_type": "INITIATIVE_ENGINE_STATE_DERIVATION",
                        "source_entry_id": source.pk,
                        "rule": category,
                    },
                    confidence=source.confidence,
                )
                record_entry(
                    project,
                    kind=CognitiveStateEntry.Kind.EVIDENCE,
                    content={
                        "evidence_type": "INITIATIVE_ENGINE_OBSERVATION",
                        "initiative_entry_id": initiative.pk,
                        "source_entry_id": source.pk,
                        "category": category,
                    },
                    provenance={
                        "source_type": "INITIATIVE_ENGINE_STATE_DERIVATION",
                        "initiative_entry_id": initiative.pk,
                        "source_entry_id": source.pk,
                    },
                    confidence=source.confidence,
                )
                active_count += 1
    return initiative_projection(project)


def dismiss_initiative(
    project: Project, *, initiative_entry_id: int, actor_id: str, reason: str
) -> list[dict[str, Any]]:
    """Dismiss an active initiative with an attributable Product Owner action."""
    normalized_actor = " ".join(actor_id.split())
    normalized_reason = " ".join(reason.split())
    if not normalized_actor or not normalized_reason:
        raise ValueError("INITIATIVE_DISMISSAL_CONTEXT_REQUIRED")
    try:
        state = project.cognitive_state
    except CognitiveState.DoesNotExist as exc:
        raise ValueError("INITIATIVE_UNAVAILABLE") from exc
    with transaction.atomic():
        entry = state.entries.select_for_update().filter(
            pk=initiative_entry_id,
            kind=CognitiveStateEntry.Kind.INITIATIVE,
            status=CognitiveStateEntry.Status.ACTIVE,
        ).first()
        if entry is None:
            raise ValueError("INITIATIVE_UNAVAILABLE")
        entry.status = CognitiveStateEntry.Status.DISMISSED
        entry.save(update_fields=["status", "updated_at"])
        record_entry(
            project,
            kind=CognitiveStateEntry.Kind.EVIDENCE,
            content={
                "evidence_type": "PRODUCT_OWNER_INITIATIVE_DISMISSAL",
                "initiative_entry_id": entry.pk,
                "reason": normalized_reason[:500],
            },
            provenance={
                "source_type": "PRODUCT_OWNER_INITIATIVE_DISMISSAL",
                "actor_type": "PRODUCT_OWNER",
                "actor_id": normalized_actor[:128],
            },
        )
    return initiative_projection(project, include_dismissed=True)

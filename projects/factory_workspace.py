"""Safe, read-only Cognitive State projections for the Factory Chat workspace."""

from __future__ import annotations

from collections.abc import Iterable

from .models import (
    CognitiveState,
    CognitiveStateEntry,
    FactoryMission,
    FactoryPlan,
    Project,
)


def _text(value: object) -> str:
    """Render structured state without exposing JSON or transcript content."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "; ".join(item for item in (_text(item) for item in value) if item)
    if isinstance(value, dict):
        return _text(value.get("value") or value.get("text") or value.get("summary"))
    return ""


def _label(content: dict[str, object]) -> str:
    attribute = _text(content.get("attribute"))
    return (
        attribute.replace("_", " ").capitalize()
        if attribute
        else "R\u00f6gz\u00edtett \u00e1llapot"
    )


def _entries(entries: Iterable[CognitiveStateEntry]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for entry in entries:
        text = _text(entry.content)
        if text:
            result.append(
                {
                    "label": _label(entry.content),
                    "text": text,
                    "confidence": entry.confidence,
                    "source": "Kanonikus Cognitive State",
                }
            )
    return result


def _fallback(values: object, label: str) -> list[dict[str, object]]:
    if not isinstance(values, list):
        values = [values]
    return [
        {
            "label": label,
            "text": text,
            "confidence": None,
            "source": "Mission projection",
        }
        for text in (_text(value) for value in values)
        if text
    ]


def cognitive_workspace_projection(
    project: Project,
    mission: FactoryMission | None,
    plan: FactoryPlan | None,
) -> dict[str, object]:
    """Return a project-isolated projection; GET requests never create state."""
    state = CognitiveState.objects.filter(project=project).first()
    active = (
        state.entries.filter(status=CognitiveStateEntry.Status.ACTIVE).order_by(
            "-created_at", "-pk"
        )
        if state
        else CognitiveStateEntry.objects.none()
    )

    def group(*kinds: str) -> list[dict[str, object]]:
        return _entries(active.filter(kind__in=kinds)[:4])

    plan_document = (
        plan.plan_document if plan and isinstance(plan.plan_document, dict) else {}
    )
    mission_items = group(CognitiveStateEntry.Kind.MISSION) or _fallback(
        [mission.objective, mission.primary_workflow] if mission else [], "Mission"
    )
    facts = group(
        CognitiveStateEntry.Kind.FACT,
        CognitiveStateEntry.Kind.BUSINESS_CONTEXT,
        CognitiveStateEntry.Kind.GOAL,
    )
    assumptions = group(CognitiveStateEntry.Kind.ASSUMPTION) or _fallback(
        mission.assumptions if mission else [], "Felt\u00e9telez\u00e9s"
    )
    decisions = group(CognitiveStateEntry.Kind.OPEN_DECISION) or _fallback(
        mission.unresolved_decisions if mission else [], "Nyitott d\u00f6nt\u00e9s"
    )
    recommendations = group(CognitiveStateEntry.Kind.RECOMMENDATION) or _fallback(
        mission.recommendations if mission else [], "Aj\u00e1nl\u00e1s"
    )
    alternatives = group(CognitiveStateEntry.Kind.ALTERNATIVE)
    plan_items = group(CognitiveStateEntry.Kind.PLAN) or _fallback(
        [plan_document.get("objective"), plan_document.get("mvp_boundary")], "Terv"
    )
    roadmap = _fallback(plan_document.get("roadmap", []), "Roadmap") or [
        {
            "label": "Roadmap",
            "text": item.title,
            "confidence": None,
            "source": "Project roadmap",
        }
        for item in project.roadmap_items.order_by("-updated_at")[:4]
    ]
    initiatives = group(CognitiveStateEntry.Kind.INITIATIVE)
    architecture = group(
        CognitiveStateEntry.Kind.ACCEPTED_DECISION,
        CognitiveStateEntry.Kind.CONSTRAINT,
    )
    next_step = (
        "N\u00e9zd \u00e1t a d\u00f6nt\u00e9si k\u00e1rty\u00e1t, \u00e9s "
        "csak akkor hagyd j\u00f3v\u00e1, ha megfelel."
        if plan and plan.status == FactoryPlan.Status.PENDING_APPROVAL
        else (
            "Folytasd term\u00e9szetes nyelven; Orki a kanonikus "
            "\u00e1llapotot friss\u00edti."
        )
    )
    documents = [
        ("Mission", mission_items),
        ("Goals", facts),
        ("Initiatives", initiatives),
        ("Architecture decisions", architecture),
        ("Plan", plan_items),
        ("Roadmap", roadmap),
    ]
    return {
        "has_state": state is not None,
        "mission": mission_items,
        "facts": facts,
        "assumptions": assumptions,
        "decisions": decisions,
        "recommendations": recommendations,
        "alternatives": alternatives,
        "plan": plan_items,
        "roadmap": roadmap,
        "initiatives": initiatives,
        "architecture": architecture,
        "next_step": next_step,
        "documents": [
            {
                "title": title,
                "items": items,
                "source": "Live Cognitive State projection",
            }
            for title, items in documents
            if items
        ],
    }


def approval_projection(
    workspace: dict[str, object], plan: FactoryPlan | None
) -> dict[str, object]:
    """Create an explainable approval card from existing canonical state."""
    document = (
        plan.plan_document if plan and isinstance(plan.plan_document, dict) else {}
    )
    return {
        "summary": _text(document.get("objective"))
        or "A terv c\u00e9lja a fenti mission megval\u00f3s\u00edt\u00e1sa.",
        "assumptions": workspace["assumptions"],
        "alternatives": workspace["alternatives"],
        "impact": _text(document.get("mvp_boundary"))
        or (
            "A v\u00e1rhat\u00f3 hat\u00e1s a tervben r\u00f6gz\u00edtett "
            "MVP-hat\u00e1r."
        ),
        "recommendations": workspace["recommendations"],
        "required_decision": (
            "J\u00f3v\u00e1hagyod-e ezt a tervet a megjelen\u00edtett "
            "felt\u00e9telez\u00e9sekkel?"
        ),
    }

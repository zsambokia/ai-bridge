"""Canonical COO mission state, plan projection, and delivery hand-off."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from django.db import transaction

from .models import FactoryChatSession, FactoryMission
from .orki_runtime import create_factory_plan_in_shadow

CONFIDENCE_THRESHOLD = 0.90
_TEXT_FIELDS = (
    "objective",
    "primary_workflow",
    "mvp_boundary",
    "persistence_requirements",
)
_LIST_FIELDS = (
    "target_users",
    "required_inputs",
    "required_outputs",
    "integrations",
    "cost_impacting_dependencies",
    "risks",
    "assumptions",
    "recommendations",
    "unresolved_decisions",
)

_CRITICAL_FIELDS: tuple[tuple[str, str], ...] = (
    ("objective", "Mi a pontos üzleti cél és az MVP sikerkritériuma?"),
    ("target_users", "Kik fogják használni a megoldást?"),
    ("primary_workflow", "Mi az elsődleges, lépésről lépésre végigvitt munkafolyamat?"),
    (
        "required_inputs",
        "Milyen bemenetek szükségesek (például térfogat, súly, konténertípus)?",
    ),
    ("required_outputs", "Milyen eredményt és megjelenítést vár a felhasználó?"),
    ("mvp_boundary", "Mi tartozik az MVP-be, és mi marad ki belőle?"),
    (
        "persistence_requirements",
        "Kell bejelentkezés, több felhasználó vagy tartós tárolás?",
    ),
)


def assess_mission_readiness(mission: FactoryMission) -> dict[str, object]:
    """Apply the Runtime-owned deterministic gate before Planning."""
    missing = [
        {"field": field, "question": question}
        for field, question in _CRITICAL_FIELDS
        if not getattr(mission, field)
    ]
    coverage = 1 - (len(missing) / len(_CRITICAL_FIELDS))
    confidence = min(mission.recommendation_confidence, coverage)
    ready = bool(
        confidence >= CONFIDENCE_THRESHOLD
        and not missing
        and not mission.unresolved_decisions
    )
    return {
        "confidence": confidence,
        "provider_confidence": mission.recommendation_confidence,
        "critical_unknowns": missing,
        "open_questions": list(mission.unresolved_decisions),
        "questions": [item["question"] for item in missing]
        + list(mission.unresolved_decisions),
        "ready_for_planning": ready,
    }


def mission_for(session: FactoryChatSession) -> FactoryMission:
    return FactoryMission.objects.get_or_create(session=session)[0]


def _strings(value: object) -> list[str]:
    return (
        [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, list)
        else []
    )


def apply_understanding(
    session: FactoryChatSession, data: Mapping[str, object], message: str
) -> FactoryMission:
    """Merge model understanding; canonical sufficiency is calculated locally."""
    mission = mission_for(session)
    for field in _TEXT_FIELDS:
        text_value = str(data.get(field, "")).strip()
        if text_value:
            setattr(mission, field, text_value[:2000])
    for field in _LIST_FIELDS:
        # An explicit empty list closes a previously raised question.  The
        # old truthy-only merge kept stale decisions indefinitely.
        if field in data:
            setattr(mission, field, _strings(data.get(field))[:30])
    confidence = data.get("recommendation_confidence")
    if isinstance(confidence, (int, float)):
        mission.recommendation_confidence = max(0.0, min(1.0, float(confidence)))
    proposal = data.get("repository_proposal")
    if isinstance(proposal, dict):
        mission.repository_proposal = proposal
    readiness = assess_mission_readiness(mission)
    readiness_confidence = readiness["confidence"]
    if not isinstance(readiness_confidence, (int, float)):
        raise TypeError("Mission readiness confidence must be numeric.")
    mission.recommendation_confidence = float(readiness_confidence)
    mission.requirements_sufficient = bool(readiness["ready_for_planning"])
    mission.delivery_status = {
        **mission.delivery_status,
        "understanding": readiness,
    }
    if mission.requirements_sufficient and mission.plan_id is None:
        mission.phase = FactoryMission.Phase.REQUIREMENTS_SUFFICIENT
    elif mission.plan_id is None:
        mission.phase = FactoryMission.Phase.QUESTION_REQUIRED
    mission.save()
    return mission


def plan_document(mission: FactoryMission) -> dict[str, object]:
    """Return a stable Product Owner artifact, never raw provider text."""
    return {
        "objective": mission.objective,
        "target_users": mission.target_users,
        "recommended_product_approach": mission.recommendations,
        "main_functions": mission.required_outputs or [mission.primary_workflow],
        "mvp_boundary": mission.mvp_boundary
        or "Az els\u0151, biztons\u00e1gosan sz\u00e1ll\u00edthat\u00f3 munkafolyamat.",
        "proposed_ux_flow": mission.primary_workflow,
        "persistence_approach": mission.persistence_requirements
        or "A term\u00e9k ig\u00e9nyeihez ill\u0151, tart\u00f3s t\u00e1rol\u00e1s.",
        "integrations": mission.integrations,
        "product_owner_architecture": (
            "Szerveroldali alkalmaz\u00e1s, "
            "elk\u00fcl\u00f6n\u00edtett integr\u00e1ci\u00f3s "
            "\u00e9s tesztel\u00e9si r\u00e9tegekkel."
        ),
        "roadmap": [
            "MVP",
            "Ellen\u0151rz\u00e9s \u00e9s finom\u00edt\u00e1s",
            "\u00c9les\u00edt\u00e9s el\u0151k\u00e9sz\u00edt\u00e9se",
        ],
        "sprint_proposal": [
            "Tervez\u00e9s \u00e9s alapok",
            "MVP megval\u00f3s\u00edt\u00e1s",
            "Elfogad\u00e1s \u00e9s kiad\u00e1s",
        ],
        "acceptance_criteria": mission.required_outputs
        or ["A f\u0151 munkafolyamat v\u00e9gigvihet\u0151."],
        "test_strategy": (
            "Backend, frontend \u00e9s val\u00f3s "
            "Chromium b\u00f6ng\u00e9sz\u0151teszt."
        ),
        "deployment_preview_approach": (
            "El\u0151n\u00e9zet \u00e9s m\u0171k\u00f6d\u00e9si "
            "ellen\u0151rz\u00e9s a sz\u00e1ll\u00edt\u00e1s el\u0151tt."
        ),
        "risks": mission.risks,
        "external_services": mission.integrations,
        "expected_costs": mission.cost_impacting_dependencies,
        "assumptions": mission.assumptions,
        "unresolved_product_owner_decisions": mission.unresolved_decisions,
        "repository_proposal": mission.repository_proposal,
        "after_approval": (
            "Orki l\u00e9trehozza vagy kapcsolja a repositoryt, "
            "majd auton\u00f3m m\u00f3don "
            "v\u00e9gigviszi a fejleszt\u00e9st \u00e9s az ellen\u0151rz\u00e9seket."
        ),
    }


def create_plan_when_sufficient(mission: FactoryMission, actor: str) -> FactoryMission:
    if (
        not mission.requirements_sufficient
        or mission.plan_id
        or mission.session.project_id is None
    ):
        return mission
    project = mission.session.project
    if project is None:
        return mission
    document = plan_document(mission)
    acceptance_criteria = document["acceptance_criteria"]
    checks = (
        "\n".join(str(value) for value in acceptance_criteria)
        if isinstance(acceptance_criteria, list)
        else "A fő munkafolyamat végigvihető."
    )
    with transaction.atomic():
        plan = create_factory_plan_in_shadow(
            project,
            {
                "outcome": mission.objective,
                "title": f"{project.display_name}: Orki terv",
                "technical_constraints": document["persistence_approach"],
                "acceptance_checks": checks,
                "risk_modifiers": "",
            },
            actor=actor,
            session=mission.session,
        )
        plan.plan_document = document
        plan.save(update_fields=["plan_document", "updated_at"])
        mission.plan = plan
        mission.phase = FactoryMission.Phase.AWAITING_PRODUCT_OWNER_APPROVAL
        mission.save(update_fields=["plan", "phase", "updated_at"])
    return mission


def begin_autonomous_delivery(mission: FactoryMission) -> FactoryMission:
    """Record the ownership transition; execution services resume from it."""
    mission.phase = FactoryMission.Phase.ORKI_OWNS_DELIVERY
    mission.delivery_status = {
        "state": "repository",
        "next": (
            "Repository el\u0151k\u00e9sz\u00edt\u00e9se "
            "\u00e9s a fejleszt\u00e9s ind\u00edt\u00e1sa."
        ),
    }
    mission.save(update_fields=["phase", "delivery_status", "updated_at"])
    return mission


def human_projection(mission: FactoryMission | None) -> dict[str, object]:
    if mission is None:
        return {
            "phase": "\u00d6tlet pontos\u00edt\u00e1sa",
            "understood": [],
            "recommendations": [],
            "missing": ["A c\u00e9l \u00e9s az els\u0151 munkafolyamat"],
            "next": "Mondd el, milyen eredm\u00e9nyt szeretn\u00e9l.",
            "decisions": [],
        }
    phases = {
        "DISCOVERY": "K\u00f6vetelm\u00e9nyek \u00f6sszegy\u0171jt\u00e9se",
        "QUESTION_REQUIRED": "Pontos\u00edt\u00e1sra v\u00e1r",
        "REQUIREMENTS_SUFFICIENT": "Terv k\u00e9sz\u00edt\u00e9se",
        "PLAN_READY": "Terv k\u00e9sz\u00edt\u00e9se",
        "AWAITING_PRODUCT_OWNER_APPROVAL": "J\u00f3v\u00e1hagy\u00e1sra v\u00e1r",
        "PLAN_APPROVED": "Repository l\u00e9trehoz\u00e1sa",
        "ORKI_OWNS_DELIVERY": "Fejleszt\u00e9s folyamatban",
        "IMPLEMENTING": "Fejleszt\u00e9s folyamatban",
        "VALIDATING": "Tesztel\u00e9s",
        "DELIVERED": "El\u0151n\u00e9zet elk\u00e9sz\u00fclt",
        "AWAITING_PRODUCT_OWNER_ACCEPTANCE": "Elfogad\u00e1sra v\u00e1r",
        "ACCEPTED": "Elfogadva",
    }
    understood = [
        item
        for item in [mission.objective, mission.primary_workflow, *mission.target_users]
        if item
    ]
    readiness = assess_mission_readiness(mission)
    readiness_questions = readiness["questions"]
    missing = (
        cast(list[str], readiness_questions)
        if isinstance(readiness_questions, list)
        else []
    )
    return {
        "phase": phases[mission.phase],
        "understood": understood,
        "recommendations": mission.recommendations,
        "missing": missing,
        "next": (mission.delivery_status or {}).get("next")
        or (
            "\u00c1tn\u00e9z\u00e9s \u00e9s egyszeri j\u00f3v\u00e1hagy\u00e1s."
            if mission.plan_id
            else "Orki a k\u00f6vetkez\u0151 l\u00e9nyeges k\u00e9rd\u00e9st teszi fel."
        ),
        "decisions": mission.unresolved_decisions,
    }

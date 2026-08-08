"""Sprint 03 canonical E2E: semantic context through a non-executing decision."""

from projects.reasoning import (
    BehaviourEngine,
    Planner,
    ReasoningFramework,
    SituationModel,
    UnderstandingEngine,
)
from projects.semantic import SemanticCandidate, SemanticContextV2


def _context(*, evidence: bool = True) -> SemanticContextV2:
    candidate = SemanticCandidate(
        1,
        0.9,
        "COSINE_SIMILARITY",
        {"title": "Logistics"},
        {"entry_id": 1},
        "container order package",
    )
    return SemanticContextV2(
        "Create a container utilisation application",
        {
            "repository_available": True,
            "project_available": True,
            "bootstrap_ready": True,
        },
        (candidate,) if evidence else (),
        candidate.content if evidence else "",
        (candidate.evidence,) if evidence else (),
    )


def test_canonical_reasoning_e2e_stops_at_structured_decision() -> None:
    decision = ReasoningFramework().decide(_context())
    assert decision.behaviour == "IMPLEMENTATION"
    assert decision.critic.passed is True
    assert decision.needs_user is False
    assert [task.identifier for task in decision.plan] == [
        "understand",
        "design",
        "verify",
    ]
    assert decision.evidence == ({"entry_id": 1},)


def test_reasoning_stages_produce_inspectable_artifacts() -> None:
    context = _context()
    understanding = UnderstandingEngine().understand(context)
    situation = SituationModel().analyse(context)
    behaviour = BehaviourEngine().select(understanding, situation)
    plan = Planner().plan(
        ReasoningFramework().reasoning.reason(context, understanding, behaviour),
        context.evidence,
    )

    assert understanding.domain == "logistics"
    assert situation.repository_available is True
    assert behaviour == "IMPLEMENTATION"
    assert plan[-1].depends_on == ("design",)


def test_critic_returns_feedback_for_missing_semantic_evidence() -> None:
    decision = ReasoningFramework().decide(_context(evidence=False))
    assert decision.critic.passed is False
    assert decision.needs_user is True
    assert decision.critic.observations == ("NO_SEMANTIC_EVIDENCE",)

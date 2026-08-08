"""Pure structured thinking from Semantic Context to a non-executable decision."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from projects.semantic import SemanticContextV2


@dataclass(frozen=True)
class Understanding:
    domain: str
    intent: str
    complexity: str
    confidence: float
    entities: tuple[str, ...]


@dataclass(frozen=True)
class Situation:
    repository_available: bool
    project_available: bool
    bootstrap_ready: bool
    knowledge_available: bool
    similar_examples_available: bool


@dataclass(frozen=True)
class ReasonedIntent:
    mission: str
    confidence: float
    rationale: str


@dataclass(frozen=True)
class CriticResult:
    passed: bool
    needs_user: bool
    observations: tuple[str, ...]


@dataclass(frozen=True)
class PlanTask:
    identifier: str
    title: str
    depends_on: tuple[str, ...]
    evidence: tuple[dict[str, Any], ...]
    expected_result: str


@dataclass(frozen=True)
class StructuredDecision:
    goal: str
    intent: str
    behaviour: str
    confidence: float
    plan: tuple[PlanTask, ...]
    needs_user: bool
    risk: str
    reasoning: str
    critic: CriticResult
    evidence: tuple[dict[str, Any], ...]


class UnderstandingEngine:
    """Extract a small, explainable meaning projection from semantic context."""

    _domains = {
        "logistics": {"container", "package", "order", "shipment", "warehouse"},
        "commerce": {"customer", "cart", "payment", "product", "order"},
        "engineering": {"repository", "api", "application", "service", "code"},
    }

    def understand(self, context: SemanticContextV2) -> Understanding:
        tokens = set(re.findall(r"[a-z0-9_]+", context.goal.lower()))
        domain, matches = max(
            (
                (name, len(tokens & vocabulary))
                for name, vocabulary in self._domains.items()
            ),
            key=lambda item: item[1],
        )
        entities = tuple(sorted(tokens & set().union(*self._domains.values())))
        intent = (
            "new_application"
            if tokens & {"build", "create", "make", "készíts"}
            else "analysis"
        )
        complexity = "medium" if len(tokens) >= 3 else "low"
        confidence = min(0.99, 0.65 + matches * 0.1 + bool(context.candidates) * 0.1)
        return Understanding(domain, intent, complexity, round(confidence, 2), entities)


class SituationModel:
    """Builds a factual state snapshot; it neither mutates nor authorizes state."""

    def analyse(self, context: SemanticContextV2) -> Situation:
        state = context.runtime_state
        return Situation(
            bool(state.get("repository_available")),
            bool(state.get("project_available")),
            bool(state.get("bootstrap_ready")),
            bool(context.candidates),
            bool(state.get("similar_examples_available")),
        )


class BehaviourEngine:
    """Selects a reasoning posture, never a Runtime action."""

    def select(self, understanding: Understanding, situation: Situation) -> str:
        if not situation.project_available:
            return "NEW_PROJECT"
        if not situation.repository_available:
            return "DISCOVERY"
        if understanding.intent == "new_application":
            return "IMPLEMENTATION"
        return "REVIEW"


class ReasoningEngine:
    """Produces an inspectable intent without calling a provider."""

    def reason(
        self, context: SemanticContextV2, understanding: Understanding, behaviour: str
    ) -> ReasonedIntent:
        mission = f"{behaviour}: {context.goal}"
        rationale = (
            f"domain={understanding.domain}; intent={understanding.intent}; "
            f"semantic_evidence={len(context.evidence)}"
        )
        return ReasonedIntent(mission, understanding.confidence, rationale)


class Critic:
    """Checks reasoning completeness and returns feedback only."""

    def review(self, intent: ReasonedIntent, situation: Situation) -> CriticResult:
        observations: list[str] = []
        if not situation.knowledge_available:
            observations.append("NO_SEMANTIC_EVIDENCE")
        if intent.confidence < 0.7:
            observations.append("LOW_CONFIDENCE")
        return CriticResult(not observations, bool(observations), tuple(observations))


class Planner:
    """Creates a non-executable task graph from reviewed reasoning."""

    def plan(
        self, intent: ReasonedIntent, evidence: tuple[dict[str, Any], ...]
    ) -> tuple[PlanTask, ...]:
        return (
            PlanTask(
                "understand",
                "Confirm mission understanding",
                (),
                evidence,
                intent.mission,
            ),
            PlanTask(
                "design",
                "Prepare bounded implementation plan",
                ("understand",),
                evidence,
                "Reviewed plan",
            ),
            PlanTask(
                "verify",
                "Define acceptance evidence",
                ("design",),
                evidence,
                "Verification criteria",
            ),
        )


class ReasoningFramework:
    """Canonical Sprint 03 pipeline; intentionally stops at StructuredDecision."""

    def __init__(self) -> None:
        self.understanding = UnderstandingEngine()
        self.situation = SituationModel()
        self.behaviour = BehaviourEngine()
        self.reasoning = ReasoningEngine()
        self.critic = Critic()
        self.planner = Planner()

    def decide(self, context: SemanticContextV2) -> StructuredDecision:
        understanding = self.understanding.understand(context)
        situation = self.situation.analyse(context)
        behaviour = self.behaviour.select(understanding, situation)
        intent = self.reasoning.reason(context, understanding, behaviour)
        critic = self.critic.review(intent, situation)
        return StructuredDecision(
            context.goal,
            understanding.intent,
            behaviour,
            intent.confidence,
            self.planner.plan(intent, context.evidence),
            critic.needs_user,
            "low" if critic.passed else "medium",
            intent.rationale,
            critic,
            context.evidence,
        )

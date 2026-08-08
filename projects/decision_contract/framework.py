"""Pure mapping, validation, and adaptation of the StructuredDecision v1 contract.

This module intentionally has no Django, Runtime, provider, queue, OESM, or
execution imports.  It creates an inspectable contract; it never executes it.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any
from uuid import UUID, uuid4

from projects.reasoning import StructuredDecision
from projects.semantic import SemanticContextV2

CONTRACT_VERSION = "StructuredDecision.v1"
_MIN_CONFIDENCE = 0.70


@dataclass(frozen=True)
class ConfidenceModel:
    overall: float
    semantic: float
    reasoning: float
    planning: float
    critic: float


@dataclass(frozen=True)
class DecisionPlanItem:
    identifier: str
    title: str
    depends_on: tuple[str, ...]
    expected_result: str


@dataclass(frozen=True)
class DecisionEvidence:
    knowledge_entry_ids: tuple[int, ...]
    embedding_hits: tuple[dict[str, Any], ...]
    behaviour: str
    plan_identifiers: tuple[str, ...]
    critic_observations: tuple[str, ...]


@dataclass(frozen=True)
class StructuredDecisionV1:
    decision_id: UUID
    contract_version: str
    goal: str
    intent: str
    behaviour: str
    confidence: ConfidenceModel
    plan: tuple[DecisionPlanItem, ...]
    required_capabilities: tuple[str, ...]
    required_tools: tuple[str, ...]
    required_workflows: tuple[str, ...]
    risk_level: str
    needs_user_input: bool
    reasoning_summary: str
    critic_summary: str
    evidence: DecisionEvidence

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["decision_id"] = str(self.decision_id)
        return payload


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]

    @property
    def feedback(self) -> str:
        return "; ".join(self.errors)


@dataclass(frozen=True)
class ExecutionRequest:
    """Runtime-facing projection only; it deliberately has no dispatch method."""

    contract_version: str
    decision_id: UUID
    goal: str
    plan: tuple[DecisionPlanItem, ...]
    required_capabilities: tuple[str, ...]
    required_tools: tuple[str, ...]
    required_workflows: tuple[str, ...]
    evidence: DecisionEvidence


class StructuredDecisionBuilder:
    """Maps the private Sprint 03 output to the public v1 contract."""

    def build(
        self,
        decision: StructuredDecision,
        context: SemanticContextV2,
        *,
        required_capabilities: tuple[str, ...],
        required_tools: tuple[str, ...] = (),
        required_workflows: tuple[str, ...] = (),
        decision_id: UUID | None = None,
    ) -> StructuredDecisionV1:
        semantic = max((item.score for item in context.candidates), default=0.0)
        planning = decision.confidence if decision.plan else 0.0
        critic = 1.0 if decision.critic.passed else 0.0
        confidence = ConfidenceModel(
            overall=round((semantic + decision.confidence + planning + critic) / 4, 3),
            semantic=round(semantic, 3),
            reasoning=decision.confidence,
            planning=round(planning, 3),
            critic=critic,
        )
        plan = tuple(
            DecisionPlanItem(
                item.identifier, item.title, item.depends_on, item.expected_result
            )
            for item in decision.plan
        )
        evidence = DecisionEvidence(
            knowledge_entry_ids=tuple(item.entry_id for item in context.candidates),
            embedding_hits=tuple(
                {
                    "entry_id": item.entry_id,
                    "score": item.score,
                    "reason": item.reason,
                    "embedding": item.evidence,
                }
                for item in context.candidates
            ),
            behaviour=decision.behaviour,
            plan_identifiers=tuple(item.identifier for item in plan),
            critic_observations=decision.critic.observations,
        )
        return StructuredDecisionV1(
            decision_id or uuid4(),
            CONTRACT_VERSION,
            decision.goal,
            decision.intent,
            decision.behaviour,
            confidence,
            plan,
            required_capabilities,
            required_tools,
            required_workflows,
            decision.risk.upper(),
            decision.needs_user,
            decision.reasoning,
            "; ".join(decision.critic.observations) or "CRITIC_PASS",
            evidence,
        )


class DecisionValidator:
    """Returns repair feedback to Reasoning; it never chooses or executes work."""

    def validate(self, decision: StructuredDecisionV1) -> ValidationResult:
        errors: list[str] = []
        if decision.contract_version != CONTRACT_VERSION:
            errors.append("INVALID_CONTRACT_VERSION")
        if not decision.goal.strip():
            errors.append("MISSING_GOAL")
        if not decision.intent.strip() or not decision.behaviour.strip():
            errors.append("MISSING_DECISION_MEANING")
        if not decision.plan:
            errors.append("MISSING_PLAN")
        if not decision.required_capabilities:
            errors.append("MISSING_CAPABILITIES")
        if (
            not decision.evidence.knowledge_entry_ids
            or not decision.evidence.embedding_hits
        ):
            errors.append("MISSING_EVIDENCE")
        if decision.evidence.behaviour != decision.behaviour:
            errors.append("INCONSISTENT_EVIDENCE_BEHAVIOUR")
        if decision.evidence.plan_identifiers != tuple(
            item.identifier for item in decision.plan
        ):
            errors.append("INCONSISTENT_EVIDENCE_PLAN")
        confidence_values = asdict(decision.confidence).values()
        if any(not 0.0 <= float(value) <= 1.0 for value in confidence_values):
            errors.append("INVALID_CONFIDENCE_RANGE")
        if decision.confidence.overall < _MIN_CONFIDENCE:
            errors.append("LOW_CONFIDENCE")
        if decision.needs_user_input and decision.risk_level == "LOW":
            errors.append("INCONSISTENT_RISK_LEVEL")
        return ValidationResult(not errors, tuple(errors))


def to_execution_request(
    decision: StructuredDecisionV1, validation: ValidationResult
) -> ExecutionRequest:
    """Create the only Runtime projection after explicit contract validation."""
    if not validation.valid:
        raise ValueError(f"DECISION_CONTRACT_INVALID:{validation.feedback}")
    return ExecutionRequest(
        decision.contract_version,
        decision.decision_id,
        decision.goal,
        decision.plan,
        decision.required_capabilities,
        decision.required_tools,
        decision.required_workflows,
        decision.evidence,
    )

"""Provider-neutral, deterministic orchestration foundation.

Model output is an untrusted recommendation.  This module validates it and
applies policy; it deliberately contains no shell or execution dispatch path.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from django.db import IntegrityError, transaction

from .models import OrchestrationDecision, OrchestrationSession, Project
from .orchestration_context import bind, for_session


class AuthorityClassification(StrEnum):
    ENGINEERING = "ENGINEERING"
    BUSINESS = "BUSINESS"
    MIXED = "MIXED"
    UNSAFE = "UNSAFE"
    UNKNOWN = "UNKNOWN"


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    REQUIRE_PRODUCT_OWNER = "REQUIRE_PRODUCT_OWNER"
    DENY = "DENY"
    REQUIRE_MORE_EVIDENCE = "REQUIRE_MORE_EVIDENCE"


class RecommendedAction(StrEnum):
    CREATE_TECHNICAL_WORK_ITEM = "CREATE_TECHNICAL_WORK_ITEM"
    REQUEST_PRODUCT_OWNER_DECISION = "REQUEST_PRODUCT_OWNER_DECISION"
    COLLECT_MORE_EVIDENCE = "COLLECT_MORE_EVIDENCE"
    NO_ACTION = "NO_ACTION"


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    rule_ids: list[str]
    reason: str


def evaluate_policy(payload: dict[str, Any]) -> PolicyResult:
    """Fail closed independently of the provider's suggested action."""
    classification = AuthorityClassification(payload["authority_classification"])
    flags = set(payload.get("risk_flags", []))
    if flags & {"SECURITY", "PRIVACY", "IRREVERSIBLE", "PRODUCTION", "CROSS_PROJECT"}:
        return PolicyResult(
            PolicyDecision.DENY,
            ["AUTH-UNSAFE-001"],
            "Excluded risk requires separate authority.",
        )
    if classification == AuthorityClassification.BUSINESS:
        return PolicyResult(
            PolicyDecision.REQUIRE_PRODUCT_OWNER,
            ["AUTH-BUSINESS-001"],
            "Business authority is reserved to the Product Owner.",
        )
    if classification in {
        AuthorityClassification.MIXED,
        AuthorityClassification.UNSAFE,
    }:
        return PolicyResult(
            PolicyDecision.REQUIRE_PRODUCT_OWNER,
            ["AUTH-MIXED-001"],
            "Mixed or unsafe scope fails closed.",
        )
    if classification == AuthorityClassification.UNKNOWN:
        return PolicyResult(
            PolicyDecision.REQUIRE_MORE_EVIDENCE,
            ["AUTH-UNKNOWN-001"],
            "Authority is not established.",
        )
    if any(
        candidate["confidence"] < 0.8 for candidate in payload["root_cause_candidates"]
    ):
        return PolicyResult(
            PolicyDecision.REQUIRE_MORE_EVIDENCE,
            ["AUTH-CONFIDENCE-001"],
            "Ownership/cause confidence is below 0.80.",
        )
    return PolicyResult(
        PolicyDecision.ALLOW,
        ["AUTH-ENGINEERING-001"],
        "Bounded technical assessment may continue through governance.",
    )


def validate_response(
    raw: dict[str, Any], session_id: str, *, repository: str | None = None
) -> dict[str, Any]:
    required = {
        "schema_version",
        "orchestration_id",
        "summary",
        "material_facts",
        "root_cause_candidates",
        "authority_classification",
        "recommended_action",
        "risk_flags",
        "required_policy_checks",
    }
    if set(raw) - (
        required | {"incident_id", "product_owner_question"}
    ) or not required.issubset(raw):
        raise ValueError("ORCHESTRATOR_SCHEMA_INVALID")
    if raw["schema_version"] != "1.0" or raw["orchestration_id"] != session_id:
        raise ValueError("ORCHESTRATOR_SCHEMA_INVALID")
    try:
        AuthorityClassification(raw["authority_classification"])
        RecommendedAction(raw["recommended_action"])
    except ValueError as exc:
        raise ValueError("ORCHESTRATOR_ENUM_INVALID") from exc
    if not isinstance(raw["summary"], str) or len(raw["summary"]) > 1000:
        raise ValueError("ORCHESTRATOR_SCHEMA_INVALID")
    if not isinstance(raw["material_facts"], list) or not isinstance(
        raw["root_cause_candidates"], list
    ):
        raise ValueError("ORCHESTRATOR_SCHEMA_INVALID")
    for item in [*raw["material_facts"], *raw["root_cause_candidates"]]:
        if not isinstance(item, dict) or not item.get("evidence_references"):
            raise ValueError("ORCHESTRATOR_EVIDENCE_REQUIRED")
    for candidate in raw["root_cause_candidates"]:
        if not all(candidate.get(key) for key in ("repository", "component", "cause")):
            raise ValueError("ORCHESTRATOR_ROOT_CAUSE_INVALID")
        if (
            not isinstance(candidate.get("confidence"), (int, float))
            or not 0 <= candidate["confidence"] <= 1
        ):
            raise ValueError("ORCHESTRATOR_CONFIDENCE_INVALID")
        if repository is not None and candidate["repository"] != repository:
            raise ValueError("ORCHESTRATOR_CONTEXT_PROJECT_MISMATCH")
    return raw


class OrchestratorProvider(Protocol):
    provider_id: str

    def assess(
        self, context: dict[str, Any], correlation_id: str
    ) -> dict[str, Any]: ...


@dataclass
class FakeOrchestratorProvider:
    response: dict[str, Any]
    provider_id: str = "fake-orchestrator"
    calls: int = 0

    def assess(self, context: dict[str, Any], correlation_id: str) -> dict[str, Any]:
        self.calls += 1
        response = json.loads(json.dumps(self.response))
        if response.get("orchestration_id") == "$SESSION":
            response["orchestration_id"] = context["orchestration_id"]
        return response


@dataclass
class OrchestratorProviderRegistry:
    providers: dict[str, OrchestratorProvider] = field(default_factory=dict)

    def register(self, provider: OrchestratorProvider) -> None:
        self.providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> OrchestratorProvider:
        try:
            return self.providers[provider_id]
        except KeyError as exc:
            raise ValueError("ORCHESTRATOR_PROVIDER_UNAVAILABLE") from exc


def build_context(
    project: Project, summary: str, orchestration_id: str
) -> dict[str, Any]:
    """Bounded normalized context; repository content, logs and secrets are excluded."""
    context = bind(project, f"orchestration:{orchestration_id}")
    return {
        **context.as_dict(),
        "project_id": project.project_id,
        "repository": project.repository_full_name,
        "summary": summary[:500],
        "schema_version": "1.0",
        "orchestration_id": orchestration_id,
        "allowed_actions": [x.value for x in RecommendedAction],
        "prohibited": ["shell_commands", "secrets", "repository_contents"],
    }


def assess(
    project: Project, summary: str, idempotency_key: str, provider: OrchestratorProvider
) -> OrchestrationSession:
    """Persist exactly one decision for an idempotency key; never dispatch it."""
    try:
        existing = OrchestrationSession.objects.get(idempotency_key=idempotency_key)
        if existing.project_id != project.pk:
            raise ValueError("ORCHESTRATION_IDEMPOTENCY_CONFLICT")
        for_session(existing)
        return existing
    except OrchestrationSession.DoesNotExist:
        pass
    correlation_id = str(uuid.uuid4())
    try:
        with transaction.atomic():
            session = OrchestrationSession.objects.create(
                project=project,
                idempotency_key=idempotency_key,
                provider_id=provider.provider_id,
                request_summary=summary[:500],
                correlation_id=correlation_id,
            )
    except IntegrityError:
        existing = OrchestrationSession.objects.get(idempotency_key=idempotency_key)
        if existing.project_id != project.pk:
            raise ValueError("ORCHESTRATION_IDEMPOTENCY_CONFLICT")
        for_session(existing)
        return existing
    context_error: ValueError | None = None
    try:
        for_session(session)
        raw = provider.assess(
            build_context(project, summary, str(session.token)), session.correlation_id
        )
        payload = validate_response(
            raw, str(session.token), repository=project.repository_full_name
        )
        policy = evaluate_policy(payload)
        evidence = sorted(
            {
                ref
                for item in [
                    *payload["material_facts"],
                    *payload["root_cause_candidates"],
                ]
                for ref in item["evidence_references"]
            }
        )[:20]
        OrchestrationDecision.objects.create(
            session=session,
            schema_version="1.0",
            authority_classification=payload["authority_classification"],
            policy_decision=policy.decision,
            recommended_action=payload["recommended_action"],
            rationale=payload["summary"],
            evidence_references=evidence,
            risk_flags=payload["risk_flags"][:20],
            policy_rule_ids=policy.rule_ids,
            product_owner_question=str(payload.get("product_owner_question", ""))[:500],
        )
        session.status = OrchestrationSession.Status.COMPLETED
    except (ValueError, RuntimeError) as error:
        session.status = OrchestrationSession.Status.FAILED
        if isinstance(error, ValueError) and str(error).startswith(
            "ORCHESTRATOR_CONTEXT_"
        ):
            context_error = error
    session.version += 1
    session.save(update_fields=["status", "version", "updated_at"])
    if context_error is not None:
        raise context_error
    return session

"""The fail-closed Orki gate for normal conversational execution.

This module deliberately makes no provider call and never dispatches work.  It
turns the already-confirmed conversational request into durable, reviewable
ownership and authority records before the canonical contract is generated.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import IntegrityError, transaction

from .knowledge import (
    build_and_record_context_package,
    context_package,
    record_context_use,
)
from .models import (
    ConversationOrchestration,
    ExecutionContract,
    KnowledgeContextUse,
    OrchestrationDecision,
    OrchestrationSession,
    OwnershipAssessment,
    Project,
)
from .orchestrator import (
    AuthorityClassification,
    PolicyDecision,
    RecommendedAction,
    evaluate_policy,
)

GATE_PROVIDER_ID = "orki-governance-gate-v1"


def _hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _ownership(
    project: Project, summary: str
) -> tuple[Project | None, float, str, list[dict[str, Any]], list[str]]:
    """Resolve only registered repository mentions; ambiguity stays fail-closed."""
    text = summary.lower()
    matches = list(
        Project.objects.filter(lifecycle=Project.Lifecycle.ACTIVE).order_by(
            "project_id"
        )
    )

    def is_mentioned(item: Project) -> bool:
        # A caller can use either the registered repository, project ID, or
        # display name.  These are registered Project facts, never inferred
        # from a branch, workspace, or filesystem path.
        identifiers = (
            item.repository_full_name,
            item.project_id,
            item.display_name,
        )
        return any(
            identifier and identifier.lower() in text for identifier in identifiers
        )

    mentioned = [item for item in matches if is_mentioned(item)]
    candidates = [
        {
            "project_id": item.project_id,
            "repository": item.repository_full_name,
            "confidence": 1.0 if item == project else 0.0,
            "evidence": "project-registry",
        }
        for item in (mentioned or [project])
    ]
    if len(mentioned) > 1:
        return (
            None,
            0.0,
            "Multiple registered repositories are mentioned.",
            candidates,
            ["AMBIGUOUS_OWNERSHIP"],
        )
    if mentioned and mentioned[0] != project:
        return (
            mentioned[0],
            1.0,
            "Request names a different registered repository.",
            candidates,
            ["CROSS_PROJECT"],
        )
    return (
        project,
        1.0,
        "Confirmed scope is bound to the selected Project registry record.",
        candidates,
        [],
    )


def open_gate(flow: ConversationOrchestration, caller: str) -> OrchestrationSession:
    """Create exactly one durable Orki decision for a conversation confirmation."""
    project = flow.scope.project
    key = f"conversation-orki:{flow.token}"
    try:
        existing = OrchestrationSession.objects.get(idempotency_key=key)
        if existing.project_id != project.pk:
            raise ValueError("ORCHESTRATION_IDEMPOTENCY_CONFLICT")
        return existing
    except OrchestrationSession.DoesNotExist:
        pass
    with transaction.atomic():
        try:
            session = OrchestrationSession.objects.create(
                project=project,
                idempotency_key=key,
                provider_id=GATE_PROVIDER_ID,
                request_summary=flow.scope.record["intent"][:500],
                correlation_id=f"conversation:{flow.token}",
                actor_identity=flow.product_owner_identity or caller,
            )
        except IntegrityError:
            return OrchestrationSession.objects.get(idempotency_key=key)
        package = build_and_record_context_package(
            project,
            f"conversation:{flow.token}",
            "ENGINEERING",
            retrieval_intent="conversation-confirmation",
            retrieval_query=session.request_summary,
        )
        selected, confidence, reason, candidates, risks = _ownership(
            project, session.request_summary
        )
        assessment = OwnershipAssessment.objects.create(
            session=session,
            selected_project=selected,
            confidence=confidence,
            policy_decision=PolicyDecision.ALLOW if not risks else PolicyDecision.DENY,
            reason=reason,
            candidates=candidates,
        )
        classification = AuthorityClassification.ENGINEERING
        lowered = session.request_summary.lower()
        if "AMBIGUOUS_OWNERSHIP" in risks:
            # Never select the conversation's initial project as a convenient
            # default when the request names several registered projects.
            classification = AuthorityClassification.MIXED
        elif any(
            marker in lowered
            for marker in ("pricing", "commercial", "business decision")
        ):
            classification = AuthorityClassification.BUSINESS
        policy = evaluate_policy(
            {
                "authority_classification": classification,
                "risk_flags": risks,
                "root_cause_candidates": [{"confidence": confidence}],
            }
        )
        decision = OrchestrationDecision.objects.create(
            session=session,
            schema_version="1.0",
            authority_classification=classification,
            policy_decision=policy.decision,
            recommended_action=(
                RecommendedAction.CREATE_TECHNICAL_WORK_ITEM
                if policy.decision == PolicyDecision.ALLOW
                else RecommendedAction.REQUEST_PRODUCT_OWNER_DECISION
            ),
            rationale=policy.reason,
            evidence_references=[
                f"project:{project.project_id}",
                f"repository:{project.repository_full_name}",
                f"scope:{flow.scope.identifier}",
                f"ownership:{assessment.pk}",
            ],
            risk_flags=risks,
            policy_rule_ids=policy.rule_ids,
            product_owner_question=(
                "Resolve ownership or authority before execution."
                if policy.decision != PolicyDecision.ALLOW
                else ""
            ),
        )
        record_context_use(package["package_id"], session=session, decision=decision)
        assessment.policy_decision = policy.decision
        assessment.save(update_fields=["policy_decision", "updated_at"])
        decision_hash = _hash(
            {
                "session": str(session.token),
                "project": project.project_id,
                "repository": project.repository_full_name,
                "context_package_hash": package["hash"],
                "ownership": assessment.pk,
                "authority": decision.authority_classification,
                "policy": decision.policy_decision,
                "rules": decision.policy_rule_ids,
            }
        )
        session.context_package_hash = package["hash"]
        session.context_entry_ids = package["entry_ids"]
        session.decision_hash = decision_hash
        session.final_outcome = decision.policy_decision
        session.status = OrchestrationSession.Status.COMPLETED
        session.save(
            update_fields=[
                "context_package_hash",
                "context_entry_ids",
                "decision_hash",
                "final_outcome",
                "status",
                "updated_at",
            ]
        )
        return session


def bind_runtime(session: OrchestrationSession, contract: ExecutionContract) -> None:
    """Persist the selected provider/runtime from the hash-bound contract."""
    session.execution_provider_id = contract.payload["provider_policy"][
        "selected_provider_identity"
    ]
    session.runtime_profile_hash = _hash(
        {
            "repository": contract.payload["project"]["repository"],
            "branch": contract.payload["execution"]["target_branch"],
        }
    )
    session.save(
        update_fields=["execution_provider_id", "runtime_profile_hash", "updated_at"]
    )
    if isinstance(contract, ExecutionContract):
        try:
            context_use = session.knowledge_context_use
        except KnowledgeContextUse.DoesNotExist:
            # A Sprint 2 session predates durable Context Package use.
            return
        context_use.execution_contract = contract
        context_use.save(update_fields=["execution_contract"])


def assert_contract_authorized(contract: ExecutionContract) -> OrchestrationSession:
    """Verify the decision/context/Project binding before normal dispatch."""
    session = contract.orchestration_session
    if session is None:
        raise ValueError("ORCHESTRATION_GATE_REQUIRED")
    if (
        session.status != OrchestrationSession.Status.COMPLETED
        or not session.context_package_hash
        or not session.decision_hash
        or contract.orchestration_decision_hash != session.decision_hash
        or session.project_id != contract.project_id
    ):
        raise ValueError("ORCHESTRATION_DECISION_INVALID")
    binding = contract.payload.get("orchestration", {})
    expected_context = context_package(
        session.project,
        session.correlation_id,
        "ENGINEERING",
        retrieval_intent="conversation-confirmation",
        retrieval_query=session.request_summary,
    )["hash"]
    if (
        binding.get("session_token") != str(session.token)
        or binding.get("context_package_hash") != session.context_package_hash
        or binding.get("context_package_hash") != expected_context
        or binding.get("decision_hash") != session.decision_hash
        or contract.payload["project"]["repository"]
        != session.project.repository_full_name
        or (
            session.execution_provider_id
            and contract.payload["provider_policy"]["selected_provider_identity"]
            != session.execution_provider_id
        )
    ):
        raise ValueError("ORCHESTRATION_BINDING_MISMATCH")
    try:
        decision = session.decision
        assessment = session.ownership_assessment
    except (
        OrchestrationDecision.DoesNotExist,
        OwnershipAssessment.DoesNotExist,
    ) as exc:
        raise ValueError("ORCHESTRATION_DECISION_INVALID") from exc
    if (
        decision.policy_decision != PolicyDecision.ALLOW
        or assessment.selected_project_id != contract.project_id
        or assessment.confidence < 0.8
    ):
        raise ValueError("ORCHESTRATION_AUTHORITY_DENIED")
    return session


def trace_for_contract(contract: ExecutionContract) -> dict[str, Any]:
    """One bounded public trace shared by MCP/API and Admin projections."""
    session = assert_contract_authorized(contract)
    decision = session.decision
    assessment = session.ownership_assessment
    try:
        context_use = session.knowledge_context_use
    except KnowledgeContextUse.DoesNotExist:
        context_use = None
    return {
        "session_token": str(session.token),
        "actor_identity": session.actor_identity,
        "project_id": session.project.project_id,
        "repository": session.project.repository_full_name,
        "ownership_assessment_id": assessment.pk,
        "ownership_confidence": assessment.confidence,
        "authority_classification": decision.authority_classification,
        "policy_decision": decision.policy_decision,
        "context_package_hash": session.context_package_hash,
        "context_package_id": context_use.package_id if context_use else None,
        "context_source_versions": (
            context_use.package.source_versions if context_use else {}
        ),
        "context_stale_warnings": (
            context_use.package.stale_warnings if context_use else []
        ),
        "context_conflict_warnings": (
            context_use.package.conflict_warnings if context_use else []
        ),
        "decision_hash": session.decision_hash,
        "provider": session.execution_provider_id,
        "runtime_profile_hash": session.runtime_profile_hash,
        "final_outcome": session.final_outcome,
    }

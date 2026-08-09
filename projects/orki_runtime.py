"""Provider-neutral Orki Runtime coordinator and persisted OESM transitions.

This module owns only Runtime coordination.  GovernanceApproval, ExecutableScope,
ExecutionContract and ExecutionRun retain their existing owners and semantics.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from typing import Any, cast

from django.db import transaction
from django.utils import timezone

from .decision_contract.framework import CONTRACT_VERSION, ExecutionRequest
from .factory_planning import approve_plan, create_plan
from .models import (
    CognitiveStateEntry,
    FactoryChatMessage,
    FactoryChatSession,
    FactoryMission,
    FactoryPlan,
    OrkiExecution,
    OrkiGoal,
    OrkiPlan,
    OrkiReflection,
    OrkiRuntimeEvent,
    Project,
    RuntimeKnowledgeCandidate,
    RuntimeReflectionCandidate,
)
from .runtime_contract import (
    RUNTIME_CANDIDATE_SCHEMA_VERSION,
    RuntimeCandidateValidationError,
    RuntimeKnowledgeCandidateValidator,
    RuntimeReflectionCandidateValidator,
)
from .providers import model_adapter_for, model_text_response
from .workflow_engine import (
    ProviderTaskError,
    WorkflowTaskFailure,
    create_workflow_candidate,
    execute_chat_provider_task,
    execute_task_adapter,
)


class RuntimeTransitionError(ValueError):
    """Raised when a caller attempts an invalid Runtime lifecycle transition."""


_TRANSITIONS: dict[str, set[str]] = {
    OrkiExecution.State.CREATED: {
        OrkiExecution.State.PLANNING,
        OrkiExecution.State.UNDERSTANDING,
    },
    OrkiExecution.State.UNDERSTANDING: {
        OrkiExecution.State.SEMANTIC_SEARCH,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.SEMANTIC_SEARCH: {
        OrkiExecution.State.DISPATCHING,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.GAP_ANALYSIS: {
        OrkiExecution.State.QUESTION_GENERATION,
        OrkiExecution.State.PLANNING,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.QUESTION_GENERATION: {
        OrkiExecution.State.WAITING_USER,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.WAITING_USER: {
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.PLANNING: {
        OrkiExecution.State.READY,
        OrkiExecution.State.WAITING_APPROVAL,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.DISPATCHING,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.WAITING_APPROVAL: {
        OrkiExecution.State.WAITING_GOVERNANCE,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.WAITING_GOVERNANCE: {
        OrkiExecution.State.DISPATCHING,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.DISPATCHING: {
        OrkiExecution.State.RUNNING,
        OrkiExecution.State.GAP_ANALYSIS,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.FAILED,
    },
    OrkiExecution.State.RUNNING: {
        OrkiExecution.State.WAITING,
        OrkiExecution.State.VERIFYING,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.WAITING_FOR_USER,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.FAILED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.VERIFYING: {
        OrkiExecution.State.REFLECTING,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.FAILED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.REFLECTING: {
        OrkiExecution.State.KNOWLEDGE_CANDIDATE,
        OrkiExecution.State.KNOWLEDGE_INTEGRATING,
        OrkiExecution.State.COMPLETED,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.KNOWLEDGE_INTEGRATING: {
        OrkiExecution.State.COMPLETED,
        OrkiExecution.State.WAITING_EXTERNAL,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.WAITING_EXTERNAL: {
        OrkiExecution.State.PLANNING,
        OrkiExecution.State.SEMANTIC_SEARCH,
        OrkiExecution.State.DISPATCHING,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.WAITING_FOR_USER: {
        OrkiExecution.State.RUNNING,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.PAUSED: set(),  # Resume restores the recorded prior state.
    OrkiExecution.State.READY: {
        OrkiExecution.State.RUNNING,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.WAITING: {
        OrkiExecution.State.RUNNING,
        OrkiExecution.State.PAUSED,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.RETRYING: {
        OrkiExecution.State.RUNNING,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.RECOVERY: {
        OrkiExecution.State.RETRYING,
        OrkiExecution.State.CANCELLED,
    },
    OrkiExecution.State.KNOWLEDGE_CANDIDATE: {OrkiExecution.State.COMPLETED},
    OrkiExecution.State.SUCCEEDED: set(),
    OrkiExecution.State.COMPLETED: set(),
    OrkiExecution.State.FAILED: {OrkiExecution.State.RECOVERY},
    OrkiExecution.State.CANCELLED: set(),
}


def _event(
    execution: OrkiExecution,
    event_type: str,
    *,
    actor: str = "",
    payload: Mapping[str, object] | None = None,
    evidence_references: list[str] | None = None,
) -> OrkiRuntimeEvent:
    """Append one event while the execution row is locked by the caller."""
    return OrkiRuntimeEvent.objects.create(
        execution=execution,
        sequence=execution.events.count() + 1,
        event_type=event_type,
        actor_identity=actor,
        payload=dict(payload or {}),
        evidence_references=list(
            evidence_references or [f"runtime-execution:{execution.token}"]
        ),
    )


def _transition(
    execution: OrkiExecution,
    target: str,
    *,
    actor: str = "",
    reason: Mapping[str, object] | None = None,
    event_type: str = "STATE_TRANSITION",
) -> OrkiExecution:
    """Move the locked execution through the canonical OESM graph and audit it."""
    current = execution.state
    if target not in _TRANSITIONS[current]:
        raise RuntimeTransitionError(f"RUNTIME_TRANSITION_FORBIDDEN:{current}:{target}")
    execution.state = target
    execution.state_version += 1
    execution.waiting_reason = dict(reason or {})
    execution.save(
        update_fields=["state", "state_version", "waiting_reason", "updated_at"]
    )
    _event(
        execution,
        event_type,
        actor=actor,
        payload={"from": current, "to": target, "reason": dict(reason or {})},
    )
    return execution


def _runtime_plan(factory_plan: FactoryPlan) -> OrkiPlan | None:
    return (
        OrkiPlan.objects.select_related("goal")
        .filter(factory_plan=factory_plan)
        .order_by("-created_at")
        .first()
    )


def start_shadow_for_factory_plan(
    factory_plan: FactoryPlan,
    *,
    actor: str,
    session: FactoryChatSession | None = None,
) -> OrkiExecution:
    """Create the Runtime trail for a Factory Plan without invoking governance.

    Shadow Mode is deliberately observational: it proves the exact intended
    handoff and records all lifecycle decisions, but never creates a contract,
    ExecutionRun, job, queue entry or provider invocation.
    """
    with transaction.atomic():
        factory_plan = (
            FactoryPlan.objects.select_for_update()
            .select_related("scope")
            .get(pk=factory_plan.pk)
        )
        existing = _runtime_plan(factory_plan)
        if existing:
            execution = existing.executions.order_by("-created_at").first()
            if execution:
                return execution
        goal = OrkiGoal.objects.create(
            project=factory_plan.project,
            source_session=session,
            intent_reference={
                "factory_plan_id": factory_plan.pk,
                "scope_identifier": factory_plan.scope.identifier,
            },
        )
        runtime_plan = OrkiPlan.objects.create(
            goal=goal,
            version=1,
            factory_plan=factory_plan,
            plan_hash=factory_plan.plan_hash,
            strategy_references={
                "scope_identifier": factory_plan.scope.identifier,
                "factory_plan_id": factory_plan.pk,
                # Derived from the approved plan artifact, never from a
                # hard-coded execution recipe.  Later planners may replace
                # this with richer semantic task decomposition.
                "mission_graph": [
                    {
                        "mission_id": f"acceptance-{index}",
                        "expected_outcome": check,
                    }
                    for index, check in enumerate(
                        factory_plan.questionnaire.get("acceptance_checks", []), start=1
                    )
                ],
            },
            status=OrkiPlan.Status.SELECTED,
        )
        execution = OrkiExecution.objects.create(
            plan=runtime_plan, mode=OrkiExecution.Mode.SHADOW
        )
        _event(
            execution,
            "EXECUTION_CREATED",
            actor=actor,
            payload={"mode": execution.mode, "plan_hash": runtime_plan.plan_hash},
            evidence_references=[factory_plan.scope.identifier],
        )
        _event(execution, "PLAN_SELECTED", actor=actor, payload={"version": 1})
        _transition(execution, OrkiExecution.State.PLANNING, actor=actor)
        if factory_plan.status == FactoryPlan.Status.APPROVED:
            _transition(
                execution,
                OrkiExecution.State.WAITING_APPROVAL,
                actor=actor,
                reason={"approval": "observed after runtime creation"},
            )
            _observe_approval_locked(execution, factory_plan, actor=actor)
        elif factory_plan.status == FactoryPlan.Status.PENDING_APPROVAL:
            _transition(
                execution,
                OrkiExecution.State.WAITING_APPROVAL,
                actor=actor,
                reason={"factory_plan_id": factory_plan.pk},
            )
        else:
            _transition(
                execution,
                OrkiExecution.State.WAITING_EXTERNAL,
                actor=actor,
                reason={"factory_plan_status": factory_plan.status},
            )
        return execution


def create_factory_plan_in_shadow(
    project: Project,
    questionnaire: dict[str, object],
    *,
    actor: str,
    session: FactoryChatSession | None = None,
) -> FactoryPlan:
    """Factory Chat adapter: plan creation is observed by Runtime from its start."""
    with transaction.atomic():
        factory_plan = create_plan(project, questionnaire, actor)
        start_shadow_for_factory_plan(factory_plan, actor=actor, session=session)
    return factory_plan


def _observe_approval_locked(
    execution: OrkiExecution, factory_plan: FactoryPlan, *, actor: str
) -> OrkiExecution:
    if (
        factory_plan.status != FactoryPlan.Status.APPROVED
        or not factory_plan.approval_id
    ):
        raise RuntimeTransitionError("RUNTIME_APPROVAL_NOT_AVAILABLE")
    if execution.state != OrkiExecution.State.WAITING_APPROVAL:
        return execution
    approval = factory_plan.approval
    if approval is None or approval.revoked_at is not None:
        raise RuntimeTransitionError("RUNTIME_APPROVAL_REVOKED")
    _transition(
        execution,
        OrkiExecution.State.WAITING_GOVERNANCE,
        actor=actor,
        reason={"approval_reference": approval.reference},
        event_type="APPROVAL_OBSERVED",
    )
    execution.governance_reference = {
        "scope_identifier": factory_plan.scope.identifier,
        "approval_reference": approval.reference,
        "handoff": "shadow_only",
    }
    execution.save(update_fields=["governance_reference", "updated_at"])
    _event(
        execution,
        "SHADOW_GOVERNANCE_HANDOFF_RECORDED",
        actor=actor,
        payload=execution.governance_reference,
        evidence_references=[factory_plan.scope.identifier, approval.reference],
    )
    return execution


def observe_factory_plan_approval(
    factory_plan: FactoryPlan, *, actor: str
) -> OrkiExecution:
    """Observe the existing approval; Runtime neither creates nor changes it."""
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__factory_plan__approval", "plan__factory_plan__scope")
            .filter(plan__factory_plan=factory_plan)
            .order_by("-created_at")
            .first()
        )
        if execution is None:
            execution = start_shadow_for_factory_plan(factory_plan, actor=actor)
            execution = OrkiExecution.objects.select_for_update().get(pk=execution.pk)
        observed_plan = execution.plan.factory_plan
        if observed_plan is None:
            raise RuntimeTransitionError("RUNTIME_APPROVAL_PLAN_REQUIRED")
        return _observe_approval_locked(execution, observed_plan, actor=actor)


def _explicit_plan_approval(text: str) -> bool:
    """Recognise the small, deterministic approval vocabulary at Runtime ingress."""
    import unicodedata

    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(character)
    )
    return normalized.strip() in {
        "jovahagyom",
        "jovahagyom a tervet",
        "ok mehet",
        "oke mehet",
        "rendben mehet",
    }


def _complete_factory_plan_approval(
    execution_token: str, *, actor: str
) -> OrkiExecution:
    """Coordinate an existing approval through OESM without replacing Governance."""
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal__source_session", "plan__factory_plan__project")
            .get(token=execution_token)
        )
        factory_plan = execution.plan.factory_plan
        if factory_plan is None:
            raise RuntimeTransitionError("RUNTIME_APPROVAL_PLAN_REQUIRED")
        if execution.state != OrkiExecution.State.WAITING_APPROVAL:
            raise RuntimeTransitionError("RUNTIME_CHAT_DISPATCH_NOT_AVAILABLE")
        _event(
            execution,
            "approval.requested",
            actor=actor,
            payload={"factory_plan_id": factory_plan.pk},
        )
        approved_plan = approve_plan(factory_plan.pk, factory_plan.project, actor)
        observe_factory_plan_approval(approved_plan, actor=actor)
        execution.refresh_from_db()
        _transition(execution, OrkiExecution.State.DISPATCHING, actor=actor)
        _transition(execution, OrkiExecution.State.RUNNING, actor=actor)

        session = execution.plan.goal.source_session
        if session is None:
            raise RuntimeTransitionError("RUNTIME_CHAT_SESSION_REQUIRED")
        mission, _ = FactoryMission.objects.get_or_create(session=session)
        mission.phase = FactoryMission.Phase.PLAN_APPROVED
        mission.delivery_status = {
            "state": "execution_preparation",
            "next": (
                "A jóváhagyott terv és a dokumentum-projekciók elkészültek. "
                "A végrehajtás külön, kanonikus szerződés alapján indítható."
            ),
        }
        mission.save(update_fields=["phase", "delivery_status", "updated_at"])
        reply = FactoryChatMessage.objects.create(
            session=session,
            role=FactoryChatMessage.Role.ORKI,
            body=(
                "A tervet jóváhagytad. Orki átvette a szállítást, és a "
                "jóváhagyott terv szerint folytatja a következő lépéssel."
            ),
            correlation_id=str(execution.provider_context.get("correlation_id", "")),
        )
        context = dict(execution.provider_context)
        context["reply_message_id"] = reply.pk
        execution.provider_context = context
        execution.save(update_fields=["provider_context", "updated_at"])
        _transition(execution, OrkiExecution.State.VERIFYING, actor=actor)
        verification = {
            "passed": True,
            "evidence_references": [
                f"factory-chat-message:{reply.pk}",
                approved_plan.scope.identifier,
                approved_plan.approval.reference if approved_plan.approval else "",
            ],
        }
        _event(execution, "verification.completed", actor=actor, payload=verification)
        _transition(execution, OrkiExecution.State.REFLECTING, actor=actor)
        reflection = OrkiReflection.objects.create(
            execution=execution,
            analysis={"factory_plan_id": approved_plan.pk, "approval_observed": True},
            evidence_references=cast(list[str], verification["evidence_references"]),
            completed_at=timezone.now(),
        )
        _event(
            execution,
            "reflection.completed",
            actor=actor,
            payload={"reflection_id": reflection.pk},
        )
        _transition(execution, OrkiExecution.State.COMPLETED, actor=actor)
        execution.plan.status = OrkiPlan.Status.COMPLETED
        execution.plan.save(update_fields=["status", "updated_at"])
        execution.plan.goal.status = OrkiGoal.Status.ACHIEVED
        execution.plan.goal.save(update_fields=["status", "updated_at"])
        _event(
            execution,
            "GOAL_ACHIEVED",
            actor=actor,
            payload={"factory_plan_id": approved_plan.pk},
        )
        return execution


def reference_cognitive_context(
    execution_token: str,
    *,
    cognitive_goal: CognitiveStateEntry,
    cognitive_plan: CognitiveStateEntry,
    actor: str,
) -> OrkiExecution:
    """Reference existing Cognitive State entries without copying their contents."""
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal")
            .get(token=execution_token)
        )
        project_id = execution.plan.goal.project_id
        if (
            cognitive_goal.state.project_id != project_id
            or cognitive_plan.state.project_id != project_id
        ):
            raise ValueError("RUNTIME_COGNITIVE_CONTEXT_PROJECT_MISMATCH")
        execution.plan.goal.cognitive_goal = cognitive_goal
        execution.plan.goal.save(update_fields=["cognitive_goal", "updated_at"])
        execution.plan.cognitive_plan = cognitive_plan
        execution.plan.save(update_fields=["cognitive_plan", "updated_at"])
        _event(
            execution,
            "COGNITIVE_CONTEXT_REFERENCED",
            actor=actor,
            payload={
                "cognitive_goal_id": cognitive_goal.pk,
                "cognitive_plan_id": cognitive_plan.pk,
            },
        )
        return execution


def pause_execution(
    execution_token: str, *, actor: str, reason: str = ""
) -> OrkiExecution:
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        if execution.state in {
            OrkiExecution.State.PAUSED,
            OrkiExecution.State.SUCCEEDED,
            OrkiExecution.State.COMPLETED,
            OrkiExecution.State.FAILED,
            OrkiExecution.State.CANCELLED,
        }:
            raise RuntimeTransitionError("RUNTIME_PAUSE_NOT_AVAILABLE")
        prior = execution.state
        _transition(
            execution,
            OrkiExecution.State.PAUSED,
            actor=actor,
            reason={"reason": reason},
        )
        execution.paused_from_state = prior
        execution.save(update_fields=["paused_from_state", "updated_at"])
        _event(execution, "PAUSED", actor=actor, payload={"resume_to": prior})
        return execution


def resume_execution(execution_token: str, *, actor: str) -> OrkiExecution:
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        target = execution.paused_from_state
        if execution.state != OrkiExecution.State.PAUSED or target not in _TRANSITIONS:
            raise RuntimeTransitionError("RUNTIME_RESUME_NOT_AVAILABLE")
        execution.state = target
        execution.paused_from_state = ""
        execution.state_version += 1
        execution.save(
            update_fields=["state", "paused_from_state", "state_version", "updated_at"]
        )
        _event(execution, "RESUMED", actor=actor, payload={"to": target})
        return execution


def recover_execution(execution_token: str, *, actor: str) -> OrkiExecution:
    """Record recovery intent; no queue/job/provider recovery is performed here."""
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        _event(
            execution,
            "RECOVERY_REQUESTED",
            actor=actor,
            payload={"state": execution.state},
        )
        if execution.state == OrkiExecution.State.WAITING_EXTERNAL:
            _transition(
                execution,
                OrkiExecution.State.PLANNING,
                actor=actor,
                reason={"recovery": "runtime_reassessment"},
                event_type="RECOVERY_REASSESSMENT_STARTED",
            )
        return execution


def wait_for_user_input(
    execution_token: str, *, actor: str, prompt: str
) -> OrkiExecution:
    """Persist an explicit Runtime user wait; it is not a paused worker."""
    if not prompt.strip():
        raise ValueError("RUNTIME_USER_WAIT_PROMPT_REQUIRED")
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        if execution.state == OrkiExecution.State.WAITING_GOVERNANCE:
            _transition(execution, OrkiExecution.State.DISPATCHING, actor=actor)
            _transition(execution, OrkiExecution.State.RUNNING, actor=actor)
        _transition(
            execution,
            OrkiExecution.State.WAITING_FOR_USER,
            actor=actor,
            reason={"prompt": prompt.strip()},
            event_type="USER_INPUT_REQUESTED",
        )
        return execution


def resume_after_user_input(
    execution_token: str, *, actor: str, response_reference: str
) -> OrkiExecution:
    """Resume an execution after a durable external response reference is supplied."""
    if not response_reference.strip():
        raise ValueError("RUNTIME_USER_RESPONSE_REFERENCE_REQUIRED")
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        _transition(
            execution,
            OrkiExecution.State.RUNNING,
            actor=actor,
            reason={"response_reference": response_reference.strip()},
            event_type="USER_INPUT_RECEIVED",
        )
        return execution


def cancel_execution(execution_token: str, *, actor: str, reason: str) -> OrkiExecution:
    """Cancel through OESM; cancellation is never a direct state write."""
    if not reason.strip():
        raise ValueError("RUNTIME_CANCELLATION_REASON_REQUIRED")
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        _transition(
            execution,
            OrkiExecution.State.CANCELLED,
            actor=actor,
            reason={"reason": reason.strip()},
            event_type="EXECUTION_CANCELLED",
        )
        execution.plan.goal.status = OrkiGoal.Status.CANCELLED
        execution.plan.goal.save(update_fields=["status", "updated_at"])
        _event(execution, "GOAL_CANCELLED", actor=actor)
        return execution


def execute_shadow_operation(
    execution_token: str,
    *,
    actor: str,
    operation: Callable[[], Mapping[str, Any]],
) -> OrkiExecution:
    """Run a real, supplied acceptance operation through the Shadow OESM.

    This is an internal Runtime acceptance seam, not a provider or filesystem API.
    It accepts no authority, starts no ExecutionRun and only runs an already
    governance-observed Shadow execution.  Production provider dispatch remains
    owned by the established ExecutionRun path.
    """
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal")
            .get(token=execution_token)
        )
        if execution.mode != OrkiExecution.Mode.SHADOW:
            raise RuntimeTransitionError("RUNTIME_ACCEPTANCE_OPERATION_SHADOW_ONLY")
        if execution.state not in {
            OrkiExecution.State.WAITING_GOVERNANCE,
            OrkiExecution.State.PLANNING,
            OrkiExecution.State.RUNNING,
        }:
            raise RuntimeTransitionError("RUNTIME_OPERATION_NOT_AVAILABLE")
        if execution.state != OrkiExecution.State.RUNNING:
            _transition(execution, OrkiExecution.State.DISPATCHING, actor=actor)
            _transition(execution, OrkiExecution.State.RUNNING, actor=actor)
        _event(execution, "EXECUTION_OPERATION_STARTED", actor=actor)

    try:
        result = execute_task_adapter(
            execution,
            task_key="shadow.acceptance.operation",
            kind="TOOL",
            input_data={"mode": execution.mode, "behaviour": execution.behaviour},
            operation=operation,
        )
    except WorkflowTaskFailure as error:  # The Engine owns task retry evidence.
        with transaction.atomic():
            execution = OrkiExecution.objects.select_for_update().get(
                token=execution_token
            )
            _event(
                execution,
                "EXECUTION_ATTEMPT_FAILED",
                actor=actor,
                payload={"error_type": type(error).__name__, "message": str(error)},
            )
            _transition(
                execution,
                OrkiExecution.State.WAITING_EXTERNAL,
                actor=actor,
                reason={
                    "recovery": "operation_failed",
                    "error_type": type(error).__name__,
                },
            )
            return execution

    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal")
            .get(token=execution_token)
        )
        _event(execution, "EXECUTION_OPERATION_COMPLETED", actor=actor, payload=result)
        _transition(execution, OrkiExecution.State.VERIFYING, actor=actor)
        verification = _validate_goal_integrity(execution, result)
        _event(execution, "verification.completed", actor=actor, payload=verification)
        if not verification["passed"]:
            _transition(
                execution,
                OrkiExecution.State.WAITING_EXTERNAL,
                actor=actor,
                reason={
                    "recovery": "goal_integrity_failed",
                    "failures": verification["failures"],
                },
            )
            return execution
        _transition(execution, OrkiExecution.State.REFLECTING, actor=actor)
        _event(
            execution,
            "reflection.started",
            actor=actor,
            payload={"verification": "passed"},
        )
        reflection = OrkiReflection.objects.create(
            execution=execution,
            analysis={
                "verification": verification,
                "knowledge_candidate": result.get("knowledge_candidate"),
            },
            evidence_references=cast(list[str], verification["evidence_references"]),
            completed_at=timezone.now(),
        )
        _event(
            execution,
            "reflection.completed",
            actor=actor,
            payload={"reflection_id": reflection.pk},
        )
        create_workflow_candidate(execution)
        _transition(execution, OrkiExecution.State.COMPLETED, actor=actor)
        execution.plan.status = OrkiPlan.Status.COMPLETED
        execution.plan.save(update_fields=["status", "updated_at"])
        execution.plan.goal.status = OrkiGoal.Status.ACHIEVED
        execution.plan.goal.save(update_fields=["status", "updated_at"])
        _event(execution, "GOAL_ACHIEVED", actor=actor, payload={"result": result})
        return execution


def _execution_request_definition(request: ExecutionRequest) -> dict[str, object]:
    """Canonical, immutable Runtime projection of an already validated decision."""
    return {
        "decision_id": str(request.decision_id),
        "goal": request.goal,
        "behaviour": request.evidence.behaviour,
        "plan": [
            {
                "identifier": item.identifier,
                "title": item.title,
                "depends_on": list(item.depends_on),
                "expected_result": item.expected_result,
            }
            for item in request.plan
        ],
        "required_capabilities": list(request.required_capabilities),
        "required_tools": list(request.required_tools),
        "required_workflows": list(request.required_workflows),
        "evidence": {
            "knowledge_entry_ids": list(request.evidence.knowledge_entry_ids),
            "embedding_hits": list(request.evidence.embedding_hits),
            "critic_observations": list(request.evidence.critic_observations),
        },
    }


def start_structured_decision_execution(
    project: Project, request: ExecutionRequest, *, actor: str
) -> OrkiExecution:
    """Create the canonical Runtime lifecycle from a validated decision request.

    Reasoning has already selected the behaviour, plan, tools, and capabilities.
    Runtime only persists and executes that immutable request; it never ranks or
    changes business candidates.
    """
    if request.contract_version != CONTRACT_VERSION:
        raise ValueError("RUNTIME_DECISION_CONTRACT_VERSION_INVALID")
    if not request.plan or not request.evidence.behaviour.strip():
        raise ValueError("RUNTIME_DECISION_REQUEST_INCOMPLETE")
    definition = _execution_request_definition(request)
    plan_hash = hashlib.sha256(
        json.dumps(definition, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with transaction.atomic():
        existing = (
            OrkiExecution.objects.select_for_update()
            .filter(provider_context__decision_id=str(request.decision_id))
            .order_by("-created_at")
            .first()
        )
        if existing:
            return existing
        goal = OrkiGoal.objects.create(
            project=project,
            intent_reference={
                "structured_decision_id": str(request.decision_id),
                "contract_version": request.contract_version,
                "goal": request.goal,
            },
        )
        plan = OrkiPlan.objects.create(
            goal=goal,
            version=1,
            plan_hash=plan_hash,
            contract_version=request.contract_version,
            definition=definition,
            strategy_references={"decision_id": str(request.decision_id)},
            status=OrkiPlan.Status.SELECTED,
        )
        execution = OrkiExecution.objects.create(
            plan=plan,
            mode=OrkiExecution.Mode.SHADOW,
            behaviour=request.evidence.behaviour,
            provider_context={
                "decision_id": str(request.decision_id),
                "contract_version": request.contract_version,
                "provider": "runtime-operation-gateway",
            },
        )
        _event(execution, "GoalCreated", actor=actor, payload={"goal": request.goal})
        _transition(
            execution,
            OrkiExecution.State.PLANNING,
            actor=actor,
            event_type="PlanningStarted",
        )
        _event(
            execution,
            "PlanningCompleted",
            actor=actor,
            payload={"plan_hash": plan_hash, "version": plan.version},
        )
        _transition(execution, OrkiExecution.State.READY, actor=actor)
        return execution


def execute_structured_decision(
    execution_token: str,
    *,
    actor: str,
    operation: Callable[[], Mapping[str, Any]],
) -> OrkiExecution:
    """Execute a supplied operation through the canonical Sprint-05 lifecycle.

    The callable is the provider gateway seam.  Its selection is outside the
    Runtime; the Runtime records provider/task events, verifies supplied
    evidence, and emits candidates without AKB mutation.
    """
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal")
            .get(token=execution_token)
        )
        if execution.state not in {
            OrkiExecution.State.READY,
            OrkiExecution.State.RETRYING,
        }:
            raise RuntimeTransitionError("RUNTIME_STRUCTURED_EXECUTION_NOT_READY")
        _transition(
            execution,
            OrkiExecution.State.RUNNING,
            actor=actor,
            event_type="ExecutionStarted",
        )
        _event(
            execution,
            "TaskStarted",
            actor=actor,
            payload={"behaviour": execution.behaviour},
        )
        _event(
            execution,
            "ProviderStarted",
            actor=actor,
            payload={"gateway": execution.provider_context.get("provider")},
        )
    try:
        result = execute_task_adapter(
            execution,
            task_key="structured.decision.operation",
            kind="TOOL",
            input_data={"behaviour": execution.behaviour},
            operation=operation,
        )
    except WorkflowTaskFailure as error:
        with transaction.atomic():
            execution = OrkiExecution.objects.select_for_update().get(
                token=execution_token
            )
            _event(
                execution,
                "Failed",
                actor=actor,
                payload={"error_type": type(error).__name__},
            )
            _transition(execution, OrkiExecution.State.FAILED, actor=actor)
            return execution
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal")
            .get(token=execution_token)
        )
        _event(
            execution,
            "ProviderCompleted",
            actor=actor,
            payload={"gateway": execution.provider_context.get("provider")},
        )
        _event(
            execution,
            "TaskCompleted",
            actor=actor,
            payload={"result_keys": sorted(result)},
        )
        _transition(
            execution,
            OrkiExecution.State.VERIFYING,
            actor=actor,
            event_type="VerificationStarted",
        )
        verification = _structured_verification(result)
        _event(execution, "VerificationCompleted", actor=actor, payload=verification)
        if not verification["passed"]:
            _event(
                execution,
                "Failed",
                actor=actor,
                payload={"failures": verification["failures"]},
            )
            _transition(execution, OrkiExecution.State.FAILED, actor=actor)
            return execution
        _transition(
            execution,
            OrkiExecution.State.REFLECTING,
            actor=actor,
            event_type="ReflectionStarted",
        )
        evidence = cast(list[str], verification["evidence_references"])
        reflection_input = result.get("reflection_candidate")
        if not isinstance(reflection_input, Mapping):
            raise RuntimeCandidateValidationError(
                "RUNTIME_CANDIDATE_REQUIRED_FIELDS:reflection_candidate"
            )
        reflection_data = RuntimeReflectionCandidateValidator.validate_input(
            reflection_input
        )
        reflection = RuntimeReflectionCandidate.objects.create(
            execution=execution,
            contract_version=CONTRACT_VERSION,
            schema_version=RUNTIME_CANDIDATE_SCHEMA_VERSION,
            goal_id=execution.plan.goal.token,
            summary=cast(str, reflection_data["summary"]),
            reflection_text=cast(str, reflection_data["reflection_text"]),
            verification_result=verification,
            confidence=cast(float, reflection_data["confidence"]),
            evidence_references=evidence,
        )
        _event(
            execution,
            "ReflectionCompleted",
            actor=actor,
            payload={"candidate_id": reflection.pk},
        )
        _transition(execution, OrkiExecution.State.KNOWLEDGE_CANDIDATE, actor=actor)
        knowledge_input = result.get("knowledge_candidate")
        if not isinstance(knowledge_input, Mapping):
            raise RuntimeCandidateValidationError(
                "RUNTIME_CANDIDATE_REQUIRED_FIELDS:knowledge_candidate"
            )
        knowledge_data = RuntimeKnowledgeCandidateValidator.validate_input(
            knowledge_input
        )
        candidate = RuntimeKnowledgeCandidate.objects.create(
            execution=execution,
            reflection_candidate=reflection,
            contract_version=CONTRACT_VERSION,
            schema_version=RUNTIME_CANDIDATE_SCHEMA_VERSION,
            title=cast(str, knowledge_data["title"]),
            summary=cast(str, knowledge_data["summary"]),
            body=cast(str, knowledge_data["body"]),
            reason=cast(str, knowledge_data["reason"]),
            confidence=cast(float, knowledge_data["confidence"]),
            tags=cast(list[str], knowledge_data["tags"]),
            evidence_references=evidence,
        )
        _event(
            execution,
            "KnowledgeCandidateCreated",
            actor=actor,
            payload={"candidate_id": candidate.pk},
            evidence_references=evidence,
        )
        create_workflow_candidate(execution)
        _transition(execution, OrkiExecution.State.COMPLETED, actor=actor)
        execution.plan.status = OrkiPlan.Status.COMPLETED
        execution.plan.save(update_fields=["status", "updated_at"])
        execution.plan.goal.status = OrkiGoal.Status.ACHIEVED
        execution.plan.goal.save(update_fields=["status", "updated_at"])
        _event(
            execution,
            "GoalCompleted",
            actor=actor,
            payload={"goal": execution.plan.goal.intent_reference["goal"]},
        )
        _event(execution, "Finished", actor=actor, payload={"state": execution.state})
        return execution


def recover_structured_decision(execution_token: str, *, actor: str) -> OrkiExecution:
    """Make a failed canonical execution retryable without losing its audit trail."""
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        if execution.state != OrkiExecution.State.FAILED:
            raise RuntimeTransitionError("RUNTIME_STRUCTURED_RECOVERY_NOT_AVAILABLE")
        _transition(execution, OrkiExecution.State.RECOVERY, actor=actor)
        _transition(execution, OrkiExecution.State.RETRYING, actor=actor)
        return execution


def _structured_verification(result: Mapping[str, Any]) -> dict[str, object]:
    verification = result.get("verification")
    if not isinstance(verification, Mapping):
        return {
            "passed": False,
            "failures": ["VERIFICATION_MISSING"],
            "evidence_references": [],
        }
    evidence = list(result.get("evidence_references") or [])
    passed = verification.get("passed") is True and bool(evidence)
    return {
        "passed": passed,
        "failures": [] if passed else ["VERIFICATION_FAILED_OR_EVIDENCE_MISSING"],
        "evidence_references": evidence,
    }


def _chat_messages_for_correlation(
    session: FactoryChatSession, correlation_id: str
) -> list[dict[str, object]]:
    """Return the durable transcript projection owned by the Runtime ingress."""
    return [
        {
            "id": message.pk,
            "role": message.role.lower(),
            "text": message.body,
            "status": message.status,
            "correlation_id": message.correlation_id,
            "error_code": message.error_code,
        }
        for message in session.messages.filter(correlation_id=correlation_id)
    ]


def start_factory_chat_execution(
    *,
    project: Project,
    session: FactoryChatSession,
    text: str,
    correlation_id: str,
    actor: str,
) -> OrkiExecution:
    """Accept a Factory Chat message through the canonical Runtime ingress.

    This deliberately does not invoke a provider.  Persisting Goal and Plan
    before dispatch makes browser retries idempotent and leaves Planning visible
    to the Runtime Event Stream.
    """
    with transaction.atomic():
        existing = (
            OrkiExecution.objects.select_for_update()
            .filter(provider_context__channel="FACTORY_CHAT")
            .order_by("-created_at")
        )
        for execution in existing:
            if execution.provider_context.get("correlation_id") == correlation_id:
                return execution
        owner = FactoryChatMessage.objects.create(
            session=session,
            role=FactoryChatMessage.Role.OWNER,
            body=text,
            correlation_id=correlation_id,
        )
        goal = OrkiGoal.objects.create(
            project=project,
            source_session=session,
            intent_reference={
                "channel": "FACTORY_CHAT",
                "owner_message_id": owner.pk,
                "correlation_id": correlation_id,
            },
        )
        approval_plan = None
        if _explicit_plan_approval(text):
            approval_plan = (
                FactoryPlan.objects.filter(
                    project=project, status=FactoryPlan.Status.PENDING_APPROVAL
                )
                .order_by("-created_at")
                .first()
            )
        plan = OrkiPlan.objects.create(
            goal=goal,
            version=1,
            plan_hash="",
            status=OrkiPlan.Status.SELECTED,
            strategy_references={
                "entrypoint": "FACTORY_CHAT_RUNTIME",
                "semantic_candidate_selection": "runtime_context_builder",
                "persona": "DEFAULT_RUNTIME_PERSPECTIVE",
                **(
                    {
                        "approval_intent": "FACTORY_PLAN",
                        "factory_plan_id": approval_plan.pk,
                    }
                    if approval_plan
                    else {}
                ),
            },
            factory_plan=approval_plan,
        )
        execution = OrkiExecution.objects.create(
            plan=plan,
            mode=OrkiExecution.Mode.LIVE,
            provider_context={
                "channel": "FACTORY_CHAT",
                "correlation_id": correlation_id,
                "owner_message_id": owner.pk,
                **({"approval_plan_id": approval_plan.pk} if approval_plan else {}),
            },
        )
        _event(execution, "FACTORY_CHAT_INGRESS_ACCEPTED", actor=actor)
        _event(
            execution,
            "GOAL_CREATED",
            actor=actor,
            payload={"goal_token": str(goal.token), "owner_message_id": owner.pk},
        )
        if approval_plan:
            _transition(execution, OrkiExecution.State.PLANNING, actor=actor)
            _transition(
                execution,
                OrkiExecution.State.WAITING_APPROVAL,
                actor=actor,
                reason={"factory_plan_id": approval_plan.pk},
            )
        else:
            _transition(execution, OrkiExecution.State.UNDERSTANDING, actor=actor)
            _event(execution, "understanding.started", actor=actor)
            _transition(execution, OrkiExecution.State.SEMANTIC_SEARCH, actor=actor)
            _event(
                execution,
                "semantic_search.started",
                actor=actor,
                payload={"sources": ["COGNITIVE_STATE_REFERENCE"]},
            )
        return execution


def _chat_failure(
    execution_token: str, *, actor: str, error_code: str, message: str
) -> OrkiExecution:
    with transaction.atomic():
        execution = OrkiExecution.objects.select_for_update().get(token=execution_token)
        context = dict(execution.provider_context)
        session = execution.plan.goal.source_session
        if session is not None and not context.get("reply_message_id"):
            reply = FactoryChatMessage.objects.create(
                session=session,
                role=FactoryChatMessage.Role.ORKI,
                body=message,
                status=FactoryChatMessage.Status.FAILED,
                correlation_id=str(context.get("correlation_id", "")),
                error_code=error_code,
            )
            context["reply_message_id"] = reply.pk
            execution.provider_context = context
            execution.save(update_fields=["provider_context", "updated_at"])
        _event(
            execution,
            "provider.dispatch.failed",
            actor=actor,
            payload={"code": error_code, "message": message},
        )
        if execution.state != OrkiExecution.State.WAITING_EXTERNAL:
            _transition(
                execution,
                OrkiExecution.State.WAITING_EXTERNAL,
                actor=actor,
                reason={"code": error_code, "message": message, "retryable": True},
            )
        return execution


def dispatch_factory_chat_execution(
    execution_token: str, *, actor: str
) -> OrkiExecution:
    """Dispatch a previously planned chat execution through the provider adapter.

    The provider boundary is reached only here.  The Runtime owns all lifecycle
    transitions, error reasons, verification, reflection and AKB hand-off.
    """
    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal__source_session")
            .get(token=execution_token)
        )
        if execution.provider_context.get("channel") != "FACTORY_CHAT":
            raise RuntimeTransitionError("RUNTIME_CHAT_EXECUTION_REQUIRED")
        if execution.state == OrkiExecution.State.COMPLETED:
            return execution
        is_approval = bool(execution.provider_context.get("approval_plan_id"))
        if execution.state not in {
            OrkiExecution.State.SEMANTIC_SEARCH,
            OrkiExecution.State.WAITING_EXTERNAL,
            OrkiExecution.State.WAITING_APPROVAL,
        } or (
            execution.state == OrkiExecution.State.WAITING_APPROVAL and not is_approval
        ):
            raise RuntimeTransitionError("RUNTIME_CHAT_DISPATCH_NOT_AVAILABLE")
        if is_approval:
            return _complete_factory_plan_approval(execution_token, actor=actor)
        if execution.state == OrkiExecution.State.WAITING_EXTERNAL:
            _transition(
                execution,
                OrkiExecution.State.SEMANTIC_SEARCH,
                actor=actor,
                reason={"retry": True},
            )
        _transition(execution, OrkiExecution.State.DISPATCHING, actor=actor)
        _event(execution, "provider.selection.started", actor=actor)
        session = execution.plan.goal.source_session
        if session is None:
            raise RuntimeTransitionError("RUNTIME_CHAT_SESSION_REQUIRED")
        owner = FactoryChatMessage.objects.get(
            pk=execution.provider_context["owner_message_id"]
        )

    # The Engine owns provider selection, prompt construction and invocation as
    # an AI Task. The Runtime only consumes its adapter result for mission flow.
    try:
        provider_result = execute_chat_provider_task(
            execution,
            session=session,
            owner_body=owner.body,
            model_adapter_resolver=model_adapter_for,
            model_text_decoder=model_text_response,
        )
    except WorkflowTaskFailure as error:
        cause = error.cause
        error_code = (
            cause.code
            if isinstance(cause, ProviderTaskError)
            else type(cause).__name__.upper() if cause else type(error).__name__.upper()
        )
        failure_message = (
            "A Runtime nem ér el konfigurált modellprovidert. "
            "A kérés helyreállítható."
            if error_code == "MODEL_PROVIDER_UNAVAILABLE"
            else (
                "A Runtime nem ér el használható provider-hitelesítést. "
                "A kérés helyreállítható."
                if error_code == "PROVIDER_CREDENTIAL_UNAVAILABLE"
                else (
                    "A Runtime várakozik: a provider válasza nem érkezett meg. "
                    "A futás helyreállítható."
                )
            )
        )
        return _chat_failure(
            execution_token,
            actor=actor,
            error_code=error_code,
            message=failure_message,
        )

    from .factory_orki import record_runtime_cognitive_observation

    response = str(provider_result["response"])
    provider_plan = provider_result.get("provider_plan")
    understanding = provider_result.get("understanding")
    raw = provider_result.get("raw")
    provider_id = str(provider_result["provider_id"])
    model = str(provider_result["model"])

    with transaction.atomic():
        execution = (
            OrkiExecution.objects.select_for_update()
            .select_related("plan__goal__source_session")
            .get(token=execution_token)
        )
        session = execution.plan.goal.source_session
        assert session is not None
        raw_payload = raw if isinstance(raw, dict) else {}
        usage = (
            raw_payload.get("usage", {})
            if isinstance(raw_payload.get("usage", {}), dict)
            else {}
        )
        reply = FactoryChatMessage.objects.create(
            session=session,
            role=FactoryChatMessage.Role.ORKI,
            body=response,
            correlation_id=str(execution.provider_context.get("correlation_id", "")),
            provider_id=provider_id,
            model=model,
            prompt_hash=str(provider_result["prompt_hash"]),
            response_hash=str(provider_result["response_hash"]),
            latency_ms=int(provider_result["latency_ms"]),
            attempt_count=int(provider_result["attempts"]),
            token_usage=usage,
        )
        try:
            replacement_response = record_runtime_cognitive_observation(
                project=execution.plan.goal.project,
                session=session,
                owner_message=owner,
                understanding=understanding,
                plan=provider_plan,
                correlation_id=str(
                    execution.provider_context.get("correlation_id", "")
                ),
                provider_id=provider_id,
                model=model,
                actor=actor,
            )
        except ValueError as error:
            error_code = str(error) or type(error).__name__.upper()
            message = (
                "A Runtime várakozik: a provider válasza nem teljesíti a "
                "kötelező Cognitive State követelményt."
            )
            reply.body = message
            reply.status = FactoryChatMessage.Status.FAILED
            reply.error_code = error_code
            reply.save(update_fields=["body", "status", "error_code"])
            _event(
                execution,
                "provider.response.rejected",
                actor=actor,
                payload={"code": error_code, "message": message},
            )
            _transition(
                execution,
                OrkiExecution.State.WAITING_EXTERNAL,
                actor=actor,
                reason={"code": error_code, "message": message, "retryable": True},
            )
            return execution
        if replacement_response:
            response = replacement_response
            reply.body = response
            reply.response_hash = hashlib.sha256(response.encode("utf-8")).hexdigest()
            reply.save(update_fields=["body", "response_hash"])
        context = dict(execution.provider_context)
        context.update(
            {
                "reply_message_id": reply.pk,
                "provider_id": provider_id,
                "model": model,
            }
        )
        execution.provider_context = context
        execution.save(update_fields=["provider_context", "updated_at"])
        _event(
            execution,
            "provider.response.received",
            actor=actor,
            payload={"provider_id": provider_id},
        )
        _transition(execution, OrkiExecution.State.GAP_ANALYSIS, actor=actor)
        mission = FactoryMission.objects.filter(session=session).first()
        readiness = mission.delivery_status.get("understanding", {}) if mission else {}
        if mission is not None and not mission.requirements_sufficient:
            _event(
                execution,
                "gap_analysis.completed",
                actor=actor,
                payload={
                    "confidence": readiness.get("confidence", 0),
                    "critical_unknowns": readiness.get("critical_unknowns", []),
                },
            )
            _transition(execution, OrkiExecution.State.QUESTION_GENERATION, actor=actor)
            _event(
                execution,
                "questions.generated",
                actor=actor,
                payload={"questions": readiness.get("questions", [])},
            )
            _transition(
                execution,
                OrkiExecution.State.WAITING_USER,
                actor=actor,
                reason={
                    "message": response,
                    "confidence": readiness.get("confidence", 0),
                    "questions": readiness.get("questions", []),
                    "critical_unknowns": readiness.get("critical_unknowns", []),
                },
            )
            return execution
        _event(
            execution, "gap_analysis.completed", actor=actor, payload={"ready": True}
        )
        _transition(execution, OrkiExecution.State.PLANNING, actor=actor)
        _event(execution, "planning.ready", actor=actor, payload={"plan_version": 1})
        _transition(
            execution,
            OrkiExecution.State.WAITING_APPROVAL,
            actor=actor,
            reason={"factory_plan_id": mission.plan_id if mission else None},
        )
        return execution


def _validate_goal_integrity(
    execution: OrkiExecution, result: Mapping[str, Any]
) -> dict[str, object]:
    """Deterministically compare the observed execution result to the original Goal."""
    factory_plan = execution.plan.factory_plan
    questionnaire: Mapping[str, Any] = (
        factory_plan.questionnaire if factory_plan else {}
    )
    expected = str(questionnaire.get("outcome", "")).strip()
    raw_checks = questionnaire.get("acceptance_checks", [])
    if isinstance(raw_checks, list):
        checks = [str(check).strip() for check in raw_checks if str(check).strip()]
    else:
        checks = [line.strip() for line in str(raw_checks).splitlines() if line.strip()]
    raw_verification = result.get("verification")
    verification: Mapping[str, Any] = (
        raw_verification if isinstance(raw_verification, Mapping) else {}
    )
    raw_checks_result = verification.get("checks")
    check_results: Mapping[str, Any] = (
        raw_checks_result if isinstance(raw_checks_result, Mapping) else {}
    )
    failures: list[str] = []
    if not expected or result.get("observed_goal") != expected:
        failures.append("GOAL_OUTCOME_MISMATCH")
    if not result.get("repository") or not result.get("repository_changes"):
        failures.append("REPOSITORY_EVIDENCE_MISSING")
    if verification.get("build") is not True or verification.get("tests") is not True:
        failures.append("BUILD_OR_TESTS_NOT_VERIFIED")
    if any(check_results.get(check) is not True for check in checks):
        failures.append("ACCEPTANCE_CHECK_FAILED")
    evidence = list(result.get("evidence_references") or [])
    if not evidence:
        failures.append("EVIDENCE_MISSING")
    return {
        "passed": not failures,
        "expected_goal": expected,
        "failures": failures,
        "evidence_references": evidence,
        "repository": result.get("repository", ""),
    }


def runtime_presentation(
    execution: OrkiExecution, *, progress_percent: int
) -> dict[str, object]:
    """Return the server-owned, plain-language Runtime presentation contract.

    This is deliberately a deterministic projection of OESM state and its
    durable reason/evidence.  It is not a Persona or Behaviour Engine and does
    not create authority, state, or knowledge.
    """
    state_copy = {
        OrkiExecution.State.CREATED: (
            "A Runtime rögzítette a kérést.",
            "A cél és a terv előkészítése következik.",
        ),
        OrkiExecution.State.UNDERSTANDING: (
            "The Runtime is interpreting the mission.",
            "Relevant knowledge sources are reviewed next.",
        ),
        OrkiExecution.State.SEMANTIC_SEARCH: (
            "The Runtime is reviewing project knowledge and prior decisions.",
            "Critical information gaps are analyzed next.",
        ),
        OrkiExecution.State.GAP_ANALYSIS: (
            "The Runtime is checking whether Planning is allowed.",
            "Critical gaps produce clarification questions.",
        ),
        OrkiExecution.State.QUESTION_GENERATION: (
            "The Runtime is generating the minimum useful clarification questions.",
            "It will wait for the user's answer.",
        ),
        OrkiExecution.State.WAITING_USER: (
            "The Runtime is waiting for answers to critical open questions.",
            "Mission understanding will run again after the answer.",
        ),
        OrkiExecution.State.PLANNING: (
            "A Runtime a célt végrehajtható tervvé rendezi.",
            "A provider-hívás előkészítése következik.",
        ),
        OrkiExecution.State.READY: (
            "The Runtime has a validated plan and is ready to execute.",
            "Execution can begin through the provider gateway.",
        ),
        OrkiExecution.State.WAITING: (
            "The Runtime is waiting for a runtime dependency.",
            "Execution resumes when the dependency is available.",
        ),
        OrkiExecution.State.RETRYING: (
            "The Runtime has recovered a failed execution and will retry.",
            "The provider gateway is the next step.",
        ),
        OrkiExecution.State.RECOVERY: (
            "The Runtime is preserving evidence while it prepares recovery.",
            "A retryable execution state follows.",
        ),
        OrkiExecution.State.WAITING_APPROVAL: (
            "A Runtime a szükséges jóváhagyásra vár.",
            "A jóváhagyás után governance ellenőrzés következik.",
        ),
        OrkiExecution.State.WAITING_GOVERNANCE: (
            "A Runtime a meglévő governance döntésre vár.",
            "A jóváhagyott végrehajtás indítása következik.",
        ),
        OrkiExecution.State.DISPATCHING: (
            "A Runtime előkészíti a provider-független végrehajtást.",
            "A végrehajtás futása következik.",
        ),
        OrkiExecution.State.RUNNING: (
            "A Runtime végrehajtja az aktuális lépést.",
            "Az eredmény ellenőrzése következik.",
        ),
        OrkiExecution.State.VERIFYING: (
            "A Runtime ellenőrzi a végrehajtás eredményét.",
            "A lezáró reflexió következik.",
        ),
        OrkiExecution.State.REFLECTING: (
            "A Runtime értékeli, hogy a cél teljesült-e.",
            "A tudásintegráció szükségességének eldöntése következik.",
        ),
        OrkiExecution.State.KNOWLEDGE_INTEGRATING: (
            "A Runtime a reflektált tanulságot ellenőrzött tudásjelöltté alakítja.",
            "A végrehajtás lezárása következik.",
        ),
        OrkiExecution.State.KNOWLEDGE_CANDIDATE: (
            "The Runtime produced a knowledge candidate for later governance.",
            "The execution can now complete without AKB mutation.",
        ),
        OrkiExecution.State.WAITING_EXTERNAL: (
            "A Runtime külső függőségre vár; a futás helyreállítható.",
            "A helyreállítás vagy az ismételt indítás következik.",
        ),
        OrkiExecution.State.WAITING_FOR_USER: (
            "A Runtime a felhasználó válaszára vár.",
            "A válasz után a végrehajtás folytatódik.",
        ),
        OrkiExecution.State.PAUSED: (
            "A Runtime futása szünetel.",
            "A folytatási döntés után az előző lépés folytatódik.",
        ),
        OrkiExecution.State.SUCCEEDED: (
            "A Runtime végrehajtása sikeres volt.",
            "A lezárási információk megtekinthetők.",
        ),
        OrkiExecution.State.COMPLETED: (
            "A Runtime végrehajtása lezárult.",
            "Nincs további végrehajtási lépés.",
        ),
        OrkiExecution.State.FAILED: (
            "A Runtime futása nem folytatható automatikusan.",
            "A rögzített hibaok alapján helyreállítás vagy új tervezés szükséges.",
        ),
        OrkiExecution.State.CANCELLED: (
            "A Runtime végrehajtása megszakult.",
            "Nincs további végrehajtási lépés.",
        ),
    }
    state = OrkiExecution.State(execution.state)
    human_message, estimated_next_step = state_copy[state]
    waiting_message = execution.waiting_reason.get("message")
    if execution.state.startswith("WAITING_") and isinstance(waiting_message, str):
        human_message = waiting_message
    latest_event = execution.events.order_by("-sequence").first()
    evidence_reference = (
        latest_event.evidence_references[0]
        if latest_event and latest_event.evidence_references
        else None
    )
    return {
        "runtime_state": execution.state,
        "progress_percent": progress_percent,
        "current_step": execution.get_state_display(),
        "human_message": human_message,
        "started_at": execution.created_at.isoformat(),
        "estimated_next_step": estimated_next_step,
        "evidence_reference": evidence_reference,
    }


def execution_projection(execution: OrkiExecution) -> dict[str, Any]:
    """Stable, provider-neutral read projection suitable for UI/API/audit consumers."""
    execution = OrkiExecution.objects.select_related(
        "plan__goal",
        "execution_run",
        "reflection__knowledge_integration",
        "knowledge_candidate",
    ).get(pk=execution.pk)
    progress_by_state = {
        OrkiExecution.State.CREATED: 0,
        OrkiExecution.State.UNDERSTANDING: 8,
        OrkiExecution.State.SEMANTIC_SEARCH: 15,
        OrkiExecution.State.GAP_ANALYSIS: 22,
        OrkiExecution.State.QUESTION_GENERATION: 26,
        OrkiExecution.State.WAITING_USER: 26,
        OrkiExecution.State.PLANNING: 30,
        OrkiExecution.State.WAITING_APPROVAL: 30,
        OrkiExecution.State.WAITING_GOVERNANCE: 40,
        OrkiExecution.State.DISPATCHING: 60,
        OrkiExecution.State.READY: 40,
        OrkiExecution.State.WAITING: 45,
        OrkiExecution.State.RETRYING: 55,
        OrkiExecution.State.RECOVERY: 50,
        OrkiExecution.State.RUNNING: 75,
        OrkiExecution.State.VERIFYING: 84,
        OrkiExecution.State.REFLECTING: 90,
        OrkiExecution.State.KNOWLEDGE_INTEGRATING: 96,
        OrkiExecution.State.KNOWLEDGE_CANDIDATE: 97,
        OrkiExecution.State.WAITING_EXTERNAL: 75,
        OrkiExecution.State.WAITING_FOR_USER: 75,
        OrkiExecution.State.PAUSED: 75,
        OrkiExecution.State.SUCCEEDED: 100,
        OrkiExecution.State.COMPLETED: 100,
        OrkiExecution.State.FAILED: 100,
        OrkiExecution.State.CANCELLED: 100,
    }
    progress_percent = progress_by_state[OrkiExecution.State(execution.state)]
    latest_event = execution.events.order_by("-sequence").first()
    presentation = {
        **runtime_presentation(execution, progress_percent=progress_percent),
        # The monitor consumes only server-owned Runtime fields.  These are
        # compact display values, not a second state model.
        "goal_status": execution.plan.goal.status,
        "planning_status": execution.plan.status,
        "waiting_message": str(execution.waiting_reason.get("message", "")),
        "reflection_status": (
            "COMPLETED" if hasattr(execution, "reflection") else "NOT_STARTED"
        ),
        "knowledge_integration_status": (
            execution.reflection.knowledge_integration.status
            if hasattr(execution, "reflection")
            and hasattr(execution.reflection, "knowledge_integration")
            else "CANDIDATE_READY"
            if hasattr(execution, "knowledge_candidate")
            else "NOT_REQUIRED"
        ),
        "behaviour": execution.behaviour or "UNSPECIFIED",
        "stage": execution.state,
        "provider": execution.provider_context.get("provider", ""),
        "running_task": (
            latest_event.payload.get("task", latest_event.event_type)
            if latest_event
            else ""
        ),
        "duration_seconds": int(
            (timezone.now() - execution.created_at).total_seconds()
        ),
    }
    events = [
        {
            "sequence": event.sequence,
            "type": event.event_type,
            "actor": event.actor_identity,
            "payload": event.payload,
            "evidence_references": event.evidence_references,
            "created_at": event.created_at.isoformat(),
        }
        for event in execution.events.all()
    ]
    recovery_events = [
        event
        for event in events
        if event["type"].startswith("RECOVERY_")
        or event["type"].startswith("recovery.")
    ]
    return {
        "token": str(execution.token),
        "execution_token": str(execution.token),
        "goal_token": str(execution.plan.goal.token),
        "goal": {
            "token": str(execution.plan.goal.token),
            "status": execution.plan.goal.status,
            "intent_reference": execution.plan.goal.intent_reference,
        },
        "plan_version": execution.plan.version,
        "plan": {
            "version": execution.plan.version,
            "status": execution.plan.status,
            "strategy_references": execution.plan.strategy_references,
        },
        "mode": execution.mode,
        "state": execution.state,
        "state_version": execution.state_version,
        "wait_reason": execution.waiting_reason,
        "waiting_reason": execution.waiting_reason,
        "governance_reference": execution.governance_reference,
        "execution_run_id": execution.execution_run_id,
        "reflection": (
            {
                "id": execution.reflection.pk,
                "completed_at": execution.reflection.completed_at.isoformat()
                if execution.reflection.completed_at
                else None,
            }
            if hasattr(execution, "reflection")
            else None
        ),
        "knowledge_integration": (
            {
                "status": execution.reflection.knowledge_integration.status,
                "knowledge_entry_id": (
                    execution.reflection.knowledge_integration.knowledge_entry_id
                ),
            }
            if hasattr(execution, "reflection")
            and hasattr(execution.reflection, "knowledge_integration")
            else None
        ),
        "progress": {
            "percent": progress_percent,
            "state": execution.state,
            "source": "OESM_DERIVED",
            "label": execution.get_state_display(),
        },
        "active_persona": "DEFAULT_RUNTIME_PERSPECTIVE",
        "presentation": presentation,
        # These fields are deliberately duplicated at the top level so every
        # API and SSE payload has the complete presentation contract without
        # client-side inference.
        **presentation,
        "evidence_count": execution.events.count()
        + (
            len(execution.reflection.evidence_references)
            if hasattr(execution, "reflection")
            else 0
        ),
        "recovery_events": recovery_events,
        "events": events,
    }

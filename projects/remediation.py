"""Provider-neutral governed remediation, validation, and release workflow."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.utils import timezone

from .engineering_memory import ingest_lifecycle_event
from .execution import cancel_run, enqueue_run
from .models import (
    DeploymentRecord,
    ExecutableScope,
    ExecutionContract,
    ExecutionRun,
    ExecutionStartRequest,
    FailureIncident,
    GovernanceApproval,
    McpAuditEvent,
    RemediationValidation,
    RemediationWorkflow,
)
from .orchestration_context import for_incident, for_remediation


class DeploymentAdapter(Protocol):
    """A release integration selected outside the orchestration domain."""

    name: str

    def deploy(self, *, environment: str, remediation: RemediationWorkflow) -> str: ...

    def rollback(
        self, *, environment: str, remediation: RemediationWorkflow
    ) -> str: ...


_deployment_adapters: dict[str, DeploymentAdapter] = {}


def register_deployment_adapter(adapter: DeploymentAdapter) -> None:
    """Register an explicit infrastructure adapter; no default is provided."""
    _deployment_adapters[adapter.name] = adapter


def _append(workflow: RemediationWorkflow, event: str, **details: object) -> None:
    workflow.timeline = [
        *workflow.timeline,
        {"at": timezone.now().isoformat(), "event": event, "details": details},
    ]


def _scope_for_contract(contract: ExecutionContract) -> ExecutableScope:
    declared = contract.payload.get("approved_scope", {})
    if contract.payload.get("schema_version") != "2.0" or not declared:
        raise ValueError("CONTRACT_AUTHORITY_REQUIRED")
    try:
        return ExecutableScope.objects.get(
            identifier=declared["identifier"], project=contract.project
        )
    except (ExecutableScope.DoesNotExist, KeyError) as exc:
        raise ValueError("CONTRACT_SCOPE_REQUIRED") from exc


def _execution_approval(
    approval: GovernanceApproval, contract: ExecutionContract
) -> None:
    scope = _scope_for_contract(contract)
    if (
        approval.revoked_at is not None
        or approval.project_id != contract.project_id
        or approval.scope_id != scope.pk
        or approval.reference != contract.payload.get("approval_reference")
        or approval.approved_action
        not in {"AUTHORIZE_EXECUTION", "ALL_GOVERNED_MUTATIONS", "ALL"}
    ):
        raise ValueError("APPROVAL_SCOPE_MISMATCH")


@transaction.atomic
def create_remediation(
    incident: FailureIncident, *, idempotency_key: str, summary: str
) -> RemediationWorkflow:
    """Create a technical plan only after deterministic ownership allows it."""
    for_incident(incident)
    existing = RemediationWorkflow.objects.filter(
        idempotency_key=idempotency_key
    ).first()
    if existing is not None:
        if existing.incident_id != incident.pk or existing.summary != summary:
            raise ValueError("REMEDIATION_IDEMPOTENCY_MISMATCH")
        for_remediation(existing)
        return existing
    try:
        ownership = incident.ownership_assessment
    except ObjectDoesNotExist as exc:
        raise ValueError("OWNERSHIP_ASSESSMENT_REQUIRED") from exc
    if (
        incident.status != FailureIncident.Status.ASSESSED
        or ownership.policy_decision != "ALLOW"
        or ownership.selected_project_id is None
    ):
        raise ValueError("REMEDIATION_POLICY_DENIED")
    try:
        with transaction.atomic():
            workflow = RemediationWorkflow.objects.create(
                incident=incident,
                project_id=ownership.selected_project_id,
                idempotency_key=idempotency_key,
                correlation_id=incident.correlation_id,
                summary=summary,
                status=RemediationWorkflow.Status.AWAITING_CONTRACT,
            )
    except IntegrityError:
        existing_workflow = RemediationWorkflow.objects.filter(
            idempotency_key=idempotency_key
        ).first()
        if (
            existing_workflow is None
            or existing_workflow.incident_id != incident.pk
            or existing_workflow.summary != summary
        ):
            raise ValueError("REMEDIATION_IDEMPOTENCY_MISMATCH")
        for_remediation(existing_workflow)
        return existing_workflow
    for_remediation(workflow)
    _append(workflow, "REMEDIATION_PLANNED", ownership_policy=ownership.policy_decision)
    workflow.save(update_fields=["timeline", "updated_at"])
    return workflow


@transaction.atomic
def link_contract(
    workflow: RemediationWorkflow, contract: ExecutionContract
) -> RemediationWorkflow:
    """Link, but never generate, the approved scope and consumed contract."""
    workflow = RemediationWorkflow.objects.select_for_update().get(pk=workflow.pk)
    for_remediation(workflow)
    if workflow.status not in {
        RemediationWorkflow.Status.AWAITING_CONTRACT,
        RemediationWorkflow.Status.RETRY_REQUIRED,
    }:
        raise ValueError("REMEDIATION_NOT_AWAITING_CONTRACT")
    if (
        contract.project_id != workflow.project_id
        or contract.lifecycle != ExecutionContract.Lifecycle.CONSUMED
    ):
        raise ValueError("REMEDIATION_CONTRACT_NOT_CONSUMED")
    scope = _scope_for_contract(contract)
    if workflow.contract_id == contract.pk:
        raise ValueError("REMEDIATION_RETRY_REQUIRES_NEW_CONTRACT")
    workflow.scope = scope
    workflow.contract = contract
    workflow.status = RemediationWorkflow.Status.CONTRACT_LINKED
    _append(
        workflow,
        "CONTRACT_LINKED" if workflow.retry_count == 0 else "RETRY_CONTRACT_LINKED",
        contract=contract.handoff_identifier,
        scope=scope.identifier,
    )
    workflow.save(
        update_fields=["scope", "contract", "status", "timeline", "updated_at"]
    )
    return workflow


@transaction.atomic
def dispatch_remediation(
    workflow: RemediationWorkflow,
    *,
    approval: GovernanceApproval,
    platform_root: Path,
    deadline_at: datetime | None = None,
    caller: str = "orchestrator-remediation",
) -> RemediationWorkflow:
    """Dispatch through the existing canonical executor after authority checks."""
    workflow = RemediationWorkflow.objects.select_for_update().get(pk=workflow.pk)
    context = for_remediation(workflow)
    if workflow.status == RemediationWorkflow.Status.DISPATCHED:
        return workflow
    if (
        workflow.status != RemediationWorkflow.Status.CONTRACT_LINKED
        or workflow.contract_id is None
    ):
        raise ValueError("REMEDIATION_DISPATCH_NOT_READY")
    contract = workflow.contract
    if contract is None:
        raise ValueError("REMEDIATION_DISPATCH_NOT_READY")
    _execution_approval(approval, contract)
    request, _ = ExecutionStartRequest.objects.get_or_create(
        contract=contract, defaults={"approval": approval}
    )
    if request.approval_id != approval.pk:
        raise ValueError("EXECUTION_REQUEST_APPROVAL_MISMATCH")
    audit = McpAuditEvent.objects.create(
        caller=caller,
        tool_name="remediation.dispatch",
        project=workflow.project,
        outcome="DISPATCHING",
        details={
            **context.as_dict(),
            "remediation_id": workflow.pk,
            "contract": contract.handoff_identifier,
            "approval": approval.reference,
        },
    )
    job = enqueue_run(contract, request, platform_root, audit_event_id=audit.pk)
    run = job.run
    audit.outcome = "DISPATCHED"
    audit.save(update_fields=["outcome"])
    request.status = "EXECUTION_QUEUED"
    request.next_action = "Independent worker must claim the durable job."
    request.save(update_fields=["status", "next_action"])
    workflow.start_request = request
    workflow.run = run
    workflow.deadline_at = deadline_at
    workflow.status = RemediationWorkflow.Status.DISPATCHED
    _append(workflow, "EXECUTOR_DISPATCHED", execution_token=str(run.token))
    workflow.save(
        update_fields=[
            "start_request",
            "run",
            "deadline_at",
            "status",
            "timeline",
            "updated_at",
        ]
    )
    return workflow


@transaction.atomic
def enforce_timeout(
    workflow: RemediationWorkflow,
    *,
    approval: GovernanceApproval,
    now: datetime | None = None,
) -> RemediationWorkflow:
    """Cancel under existing authority on deadline; never start a replacement."""
    for_remediation(workflow)
    now = now or timezone.now()
    if workflow.status != RemediationWorkflow.Status.DISPATCHED:
        return workflow
    if workflow.deadline_at is None or now < workflow.deadline_at:
        return workflow
    run = workflow.run
    if run is None:
        raise ValueError("REMEDIATION_RUN_REQUIRED")
    contract = workflow.contract
    if contract is None:
        raise ValueError("REMEDIATION_RUN_REQUIRED")
    _execution_approval(approval, contract)
    if run.lifecycle in {
        ExecutionRun.Lifecycle.RUNNING,
        ExecutionRun.Lifecycle.STARTING,
    }:
        cancel_run(
            run,
            approval_reference=approval.reference,
            phase="TIMED_OUT",
        )
    workflow.status = RemediationWorkflow.Status.TIMED_OUT
    _append(workflow, "DISPATCH_TIMED_OUT", execution_token=str(run.token))
    workflow.save(update_fields=["status", "timeline", "updated_at"])
    return workflow


@transaction.atomic
def cancel_remediation(
    workflow: RemediationWorkflow, *, approval: GovernanceApproval
) -> RemediationWorkflow:
    """Cancel an active run only under the original scope-bound authority."""
    for_remediation(workflow)
    run = workflow.run
    contract = workflow.contract
    if run is None or contract is None:
        raise ValueError("REMEDIATION_RUN_REQUIRED")
    _execution_approval(approval, contract)
    if run.lifecycle in {
        ExecutionRun.Lifecycle.RUNNING,
        ExecutionRun.Lifecycle.STARTING,
    }:
        cancel_run(run, approval_reference=approval.reference)
    elif run.lifecycle != ExecutionRun.Lifecycle.CANCELLED:
        raise ValueError("EXECUTION_NOT_CANCELLABLE")
    workflow.status = RemediationWorkflow.Status.CANCELLED
    _append(workflow, "REMEDIATION_CANCELLED", approval=approval.reference)
    workflow.save(update_fields=["status", "timeline", "updated_at"])
    return workflow


@transaction.atomic
def validate_remediation(
    workflow: RemediationWorkflow,
    *,
    validator_identity: str,
    outcome: str,
    evidence_references: list[str],
    rationale: str,
) -> RemediationValidation:
    """Persist an independently identified validator result with provenance."""
    workflow = RemediationWorkflow.objects.select_for_update().get(pk=workflow.pk)
    for_remediation(workflow)
    run = workflow.run
    if run is None or run.lifecycle != ExecutionRun.Lifecycle.COMPLETED:
        raise ValueError("COMPLETED_RUN_REQUIRED")
    if not validator_identity or validator_identity == run.provider_name:
        raise ValueError("INDEPENDENT_VALIDATOR_REQUIRED")
    if not evidence_references or any(
        not reference for reference in evidence_references
    ):
        raise ValueError("VALIDATION_EVIDENCE_REQUIRED")
    if outcome not in RemediationValidation.Outcome.values:
        raise ValueError("VALIDATION_OUTCOME_INVALID")
    validation, created = RemediationValidation.objects.get_or_create(
        remediation=workflow,
        execution_token=run.token,
        defaults={
            "validator_identity": validator_identity,
            "outcome": outcome,
            "evidence_references": evidence_references,
            "rationale": rationale,
        },
    )
    if not created and (
        validation.validator_identity != validator_identity
        or validation.outcome != outcome
        or validation.evidence_references != evidence_references
        or validation.rationale != rationale
    ):
        raise ValueError("VALIDATION_IMMUTABLE")
    if not created:
        return validation
    workflow.status = RemediationWorkflow.Status.VALIDATION_PENDING
    _append(
        workflow,
        "INDEPENDENT_VALIDATION",
        outcome=outcome,
        validator=validator_identity,
    )
    workflow.save(update_fields=["status", "timeline", "updated_at"])
    return validation


@transaction.atomic
def continue_workflow(workflow: RemediationWorkflow) -> RemediationWorkflow:
    """Deterministically resume, retry, or escalate without execution authority."""
    workflow = RemediationWorkflow.objects.select_for_update().get(pk=workflow.pk)
    for_remediation(workflow)
    if workflow.status in {
        RemediationWorkflow.Status.RESUMED,
        RemediationWorkflow.Status.ESCALATED,
        RemediationWorkflow.Status.RETRY_REQUIRED,
    }:
        return workflow
    if workflow.status != RemediationWorkflow.Status.VALIDATION_PENDING:
        raise ValueError("REMEDIATION_VALIDATION_NOT_READY")
    validation = workflow.validations.order_by("-created_at", "-pk").first()
    if validation is None:
        raise ValueError("VALIDATION_REQUIRED")
    if validation.outcome == RemediationValidation.Outcome.PASSED:
        workflow.incident.status = FailureIncident.Status.CLOSED
        workflow.incident.save(update_fields=["status", "updated_at"])
        workflow.status = RemediationWorkflow.Status.RESUMED
        event = "WORKFLOW_RESUMED"
        ingest_lifecycle_event(
            workflow.project,
            event_type="REMEDIATION_COMPLETED",
            event_key=str(workflow.pk),
            source_reference=f"remediation:{workflow.pk}",
            evidence_references=validation.evidence_references,
            attributes={
                "validator": validation.validator_identity,
                "outcome": validation.outcome,
            },
        )
        ingest_lifecycle_event(
            workflow.project,
            event_type="INCIDENT_RESOLVED",
            event_key=str(workflow.incident.token),
            source_reference=f"incident:{workflow.incident.token}",
            evidence_references=validation.evidence_references,
            attributes={"via_remediation": workflow.pk},
        )
    elif workflow.incident.causal_classification in {"BUSINESS", "MIXED", "UNSAFE"}:
        workflow.status = RemediationWorkflow.Status.ESCALATED
        event = "BUSINESS_AUTHORITY_ESCALATED"
    elif workflow.retry_count >= workflow.max_retries:
        workflow.status = RemediationWorkflow.Status.ESCALATED
        event = "RETRY_EXHAUSTED_ESCALATED"
    else:
        workflow.retry_count += 1
        workflow.status = RemediationWorkflow.Status.RETRY_REQUIRED
        event = "RETRY_REQUIRES_NEW_CONTRACT"
    _append(workflow, event, validation_outcome=validation.outcome)
    workflow.save(update_fields=["status", "retry_count", "timeline", "updated_at"])
    return workflow


def deploy_or_rollback(
    workflow: RemediationWorkflow,
    *,
    approval: GovernanceApproval,
    action: str,
    environment: str,
    adapter_name: str,
    idempotency_key: str,
) -> DeploymentRecord:
    """Execute an adapter only with a durable, explicit release authority."""
    for_remediation(workflow)
    existing = DeploymentRecord.objects.filter(idempotency_key=idempotency_key).first()
    if existing is not None:
        if (
            existing.remediation_id != workflow.pk
            or existing.approval_id != approval.pk
            or existing.action != action
            or existing.environment != environment
        ):
            raise ValueError("DEPLOYMENT_IDEMPOTENCY_MISMATCH")
        return existing
    expected = (
        "AUTHORIZE_DEPLOYMENT"
        if action == DeploymentRecord.Action.DEPLOY
        else "AUTHORIZE_ROLLBACK"
    )
    if action not in DeploymentRecord.Action.values or approval.revoked_at is not None:
        raise ValueError("DEPLOYMENT_AUTHORITY_REQUIRED")
    if approval.project_id != workflow.project_id or approval.approved_action not in {
        expected,
        "ALL_GOVERNED_MUTATIONS",
        "ALL",
    }:
        raise ValueError("DEPLOYMENT_AUTHORITY_REQUIRED")
    if approval.scope_id is not None and approval.scope_id != workflow.scope_id:
        raise ValueError("DEPLOYMENT_AUTHORITY_REQUIRED")
    if action == DeploymentRecord.Action.DEPLOY:
        if workflow.status != RemediationWorkflow.Status.RESUMED:
            raise ValueError("VALIDATED_REMEDIATION_REQUIRED")
    elif not workflow.deployments.filter(
        action=DeploymentRecord.Action.DEPLOY, status=DeploymentRecord.Status.COMPLETED
    ).exists():
        raise ValueError("DEPLOYMENT_REQUIRED_BEFORE_ROLLBACK")
    adapter = _deployment_adapters.get(adapter_name)
    if adapter is None:
        raise ValueError("DEPLOYMENT_ADAPTER_UNAVAILABLE")
    try:
        with transaction.atomic():
            record = DeploymentRecord.objects.create(
                remediation=workflow,
                approval=approval,
                action=action,
                environment=environment,
                idempotency_key=idempotency_key,
                status=DeploymentRecord.Status.REQUESTED,
            )
    except IntegrityError:
        existing_record = DeploymentRecord.objects.filter(
            idempotency_key=idempotency_key
        ).first()
        if (
            existing_record is None
            or existing_record.remediation_id != workflow.pk
            or existing_record.approval_id != approval.pk
            or existing_record.action != action
            or existing_record.environment != environment
        ):
            raise ValueError("DEPLOYMENT_IDEMPOTENCY_MISMATCH")
        return existing_record
    try:
        receipt = (
            adapter.deploy(environment=environment, remediation=workflow)
            if action == DeploymentRecord.Action.DEPLOY
            else adapter.rollback(environment=environment, remediation=workflow)
        )
    except OSError as exc:
        record.status = DeploymentRecord.Status.FAILED
        record.detail = str(exc)[:1000]
        record.save(update_fields=["status", "detail", "updated_at"])
        raise ValueError("DEPLOYMENT_PROVIDER_UNAVAILABLE") from exc
    record.status = DeploymentRecord.Status.COMPLETED
    record.provider_receipt = receipt[:255]
    record.save(update_fields=["status", "provider_receipt", "updated_at"])
    _append(
        workflow, f"{action}_COMPLETED", environment=environment, receipt=receipt[:255]
    )
    workflow.save(update_fields=["timeline", "updated_at"])
    if action == DeploymentRecord.Action.DEPLOY:
        ingest_lifecycle_event(
            workflow.project,
            event_type="RELEASE_COMPLETED",
            event_key=str(record.pk),
            source_reference=f"deployment:{record.pk}",
            evidence_references=[record.provider_receipt],
            attributes={"environment": environment, "remediation": workflow.pk},
        )
    return record

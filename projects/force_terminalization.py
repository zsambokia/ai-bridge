"""Narrow, local break-glass terminalization for unsafe stuck executions.

This module is deliberately not exposed through the governed MCP surface.  It
exists for a Product Owner-authorized incident where the normal provider and
recovery path cannot safely make progress.  It never starts, cancels, requeues,
or recovers a provider process.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .execution import add_event, provider
from .models import (
    ExecutionContract,
    ExecutionJob,
    ExecutionProgressEvent,
    ExecutionRun,
    ExecutionWorkspace,
)


class ForceTerminalizationRefused(ValueError):
    """The observed execution state is not safe for a break-glass stop."""


@dataclass(frozen=True)
class ForceTerminalizationResult:
    execution_token: str
    job_token: str
    action: str
    dry_run: bool
    idempotent: bool
    run_lifecycle_before: str
    run_lifecycle_after: str
    job_status_before: str
    job_status_after: str
    contract_lifecycle_before: str
    contract_lifecycle_after: str
    workspace_status_before: str
    workspace_status_after: str
    workspace_provider_pid_after: int | None
    workspace_preserved: bool
    idempotency_key: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def force_terminalize_execution(
    execution_token: str | UUID,
    *,
    reason: str,
    operator: str,
    preserve_workspace: bool,
    dry_run: bool = False,
    idempotency_key: str | None = None,
) -> ForceTerminalizationResult:
    """Atomically terminalize one verified non-running execution and its job.

    The only admitted cases are a not-yet-started request, a RUNNING record
    whose OS process is gone and whose projected provider event proves a process
    exit, or the narrow STARTING/RECOVERING state created when reconciliation
    tried to restart such a proven-finished provider. Terminal runs are an
    idempotent no-op.
    """

    token = _parse_token(execution_token)
    normalized_reason = reason.strip()
    normalized_operator = operator.strip()
    if not normalized_reason:
        raise ForceTerminalizationRefused("BREAK_GLASS_REASON_REQUIRED")
    if not normalized_operator:
        raise ForceTerminalizationRefused("BREAK_GLASS_OPERATOR_REQUIRED")
    if not preserve_workspace:
        raise ForceTerminalizationRefused("BREAK_GLASS_WORKSPACE_PRESERVATION_REQUIRED")
    key = idempotency_key or _idempotency_key(
        token, normalized_operator, normalized_reason
    )

    with transaction.atomic():
        run = ExecutionRun.objects.select_for_update().filter(token=token).first()
        if run is None:
            raise ForceTerminalizationRefused("EXECUTION_NOT_FOUND")
        job = ExecutionJob.objects.select_for_update().filter(run=run).first()
        if job is None:
            raise ForceTerminalizationRefused("EXECUTION_JOB_NOT_FOUND")
        contract = ExecutionContract.objects.select_for_update().get(pk=run.contract_id)
        workspace = (
            ExecutionWorkspace.objects.select_for_update().filter(run=run).first()
        )
        before_lifecycle = run.lifecycle
        before_job_status = job.status
        before_contract_lifecycle = contract.lifecycle
        if run.lifecycle in _TERMINAL_LIFECYCLES:
            return _result(
                run,
                job,
                action="ALREADY_TERMINAL",
                dry_run=dry_run,
                idempotent=True,
                run_lifecycle_before=before_lifecycle,
                run_lifecycle_after=run.lifecycle,
                job_status_before=before_job_status,
                job_status_after=job.status,
                contract_lifecycle_before=before_contract_lifecycle,
                contract_lifecycle_after=contract.lifecycle,
                workspace_status_before=workspace.status if workspace else "",
                workspace_status_after=workspace.status if workspace else "",
                workspace_provider_pid_after=workspace.provider_pid
                if workspace
                else None,
                idempotency_key=key,
            )

        observation = _validate_safe_terminalization(run, job)
        if dry_run:
            return _result(
                run,
                job,
                action="WOULD_TERMINALIZE",
                dry_run=True,
                idempotent=False,
                run_lifecycle_before=before_lifecycle,
                run_lifecycle_after=ExecutionRun.Lifecycle.CANCELLED,
                job_status_before=before_job_status,
                job_status_after=ExecutionJob.Status.FAILED,
                contract_lifecycle_before=before_contract_lifecycle,
                contract_lifecycle_after=ExecutionContract.Lifecycle.CANCELLED,
                workspace_status_before=workspace.status if workspace else "",
                workspace_status_after=(
                    ExecutionWorkspace.Status.RETAINED if workspace else ""
                ),
                workspace_provider_pid_after=None,
                idempotency_key=key,
            )

        now = timezone.now()
        last_heartbeat_at = job.last_heartbeat_at
        job.status = ExecutionJob.Status.FAILED
        job.lease_owner = ""
        job.lease_expires_at = None
        job.last_heartbeat_at = None
        job.next_recovery_at = None
        job.provider_attempt_metadata = {
            **job.provider_attempt_metadata,
            "break_glass_terminalization": {
                "idempotency_key": key,
                "operator": normalized_operator,
                "reason": normalized_reason,
                "at": now.isoformat(),
            },
        }
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "last_heartbeat_at",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
        run.lifecycle = ExecutionRun.Lifecycle.CANCELLED
        run.current_phase = "BREAK_GLASS_TERMINALIZED"
        run.terminal_state = "CANCELLED — PRODUCT OWNER BREAK-GLASS"
        run.current_blocker = {
            "code": "BREAK_GLASS_TERMINALIZED",
            "operator": normalized_operator,
            "reason": normalized_reason,
            "workspace_preserved": True,
        }
        run.ended_at = now
        run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "terminal_state",
                "current_blocker",
                "ended_at",
                "updated_at",
            ]
        )
        contract.lifecycle = ExecutionContract.Lifecycle.CANCELLED
        contract.closure_state = "CANCELLED — PRODUCT OWNER BREAK-GLASS"
        contract.completed_at = now
        contract.save(update_fields=["lifecycle", "closure_state", "completed_at"])
        workspace_before = workspace.status if workspace else ""
        if workspace is not None:
            workspace.status = ExecutionWorkspace.Status.RETAINED
            workspace.provider_pid = None
            workspace.save(update_fields=["status", "provider_pid", "updated_at"])
        add_event(
            run,
            "EXECUTION_BREAK_GLASS_TERMINALIZED",
            operation="force_terminalize_execution",
            break_glass=True,
            idempotency_key=key,
            operator=normalized_operator,
            reason=normalized_reason,
            lifecycle_before=before_lifecycle,
            lifecycle_after=run.lifecycle,
            job_status_before=before_job_status,
            job_status_after=job.status,
            provider_execution_id=run.provider_execution_id,
            provider_pid_state=observation["provider_pid_state"],
            last_heartbeat_at=_isoformat(last_heartbeat_at),
            last_provider_event=observation["last_provider_event"],
            provider_exit_evidence=observation["provider_exit_evidence"],
            workspace_preserved=True,
            workspace_id=str(workspace.token) if workspace else "",
            workspace_status_before=workspace_before,
            workspace_status_after=workspace.status if workspace else "",
            workspace_cleanup_performed=False,
        )
        return _result(
            run,
            job,
            action="TERMINALIZED",
            dry_run=False,
            idempotent=False,
            run_lifecycle_before=before_lifecycle,
            run_lifecycle_after=run.lifecycle,
            job_status_before=before_job_status,
            job_status_after=job.status,
            contract_lifecycle_before=before_contract_lifecycle,
            contract_lifecycle_after=contract.lifecycle,
            workspace_status_before=workspace_before,
            workspace_status_after=workspace.status if workspace else "",
            workspace_provider_pid_after=workspace.provider_pid if workspace else None,
            idempotency_key=key,
        )


_TERMINAL_LIFECYCLES = {
    ExecutionRun.Lifecycle.COMPLETED,
    ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION,
    ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
    ExecutionRun.Lifecycle.FAILED_GOVERNANCE,
    ExecutionRun.Lifecycle.CANCELLED,
}


def _validate_safe_terminalization(
    run: ExecutionRun, job: ExecutionJob
) -> dict[str, object]:
    events = list(run.events.order_by("sequence"))
    last_provider_event = next(
        (
            event
            for event in reversed(events)
            if event.event_type.startswith("PROVIDER_")
        ),
        None,
    )
    observation: dict[str, object] = {
        "provider_pid_state": "NOT_APPLICABLE",
        "last_provider_event": _event_snapshot(last_provider_event),
        "provider_exit_evidence": {},
    }
    if run.lifecycle == ExecutionRun.Lifecycle.REQUESTED:
        if run.provider_execution_id:
            raise ForceTerminalizationRefused("REQUESTED_EXECUTION_HAS_PROVIDER_ID")
        if job.status not in {ExecutionJob.Status.QUEUED, ExecutionJob.Status.LEASED}:
            raise ForceTerminalizationRefused("REQUESTED_EXECUTION_JOB_NOT_CANCELLABLE")
        return observation
    recovery_restart = (
        run.lifecycle == ExecutionRun.Lifecycle.STARTING
        and run.current_phase == "RECOVERING"
        and job.status == ExecutionJob.Status.RECOVERING
    )
    if run.lifecycle != ExecutionRun.Lifecycle.RUNNING and not recovery_restart:
        raise ForceTerminalizationRefused(
            "EXECUTION_LIFECYCLE_NOT_BREAK_GLASS_ELIGIBLE"
        )
    workspace_provider_pid = (
        ExecutionWorkspace.objects.filter(run=run)
        .values_list("provider_pid", flat=True)
        .first()
    )
    provider_ids = {
        str(candidate)
        for candidate in (
            run.provider_execution_id,
            job.provider_attempt_metadata.get("provider_execution_id"),
            workspace_provider_pid,
        )
        if candidate not in (None, "")
    }
    if not provider_ids:
        raise ForceTerminalizationRefused("RUNNING_EXECUTION_PROVIDER_ID_REQUIRED")
    if len(provider_ids) != 1:
        raise ForceTerminalizationRefused("PROVIDER_EXECUTION_ID_CONFLICT")
    provider_execution_id = provider_ids.pop()
    try:
        provider_status = provider(run.provider_name).status(provider_execution_id)
    except (OSError, ValueError) as exc:
        raise ForceTerminalizationRefused("PROVIDER_PID_STATE_UNVERIFIABLE") from exc
    observation["provider_pid_state"] = provider_status
    if provider_status != "FINISHED":
        raise ForceTerminalizationRefused("PROVIDER_PROCESS_STILL_RUNNING")
    exit_event = next(
        (
            event
            for event in reversed(events)
            if event.event_type == "PROVIDER_COMPLETED"
            and event.details.get("provider_event_type") == "process.exit"
        ),
        None,
    )
    if exit_event is None:
        raise ForceTerminalizationRefused("PROVIDER_EXIT_EVENT_REQUIRED")
    observation["provider_exit_evidence"] = _event_snapshot(exit_event)
    return observation


def _event_snapshot(event: ExecutionProgressEvent | None) -> dict[str, object]:
    if event is None:
        return {}
    return {
        "sequence": event.sequence,
        "event_type": event.event_type,
        "created_at": _isoformat(event.created_at),
        "provider_event_type": event.details.get("provider_event_type", ""),
        "exit_code": event.details.get("exit_code"),
    }


def _result(
    run: ExecutionRun,
    job: ExecutionJob,
    *,
    action: str,
    dry_run: bool,
    idempotent: bool,
    run_lifecycle_before: str,
    run_lifecycle_after: str,
    job_status_before: str,
    job_status_after: str,
    contract_lifecycle_before: str,
    contract_lifecycle_after: str,
    workspace_status_before: str,
    workspace_status_after: str,
    workspace_provider_pid_after: int | None,
    idempotency_key: str,
) -> ForceTerminalizationResult:
    return ForceTerminalizationResult(
        execution_token=str(run.token),
        job_token=str(job.token),
        action=action,
        dry_run=dry_run,
        idempotent=idempotent,
        run_lifecycle_before=run_lifecycle_before,
        run_lifecycle_after=run_lifecycle_after,
        job_status_before=job_status_before,
        job_status_after=job_status_after,
        contract_lifecycle_before=contract_lifecycle_before,
        contract_lifecycle_after=contract_lifecycle_after,
        workspace_status_before=workspace_status_before,
        workspace_status_after=workspace_status_after,
        workspace_provider_pid_after=workspace_provider_pid_after,
        workspace_preserved=True,
        idempotency_key=idempotency_key,
    )


def _parse_token(value: str | UUID) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise ForceTerminalizationRefused("EXECUTION_TOKEN_INVALID") from exc


def _idempotency_key(token: UUID, operator: str, reason: str) -> str:
    payload = f"force-terminalize:{token}:{operator}:{reason}".encode("utf-8")
    return sha256(payload).hexdigest()


def _isoformat(value: object) -> str:
    return value.isoformat() if hasattr(value, "isoformat") else ""

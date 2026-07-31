"""Canonical execution dispatch, provider boundary and bounded repair control."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Protocol

from django.conf import settings
from django.db import IntegrityError, OperationalError, models, transaction
from django.utils import timezone

from .delivery import delivery_projection, verify_and_publish_delivery
from .execution_activity import console_line
from .models import (
    ContractConsumption,
    ExecutionCancellation,
    ExecutionContract,
    ExecutionJob,
    ExecutionProgressEvent,
    ExecutionRun,
    ExecutionStartRequest,
    ExecutionWorkspace,
    KnowledgeContextUse,
)
from .models import ExecutionProvider as ExecutionProviderRecord
from .provider_events import redact_value
from .providers import (
    CodexCliAdapter,
    ProviderStart,
    adapter_for,
    check_health,
    mark_runtime_unavailable,
    select_provider,
)
from .services import project_repository_root
from .workspace import WorkspaceError, WorkspaceManager

ACTIVE_STATES = {
    ExecutionRun.Lifecycle.REQUESTED,
    ExecutionRun.Lifecycle.STARTING,
    ExecutionRun.Lifecycle.RUNNING,
    ExecutionRun.Lifecycle.CANCELLING,
    ExecutionRun.Lifecycle.VALIDATING,
    ExecutionRun.Lifecycle.REPAIRING,
    ExecutionRun.Lifecycle.DOCUMENTING,
    ExecutionRun.Lifecycle.CLOSING,
}
MAX_PROVIDER_START_ATTEMPTS = 2
PROVIDER_START_RECOVERY_DELAY_SECONDS = 15


def lifecycle_status_projection(run: ExecutionRun) -> dict[str, object]:
    """Return the one safe lifecycle projection for API and administration.

    It deliberately exposes ownership as booleans, never a worker identity or
    PID.  Every caller observes the same durable run, job, workspace and
    activity state rather than reconstructing a process-local view.
    """
    from .execution_activity import heartbeat_projection

    job = ExecutionJob.objects.filter(run=run).first()
    workspace = ExecutionWorkspace.objects.filter(run=run).first()
    return {
        "execution_token": str(run.token),
        "status": run.lifecycle,
        "phase": run.current_phase,
        "provider": run.provider_name,
        "provider_execution_id": run.provider_execution_id,
        "attempt_count": run.attempt_count,
        "current_blocker": run.current_blocker,
        "heartbeat": heartbeat_projection(run),
        "queue": {
            "status": job.status if job else None,
            "lease_owner_present": bool(job and job.lease_owner),
            "lease_expires_at": job.lease_expires_at.isoformat()
            if job and job.lease_expires_at
            else None,
            "last_heartbeat_at": job.last_heartbeat_at.isoformat()
            if job and job.last_heartbeat_at
            else None,
            "fencing_token": job.lease_fencing_token if job else None,
            "recovery_attempts": job.recovery_attempts if job else None,
            "next_recovery_at": job.next_recovery_at.isoformat()
            if job and job.next_recovery_at
            else None,
            "recovery_action": job.provider_attempt_metadata.get("recovery_action")
            if job
            else None,
        },
        "workspace": {
            "status": workspace.status if workspace else None,
            "provider_pid_present": bool(workspace and workspace.provider_pid),
            "retention_until": workspace.retention_until.isoformat()
            if workspace and workspace.retention_until
            else None,
            "retention_reason": workspace.retention_reason if workspace else None,
        },
        "evidence": {
            "evidence_root": run.evidence_root,
            "final_commit_sha": run.final_commit_sha,
            "terminal_state": run.terminal_state,
        },
        "delivery": delivery_projection(run),
    }


# These are immutable-authority failures.  Re-running the same claimed job
# cannot make them true, so retrying would only reclaim it forever.  Keep this
# intentionally closed: unknown failures still surface to the worker process
# instead of being mistaken for safe job-level rejections.
NON_RETRYABLE_EXECUTION_FAILURE_PREFIXES = (
    "CONTRACT_INTEGRITY_FAILURE:",
    "CONTRACT_AUTHORITY_REQUIRED",
    "CONTRACT_NOT_CONSUMED",
    "CONSUMPTION_RECEIPT_REQUIRED",
    "EXECUTION_REQUEST_CONTRACT_MISMATCH",
    "EXECUTION_RUN_NOT_ACTIVE",
    "LEGACY_CONTRACT_NOT_EXECUTABLE",
)


def enqueue_run(
    contract: ExecutionContract,
    request: ExecutionStartRequest,
    platform_root: Path,
    audit_event_id: int | None = None,
) -> ExecutionJob:
    """Persist provider work; a web request never starts the provider itself."""
    if contract.lifecycle not in {
        ExecutionContract.Lifecycle.CONSUMED,
        ExecutionContract.Lifecycle.RUNNING,
    }:
        raise ValueError("CONTRACT_NOT_CONSUMED")
    receipt = ContractConsumption.objects.filter(contract=contract).first()
    if receipt is None:
        raise ValueError("CONSUMPTION_RECEIPT_REQUIRED")
    from .contracts import validate_issued_execution_contract

    validate_issued_execution_contract(contract, platform_root)
    if "orchestration" in contract.payload:
        from .orchestration_gate import assert_contract_authorized

        assert_contract_authorized(contract)
    workspace_root = project_repository_root(contract.project, platform_root)
    execution = contract.payload["execution"]
    with transaction.atomic():
        run, created = ExecutionRun.objects.get_or_create(
            start_request=request,
            defaults={
                "contract": contract,
                "repository": contract.payload["project"]["repository"],
                "branch": execution["target_branch"],
                "baseline_commit": execution["baseline_commit"],
                "contract_hash": contract.contract_hash,
                "workspace_identifier": str(workspace_root),
                "provider_name": receipt.provider_identity,
                "audit_event_id": audit_event_id,
                "lifecycle": ExecutionRun.Lifecycle.REQUESTED,
                "current_phase": "QUEUED",
                "evidence_root": contract.payload["evidence"]["root"],
                "orchestration_session": contract.orchestration_session,
            },
        )
        if run.contract_id != contract.pk:
            raise ValueError("EXECUTION_REQUEST_CONTRACT_MISMATCH")
        job, job_created = ExecutionJob.objects.get_or_create(run=run)
        try:
            context_use = contract.knowledge_context_use
        except KnowledgeContextUse.DoesNotExist:
            # Contracts issued before Sprint 3 do not have a durable context binding.
            pass
        else:
            if context_use.execution_run_id != run.id:
                context_use.execution_run = run
                context_use.save(update_fields=["execution_run"])
    if created or job_created:
        add_event(run, "EXECUTION_ENQUEUED", job_token=str(job.token))
    return job


def claim_next_job(worker_id: str, lease_seconds: int) -> ExecutionJob | None:
    """Atomically lease queued work, including work abandoned by a dead worker."""
    if not worker_id or lease_seconds <= 0:
        raise ValueError("INVALID_WORKER_LEASE")
    now = timezone.now()
    with transaction.atomic():
        job = (
            ExecutionJob.objects.select_for_update()
            .filter(
                status__in=[
                    ExecutionJob.Status.QUEUED,
                    ExecutionJob.Status.LEASED,
                    ExecutionJob.Status.RECOVERING,
                ]
            )
            .filter(run__lifecycle__in=ACTIVE_STATES)
            .filter(
                models.Q(status=ExecutionJob.Status.QUEUED)
                | models.Q(status=ExecutionJob.Status.LEASED, lease_expires_at__lt=now)
                | models.Q(
                    status=ExecutionJob.Status.RECOVERING, next_recovery_at__lte=now
                )
            )
            .order_by("created_at", "id")
            .first()
        )
        if job is None:
            return None
        reclaimed = job.status in {
            ExecutionJob.Status.LEASED,
            ExecutionJob.Status.RECOVERING,
        }
        job.status = ExecutionJob.Status.LEASED
        job.lease_owner = worker_id
        job.lease_expires_at = now + timedelta(seconds=lease_seconds)
        job.last_heartbeat_at = now
        job.lease_fencing_token += 1
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "last_heartbeat_at",
                "lease_fencing_token",
                "updated_at",
            ]
        )
    add_event(
        job.run,
        "WORKER_LEASE_RECLAIMED" if reclaimed else "WORKER_LEASE_ACQUIRED",
        worker=worker_id,
        fencing_token=job.lease_fencing_token,
    )
    return job


def heartbeat_job(
    job: ExecutionJob, worker_id: str, lease_seconds: int
) -> ExecutionJob:
    """Renew only the lease held by this worker and record durable liveness."""
    expected_fencing_token = job.lease_fencing_token
    now = timezone.now()
    with transaction.atomic():
        job = ExecutionJob.objects.select_for_update().get(pk=job.pk)
        if job.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            job.status
            not in {
                ExecutionJob.Status.LEASED,
                ExecutionJob.Status.STARTED,
            }
            or job.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        job.last_heartbeat_at = now
        job.lease_expires_at = now + timedelta(seconds=lease_seconds)
        job.save(update_fields=["last_heartbeat_at", "lease_expires_at", "updated_at"])
    add_event(job.run, "WORKER_HEARTBEAT", worker=worker_id)
    return job


def is_non_retryable_execution_failure(error: ValueError) -> bool:
    """Return whether a claimed job has permanently invalid authority.

    This deliberately does not classify lease ownership, provider readiness,
    or unknown runtime errors.  Those conditions require their existing
    recovery or operator paths and must never be silently converted to a
    rejection.
    """
    return str(error).startswith(NON_RETRYABLE_EXECUTION_FAILURE_PREFIXES)


def reject_claimed_job(
    job: ExecutionJob, worker_id: str, error: ValueError
) -> ExecutionJob:
    """Durably reject one invalid claimed job without starting a provider."""
    if not is_non_retryable_execution_failure(error):
        raise ValueError("REJECTION_REQUIRES_NON_RETRYABLE_EXECUTION_FAILURE")
    reason = str(error)
    expected_fencing_token = job.lease_fencing_token
    now = timezone.now()
    with transaction.atomic():
        locked_job = (
            ExecutionJob.objects.select_for_update()
            .select_related("run", "run__contract")
            .get(pk=job.pk)
        )
        if locked_job.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            locked_job.status != ExecutionJob.Status.LEASED
            or locked_job.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        run = locked_job.run
        inactive_run = reason == "EXECUTION_RUN_NOT_ACTIVE"
        evidence = {
            "recorded_at": now.isoformat(),
            "classification": (
                "RUN_LIFECYCLE_RACE_CONVERGED"
                if inactive_run
                else "NON_RETRYABLE_CONTRACT_OR_GOVERNANCE_FAILURE"
            ),
            "reason": reason,
            "retryable": False,
            "worker": worker_id,
            "contract_id": run.contract_id,
            "contract_hash": run.contract_hash,
            "provider_started": False,
        }
        locked_job.status = (
            ExecutionJob.Status.COMPLETED
            if inactive_run and run.lifecycle == ExecutionRun.Lifecycle.COMPLETED
            else ExecutionJob.Status.REJECTED
        )
        locked_job.lease_owner = ""
        locked_job.lease_expires_at = None
        locked_job.next_recovery_at = None
        locked_job.reconciliation_evidence = [
            *locked_job.reconciliation_evidence,
            evidence,
        ]
        locked_job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "next_recovery_at",
                "reconciliation_evidence",
                "updated_at",
            ]
        )
        if inactive_run:
            add_event(
                run,
                "WORKER_RUN_LIFECYCLE_RACE_CONVERGED",
                worker=worker_id,
                lifecycle=run.lifecycle,
            )
            return locked_job

        run.lifecycle = ExecutionRun.Lifecycle.FAILED_GOVERNANCE
        run.current_phase = "CONTRACT_REJECTED"
        run.current_blocker = {
            "category": "non-retryable contract or governance failure",
            "reason": reason,
            "evidence": evidence,
        }
        run.terminal_state = "REJECTED — NON-RETRYABLE CONTRACT INTEGRITY FAILURE"
        run.ended_at = now
        run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "current_blocker",
                "terminal_state",
                "ended_at",
                "updated_at",
            ]
        )
    add_event(
        run,
        "EXECUTION_JOB_REJECTED",
        **evidence,
    )
    return locked_job


def fail_claimed_job(job: ExecutionJob, worker_id: str, reason: str) -> ExecutionJob:
    """Terminalize one execution failure while keeping the worker available."""
    expected_fencing_token = job.lease_fencing_token
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
        if locked.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            locked.status != ExecutionJob.Status.LEASED
            or locked.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        locked.status = ExecutionJob.Status.FAILED
        locked.lease_owner = ""
        locked.lease_expires_at = None
        locked.save(
            update_fields=["status", "lease_owner", "lease_expires_at", "updated_at"]
        )
        locked.run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
        locked.run.current_phase = "WORKSPACE_FAILED"
        locked.run.current_blocker = {
            "category": "WORKSPACE_PROVISIONING_FAILED",
            "reason": reason,
        }
        locked.run.ended_at = timezone.now()
        locked.run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "current_blocker",
                "ended_at",
                "updated_at",
            ]
        )
    add_event(locked.run, "WORKSPACE_PROVISIONING_FAILED", reason=reason)
    return locked


def requeue_provider_start_failure(job: ExecutionJob, worker_id: str) -> ExecutionJob:
    """Return a provider-free start failure to the durable queue once.

    ``start_run`` records a failed provider launch before it raises so the
    incident is visible even if the worker process exits.  The worker must then
    release its lease and restore an active lifecycle; otherwise a repaired
    provider can never claim the same governed run.  Keep the retry budget on
    the durable run and fail closed after it is exhausted.
    """
    expected_fencing_token = job.lease_fencing_token
    now = timezone.now()
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
        if locked.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            locked.status != ExecutionJob.Status.LEASED
            or locked.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        run = locked.run
        if (
            run.lifecycle != ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
            or run.provider_execution_id
        ):
            raise ValueError("PROVIDER_START_RECOVERY_NOT_ALLOWED")
        failure = (
            run.current_blocker.get("evidence", "EXECUTOR_START_FAILED")
            if isinstance(run.current_blocker, dict)
            else "EXECUTOR_START_FAILED"
        )
        locked.lease_owner = ""
        locked.lease_expires_at = None
        if run.attempt_count >= MAX_PROVIDER_START_ATTEMPTS:
            locked.status = ExecutionJob.Status.FAILED
            locked.next_recovery_at = None
            locked.save(
                update_fields=[
                    "status",
                    "lease_owner",
                    "lease_expires_at",
                    "next_recovery_at",
                    "updated_at",
                ]
            )
            add_event(
                run,
                "PROVIDER_START_RETRY_EXHAUSTED",
                attempts=run.attempt_count,
                reason=str(failure)[:100],
            )
            return locked
        locked.status = ExecutionJob.Status.RECOVERING
        locked.recovery_attempts += 1
        locked.next_recovery_at = now + timedelta(
            seconds=PROVIDER_START_RECOVERY_DELAY_SECONDS
        )
        locked.provider_attempt_metadata = {
            **locked.provider_attempt_metadata,
            "recovery_action": "RETRY_PROVIDER_START",
            "last_provider_start_failure": str(failure)[:300],
        }
        locked.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "recovery_attempts",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
        run.lifecycle = ExecutionRun.Lifecycle.STARTING
        run.current_phase = "PROVIDER_RECOVERY_PENDING"
        run.current_blocker = {
            "category": "provider start recovery pending",
            "evidence": str(failure)[:300],
            "retry_at": locked.next_recovery_at.isoformat(),
        }
        run.ended_at = None
        run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "current_blocker",
                "ended_at",
                "updated_at",
            ]
        )
    add_event(
        run,
        "PROVIDER_START_RECOVERY_QUEUED",
        recovery_attempt=locked.recovery_attempts,
        retry_at=locked.next_recovery_at.isoformat()
        if locked.next_recovery_at
        else None,
    )
    return locked


def defer_claimed_job_for_active_branch(
    job: ExecutionJob, worker_id: str
) -> ExecutionJob:
    """Release a lease when another governed run still owns the target branch.

    A branch conflict is a transient scheduling condition, not invalid
    authority and not a provider-start failure.  Leaving the job leased makes
    the recovery depend on lease expiry and can terminate a one-shot worker;
    instead persist a bounded-delay retry with explicit lifecycle evidence.
    """
    expected_fencing_token = job.lease_fencing_token
    now = timezone.now()
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
        if locked.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            locked.status != ExecutionJob.Status.LEASED
            or locked.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        locked.status = ExecutionJob.Status.RECOVERING
        locked.lease_owner = ""
        locked.lease_expires_at = None
        locked.next_recovery_at = now + timedelta(
            seconds=PROVIDER_START_RECOVERY_DELAY_SECONDS
        )
        locked.provider_attempt_metadata = {
            **locked.provider_attempt_metadata,
            "recovery_action": "WAIT_FOR_ACTIVE_BRANCH",
        }
        locked.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
        run = locked.run
        run.lifecycle = ExecutionRun.Lifecycle.STARTING
        run.current_phase = "WAITING_FOR_BRANCH"
        run.current_blocker = {
            "category": "active branch execution",
            "retry_at": locked.next_recovery_at.isoformat(),
        }
        run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "current_blocker",
                "updated_at",
            ]
        )
    add_event(
        run,
        "EXECUTION_BRANCH_CONFLICT_DEFERRED",
        retry_at=locked.next_recovery_at.isoformat()
        if locked.next_recovery_at
        else None,
    )
    return locked


def requeue_workspace_provisioning_failure(run: ExecutionRun) -> ExecutionJob:
    """Return one provider-free workspace failure to the durable worker queue."""
    with transaction.atomic():
        job = (
            ExecutionJob.objects.select_for_update().select_related("run").get(run=run)
        )
        locked_run = job.run
        if (
            job.status != ExecutionJob.Status.FAILED
            or locked_run.lifecycle != ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
            or locked_run.current_phase != "WORKSPACE_FAILED"
            or locked_run.provider_execution_id
        ):
            raise ValueError("WORKSPACE_FAILURE_REQUEUE_NOT_ALLOWED")
        job.status = ExecutionJob.Status.QUEUED
        job.lease_owner = ""
        job.lease_expires_at = None
        job.next_recovery_at = None
        job.provider_attempt_metadata = {
            **job.provider_attempt_metadata,
            "recovery_action": "RESTART_WORKSPACE_PROVISIONING",
        }
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
    add_event(
        locked_run,
        "WORKSPACE_PROVISIONING_REQUEUED",
        provider_started=False,
    )
    return job


class ExecutionProvider(Protocol):
    name: str

    def start(self, *, repository: Path, prompt: str) -> ProviderStart: ...
    def status(self, execution_id: str) -> str: ...
    def cancel(self, execution_id: str) -> None: ...


CodexCliProvider = CodexCliAdapter


def provider(identity: str | None = None) -> ExecutionProvider:
    """Return the explicitly selected operational provider; never fall back."""
    configured = getattr(settings, "BRIDGE_EXECUTOR_PROVIDER", "codex-cli")
    selected = identity or configured
    if selected != configured:
        raise ValueError("EXECUTOR_PROVIDER_UNAVAILABLE")
    return adapter_for(select_provider(selected))


def _safe_details(details: dict[str, object]) -> dict[str, object]:
    """Apply recursive redaction and bounded text retention before persistence."""
    safe = redact_value(details)
    return safe if isinstance(safe, dict) else {}


def add_event(
    run: ExecutionRun, event_type: str, **details: object
) -> ExecutionProgressEvent:
    provider_event_id = str(details.pop("provider_event_id", "") or "")[:255]
    if provider_event_id:
        existing = ExecutionProgressEvent.objects.filter(
            run=run, provider_event_id=provider_event_id
        ).first()
        if existing is not None:
            _terminalize_provider_event_if_needed(run, existing)
            return existing
    for attempt in range(3):
        try:
            with transaction.atomic():
                last = (
                    ExecutionProgressEvent.objects.select_for_update()
                    .filter(run=run)
                    .order_by("-sequence")
                    .first()
                )
                event = ExecutionProgressEvent.objects.create(
                    run=run,
                    sequence=1 if last is None else last.sequence + 1,
                    event_type=event_type,
                    details=_safe_details(details),
                    provider_event_id=provider_event_id or None,
                )
            break
        except IntegrityError:
            if provider_event_id:
                existing = ExecutionProgressEvent.objects.get(
                    run=run, provider_event_id=provider_event_id
                )
                _terminalize_provider_event_if_needed(run, existing)
                return existing
            raise
        except OperationalError:
            if attempt == 2:
                raise
            sleep(0.05 * (attempt + 1))
    if settings.AI_BRIDGE_DEV_EXECUTION_ACTIVITY:
        print(console_line(event), flush=True)
    _terminalize_provider_event_if_needed(run, event)
    return event


def _is_provider_terminal_event(event: ExecutionProgressEvent) -> bool:
    details = event.details if isinstance(event.details, dict) else {}
    return event.event_type == "PROVIDER_COMPLETED" or (
        event.event_type == "PROVIDER_OUTPUT"
        and details.get("activity_type") == "turn.completed"
    )


def _terminalize_provider_event_if_needed(
    run: ExecutionRun, event: ExecutionProgressEvent
) -> None:
    """Queue finalization for an exited provider exactly once.

    A terminal provider event is not canonical completion evidence. It hands
    the run to worker-owned finalization while retaining contract authority.
    """
    if not _is_provider_terminal_event(event):
        return
    with transaction.atomic():
        locked = (
            ExecutionRun.objects.select_for_update()
            .select_related("contract")
            .get(pk=run.pk)
        )
        job = ExecutionJob.objects.select_for_update().filter(run=locked).first()
        now = timezone.now()
        try:
            cancellation = locked.cancellation
        except ExecutionCancellation.DoesNotExist:
            cancellation = None
        if (
            locked.lifecycle == ExecutionRun.Lifecycle.CANCELLING
            and cancellation is not None
        ):
            _complete_cancellation_locked(
                locked, cancellation, job=job, acknowledged=True, now=now
            )
        elif (
            locked.lifecycle == ExecutionRun.Lifecycle.VALIDATING
            and locked.current_phase == "PROVIDER_COMPLETION_FINALIZATION_PENDING"
        ):
            # The provider may repeat its terminal notification.  The first
            # notification already owns the queued finalization job, so a
            # duplicate must not manufacture a second recovery/delivery path.
            return
        elif locked.lifecycle in ACTIVE_STATES:
            _queue_provider_completion_finalization_locked(
                locked,
                job,
                source_event=event.event_type,
                source_sequence=event.sequence,
                observed_at=now,
            )
            add_event(
                run,
                "PROVIDER_COMPLETION_FINALIZATION_QUEUED",
                outcome="FINALIZATION_QUEUED",
                source_event=event.event_type,
                source_sequence=event.sequence,
            )
            return
        else:
            return


def _queue_provider_completion_finalization_locked(
    run: ExecutionRun,
    job: ExecutionJob | None,
    *,
    source_event: str,
    source_sequence: int | None,
    observed_at: datetime,
) -> None:
    """Persist a worker-owned finalization step without cancelling authority."""
    run.lifecycle = ExecutionRun.Lifecycle.VALIDATING
    run.current_phase = "PROVIDER_COMPLETION_FINALIZATION_PENDING"
    run.current_blocker = {
        "category": "PROVIDER_COMPLETION_FINALIZATION",
        "reason": "provider exited before canonical completion was recorded",
        "source_event": source_event,
        "source_sequence": source_sequence,
    }
    run.terminal_state = ""
    run.ended_at = None
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "current_blocker",
            "terminal_state",
            "ended_at",
            "updated_at",
        ]
    )
    workspace = ExecutionWorkspace.objects.select_for_update().filter(run=run).first()
    if workspace is not None:
        workspace.status = ExecutionWorkspace.Status.VALIDATING
        workspace.provider_pid = None
        workspace.save(update_fields=["status", "provider_pid", "updated_at"])
    if job is not None:
        job.status = ExecutionJob.Status.QUEUED
        job.lease_owner = ""
        job.lease_expires_at = None
        job.next_recovery_at = None
        job.provider_attempt_metadata = {
            **job.provider_attempt_metadata,
            "recovery_action": "FINALIZE_PROVIDER_COMPLETION",
            "provider_terminal_event": source_event,
            "provider_terminal_sequence": source_sequence,
            "provider_terminal_observed_at": observed_at.isoformat(),
        }
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )


def _prompt(contract: ExecutionContract) -> str:
    """Give the provider the immutable, issued authority rather than a hint."""
    return (
        "Execute only this consumed AI Bridge contract. The JSON payload is the "
        "complete authority: do not expand its scope or modify unrelated work. "
        "Read the binding documents named by the contract before mutation, "
        "implement the approved intent, run every listed Release Gate, and write "
        "truthful evidence under the contract evidence root; never expose "
        "credentials. Do not claim completion unless the repository state and "
        "evidence support it.\n\n"
        "ISSUED_CONTRACT_JSON:\n"
        + json.dumps(contract.payload, ensure_ascii=False, indent=2, sort_keys=True)
    )


def start_run(
    contract: ExecutionContract,
    request: ExecutionStartRequest,
    platform_root: Path,
    audit_event_id: int | None = None,
    *,
    worker_id: str | None = None,
    lease_seconds: int = 120,
) -> ExecutionRun:
    """Persist authorization and ownership before an external start is active."""
    if contract.lifecycle not in {
        ExecutionContract.Lifecycle.CONSUMED,
        ExecutionContract.Lifecycle.RUNNING,
    }:
        raise ValueError("CONTRACT_NOT_CONSUMED")
    receipt = ContractConsumption.objects.filter(contract=contract).first()
    if receipt is None:
        raise ValueError("CONSUMPTION_RECEIPT_REQUIRED")
    from .contracts import validate_issued_execution_contract

    # Scope authority is published by AI Bridge, while the provider must run in
    # the Project registry's resolved workspace.  Keep those roots distinct.
    validate_issued_execution_contract(contract, platform_root)
    if "orchestration" in contract.payload:
        from .orchestration_gate import assert_contract_authorized

        assert_contract_authorized(contract)
    workspace_root = project_repository_root(contract.project, platform_root)
    execution = contract.payload["execution"]
    recoverable_run = (
        ExecutionRun.objects.filter(
            contract=contract,
            lifecycle__in=[
                ExecutionRun.Lifecycle.REQUESTED,
                ExecutionRun.Lifecycle.STARTING,
            ],
            provider_execution_id="",
        )
        .order_by("id")
        .first()
    )
    if recoverable_run is None:
        recoverable_run = (
            ExecutionRun.objects.filter(
                contract=contract,
                lifecycle=ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
                provider_execution_id="",
                attempt_count__lt=MAX_PROVIDER_START_ATTEMPTS,
            )
            .order_by("id")
            .first()
        )
    if recoverable_run is None:
        recoverable_run = (
            ExecutionRun.objects.filter(
                contract=contract,
                lifecycle=ExecutionRun.Lifecycle.REPAIRING,
                provider_execution_id="",
            )
            .order_by("id")
            .first()
        )
    if recoverable_run is None:
        # ``ExecutionRun.start_request`` is intentionally one-to-one: a
        # recovery must retain the original authorization and audit binding.
        # A cancelled provider has no active slot, so reuse that durable run
        # record instead of attempting to create a second row for the same
        # request.
        recoverable_run = (
            ExecutionRun.objects.filter(
                contract=contract,
                lifecycle=ExecutionRun.Lifecycle.CANCELLED,
            )
            .order_by("id")
            .first()
        )
    if (
        contract.lifecycle == ExecutionContract.Lifecycle.RUNNING
        and recoverable_run is None
    ):
        raise ValueError("CONTRACT_RUNNING_REQUIRES_RECOVERY")
    active_runs = ExecutionRun.objects.filter(
        contract__project=contract.project,
        branch=execution["target_branch"],
        lifecycle__in=ACTIVE_STATES,
    )
    if recoverable_run is not None:
        active_runs = active_runs.exclude(pk=recoverable_run.pk)
    if active_runs.exists():
        raise ValueError("CONFLICTING_ACTIVE_EXECUTION")
    selected_provider = provider(receipt.provider_identity)
    provider_record = ExecutionProviderRecord.objects.get(
        provider_id=receipt.provider_identity
    )
    if provider_record.first_used_at is None:
        provider_record.first_used_at = timezone.now()
        provider_record.save(update_fields=["first_used_at", "updated_at"])
    if recoverable_run is None:
        run = ExecutionRun.objects.create(
            contract=contract,
            start_request=request,
            repository=contract.payload["project"]["repository"],
            branch=execution["target_branch"],
            baseline_commit=execution["baseline_commit"],
            contract_hash=contract.contract_hash,
            workspace_identifier=str(workspace_root),
            provider_name=selected_provider.name,
            audit_event_id=audit_event_id,
            lifecycle=ExecutionRun.Lifecycle.STARTING,
            current_phase="STARTING",
            evidence_root=contract.payload["evidence"]["root"],
            orchestration_session=contract.orchestration_session,
            started_at=timezone.now(),
        )
        add_event(
            run, "PREFLIGHT_COMPLETED", branch=run.branch, baseline=run.baseline_commit
        )
    else:
        run = recoverable_run
        run.lifecycle = ExecutionRun.Lifecycle.STARTING
        run.current_phase = "STARTING"
        run.current_blocker = {}
        run.ended_at = None
        run.started_at = timezone.now()
        run.provider_execution_id = ""
        run.workspace_identifier = ""
        run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "current_blocker",
                "ended_at",
                "started_at",
                "provider_execution_id",
                "workspace_identifier",
                "updated_at",
            ]
        )
        add_event(
            run, "START_RECOVERED", reason="resuming persisted queued or blocked run"
        )

    try:
        context_use = contract.knowledge_context_use
    except KnowledgeContextUse.DoesNotExist:
        # Contracts issued before Sprint 3 do not have a durable context binding.
        pass
    else:
        if context_use.execution_run_id != run.id:
            context_use.execution_run = run
            context_use.save(update_fields=["execution_run"])

    manager = WorkspaceManager()
    try:
        add_event(run, "WORKSPACE_REQUESTED")
        add_event(run, "WORKSPACE_PROVISIONING_STARTED")
        workspace = manager.provision(run)
        if getattr(workspace, "_was_reused", False):
            add_event(run, "WORKSPACE_REUSED", workspace_id=str(workspace.token))
        add_event(run, "WORKSPACE_REPOSITORY_READY", workspace_id=str(workspace.token))
        add_event(run, "WORKSPACE_VENV_READY", workspace_id=str(workspace.token))
        add_event(
            run, "WORKSPACE_DEPENDENCIES_READY", workspace_id=str(workspace.token)
        )
        add_event(run, "WORKSPACE_DATABASE_READY", workspace_id=str(workspace.token))
        add_event(
            run,
            "APPLICATION_DATABASE_CREATED",
            workspace_id=str(workspace.token),
        )
        add_event(run, "APPLICATION_MIGRATED", workspace_id=str(workspace.token))
        seed_state = getattr(workspace, "seed_state", {})
        add_event(
            run,
            "APPLICATION_SEEDED"
            if seed_state.get("status") == "APPLIED"
            else "APPLICATION_SEED_SKIPPED",
            workspace_id=str(workspace.token),
        )
        services = getattr(workspace, "runtime_services", [])
        add_event(
            run,
            "RUNTIME_SERVICES_STARTED" if services else "RUNTIME_SERVICES_SKIPPED",
            workspace_id=str(workspace.token),
        )
        descriptor = manager.descriptor(workspace, run)
        add_event(run, "WORKSPACE_PREFLIGHT_PASSED", workspace_id=str(workspace.token))
        add_event(run, "WORKSPACE_READY", workspace_id=str(workspace.token))
    except WorkspaceError as exc:
        add_event(run, "WORKSPACE_PROVISIONING_FAILED", reason=str(exc))
        raise ValueError("WORKSPACE_PROVISIONING_FAILED") from exc

    started: ProviderStart | None = None
    failure: Exception | None = None
    for attempt in range(1, MAX_PROVIDER_START_ATTEMPTS + 1):
        run.attempt_count += 1
        run.save(update_fields=["attempt_count", "updated_at"])
        try:
            readiness = check_health(provider_record)
            if readiness["status"] != "HEALTHY":
                raise ValueError("CODEX_RUNTIME_NOT_READY")
            start_with_runtime_activity = getattr(
                selected_provider, "start_with_runtime_activity", None
            )
            start_with_activity = getattr(
                selected_provider, "start_with_activity", None
            )
            if callable(start_with_runtime_activity) or callable(start_with_activity):
                add_event(
                    run,
                    "PROVIDER_STARTED",
                    provider=run.provider_name,
                    message="Codex provider launch started",
                )

                def callback(details: dict[str, object]) -> None:
                    projected = dict(details)
                    event_type = str(projected.pop("event_type", "PROVIDER_MESSAGE"))
                    add_event(
                        run, "PROVIDER_ACTIVITY_RECEIVED", activity_type=event_type
                    )
                    add_event(run, event_type, **projected)
                    if event_type == "FILE_CHANGED":
                        add_event(run, "SOURCE_TREE_CHANGED", **projected)
                    elif event_type == "TEST_STARTED":
                        add_event(run, "VALIDATION_STARTED", **projected)
                    elif event_type == "TEST_RESULT":
                        add_event(run, "VALIDATION_COMPLETED", **projected)
                    if worker_id:
                        try:
                            heartbeat_job(
                                ExecutionJob.objects.get(run=run),
                                worker_id,
                                lease_seconds,
                            )
                        except (ExecutionJob.DoesNotExist, ValueError):
                            # The callback can outlive a completed or recovered job.
                            pass

                if callable(start_with_runtime_activity):
                    started = start_with_runtime_activity(
                        runtime=descriptor,
                        prompt=_prompt(contract),
                        activity_callback=callback,
                    )
                elif callable(start_with_activity):
                    started = start_with_activity(
                        repository=Path(str(descriptor["repository_root"])),
                        prompt=_prompt(contract),
                        activity_callback=callback,
                    )
                else:
                    raise ValueError("PROVIDER_ACTIVITY_START_UNAVAILABLE")
            else:
                start_with_runtime = getattr(
                    selected_provider, "start_with_runtime", None
                )
                if callable(start_with_runtime):
                    started = start_with_runtime(
                        runtime=descriptor, prompt=_prompt(contract)
                    )
                else:
                    # Test and third-party legacy adapters remain supported while
                    # the canonical Codex adapter consumes the full descriptor.
                    started = selected_provider.start(
                        repository=Path(str(descriptor["repository_root"])),
                        prompt=_prompt(contract),
                    )
            break
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            failure = exc
            retryable = str(exc) in {
                "CODEX_SUBPROCESS_EXITED_EARLY",
                "CODEX_RUNTIME_EXECUTABLE_UNAVAILABLE",
            }
            if retryable and attempt < MAX_PROVIDER_START_ATTEMPTS:
                add_event(
                    run,
                    "PROVIDER_START_RETRYING",
                    attempt=attempt,
                    reason=str(exc)[:100],
                )
                continue
            break
    if started is None:
        assert failure is not None
        failure_text = str(failure)
        mark_runtime_unavailable(provider_record, failure_text)
        run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
        run.current_blocker = {
            "category": "unavailable external input",
            "question": "Restore Codex provider access.",
            "evidence": failure_text[:300],
        }
        run.ended_at = timezone.now()
        run.save(
            update_fields=["lifecycle", "current_blocker", "ended_at", "updated_at"]
        )
        add_event(
            run,
            "PROVIDER_FAILURE",
            classification="unavailable external input",
            reason=failure_text[:100],
            readiness_invalidated=True,
        )
        manager.retain(workspace, run)
        add_event(run, "WORKSPACE_RETAINED", workspace_id=str(workspace.token))
        raise ValueError("EXECUTOR_START_FAILED") from failure
    run.provider_execution_id = started.execution_id
    run.workspace_identifier = started.workspace_identifier
    run.lifecycle = ExecutionRun.Lifecycle.RUNNING
    run.current_phase = "EXECUTING"
    run.save(
        update_fields=[
            "provider_execution_id",
            "workspace_identifier",
            "lifecycle",
            "current_phase",
            "updated_at",
        ]
    )
    manager.mark_in_use(
        workspace,
        int(started.execution_id) if started.execution_id.isdigit() else None,
    )
    add_event(
        run,
        "EXECUTOR_STARTED",
        provider=run.provider_name,
        execution_id=started.execution_id,
    )
    add_event(run, "EXECUTION_ACTIVITY_STARTED", message="provider process is running")
    contract.lifecycle = ExecutionContract.Lifecycle.RUNNING
    contract.save(update_fields=["lifecycle"])
    return run


def execute_claimed_job(
    job: ExecutionJob, worker_id: str, platform_root: Path
) -> ExecutionRun:
    """Run a claimed job from the independent worker process only."""
    expected_fencing_token = job.lease_fencing_token
    with transaction.atomic():
        job = (
            ExecutionJob.objects.select_for_update()
            .select_related("run", "run__contract")
            .get(pk=job.pk)
        )
        if job.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if job.status != ExecutionJob.Status.LEASED or job.lease_owner != worker_id:
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        if job.run.lifecycle not in ACTIVE_STATES:
            raise ValueError("EXECUTION_RUN_NOT_ACTIVE")
    action = job.provider_attempt_metadata.get("recovery_action")
    if action == "FINALIZE_PROVIDER_COMPLETION":
        return finalize_provider_completion(job, worker_id)
    if action == "REATTACH":
        job.status = ExecutionJob.Status.STARTED
        job.provider_attempt_metadata = {
            **job.provider_attempt_metadata,
            "recovery_action": "REATTACHED",
        }
        job.save(update_fields=["status", "provider_attempt_metadata", "updated_at"])
        add_event(
            job.run,
            "WORKER_REATTACHED_TO_PROVIDER_EXECUTION",
            worker=worker_id,
            provider=job.run.provider_name,
            provider_execution_id=job.run.provider_execution_id,
        )
        return job.run
    run = start_run(
        job.run.contract,
        job.run.start_request,
        platform_root,
        worker_id=worker_id,
    )
    job.status = ExecutionJob.Status.STARTED
    job.provider_attempt_metadata = {
        "attempt_count": run.attempt_count,
        "provider_execution_id": run.provider_execution_id,
        "started_at": run.started_at.isoformat() if run.started_at else None,
    }
    job.save(update_fields=["status", "provider_attempt_metadata", "updated_at"])
    add_event(run, "WORKER_DISPATCH_COMPLETED", worker=worker_id)
    return run


def finalize_provider_completion(job: ExecutionJob, worker_id: str) -> ExecutionRun:
    """Inspect an exited provider workspace and queue authoritative recovery.

    This deliberately does not infer delivery, deployment, or scope completion
    from an exit code.  A provider that omitted canonical completion evidence
    is resumed from the same accepted contract after its repository facts have
    been durably recorded.
    """
    expected_fencing_token = job.lease_fencing_token
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run", "run__contract")
            .get(pk=job.pk)
        )
        if locked.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            locked.status != ExecutionJob.Status.LEASED
            or locked.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        run = locked.run
        if run.lifecycle != ExecutionRun.Lifecycle.VALIDATING:
            raise ValueError("PROVIDER_FINALIZATION_NOT_PENDING")
        workspace = (
            ExecutionWorkspace.objects.select_for_update().filter(run=run).first()
        )
        facts: dict[str, object] = {"workspace_present": workspace is not None}
        if workspace is not None and Path(workspace.repository_path).is_dir():
            repository = Path(workspace.repository_path)
            try:
                head = subprocess.run(
                    ["git", "-C", str(repository), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=False,
                ).stdout.strip()
                changed = subprocess.run(
                    ["git", "-C", str(repository), "status", "--porcelain"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=False,
                ).stdout.splitlines()
                facts.update(
                    {
                        "repository_inspected": True,
                        "head": head,
                        "dirty_entry_count": len(changed),
                        # A provider terminal notification does not prove a
                        # delivery.  Preserve the distinct no-change result
                        # so recovery never invents a commit or receipt.
                        "provider_outcome": (
                            "NO_CHANGE"
                            if head == run.baseline_commit and not changed
                            else "CANONICAL_COMPLETION_MISSING"
                        ),
                    }
                )
            except (OSError, subprocess.SubprocessError):
                facts.update(
                    {
                        "repository_inspected": False,
                        "inspection_error": "GIT_INSPECTION_FAILED",
                    }
                )
        else:
            facts.update(
                {
                    "repository_inspected": False,
                    "inspection_error": "WORKSPACE_REPOSITORY_UNAVAILABLE",
                }
            )
        if workspace is not None:
            workspace.status = ExecutionWorkspace.Status.RETAINED
            workspace.provider_pid = None
            workspace.retention_until = None
            workspace.retention_reason = "PROVIDER_COMPLETION_RECOVERY"
            workspace.save(
                update_fields=[
                    "status",
                    "provider_pid",
                    "retention_until",
                    "retention_reason",
                    "updated_at",
                ]
            )
        locked.status = ExecutionJob.Status.RECOVERING
        locked.lease_owner = ""
        locked.lease_expires_at = None
        locked.recovery_attempts += 1
        locked.next_recovery_at = timezone.now() + timedelta(
            seconds=PROVIDER_START_RECOVERY_DELAY_SECONDS
        )
        locked.provider_attempt_metadata = {
            **locked.provider_attempt_metadata,
            "recovery_action": "RESTART_FROM_AUTHORITY",
            "finalization_facts": facts,
        }
        locked.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "recovery_attempts",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
        run.lifecycle = ExecutionRun.Lifecycle.REPAIRING
        provider_outcome = facts.get("provider_outcome")
        run.current_phase = (
            "PROVIDER_COMPLETION_NO_CHANGE_RECOVERY_REQUIRED"
            if provider_outcome == "NO_CHANGE"
            else "PROVIDER_COMPLETION_RECOVERY_REQUIRED"
        )
        run.current_blocker = {
            "category": (
                "PROVIDER_NO_CHANGE_RESULT"
                if provider_outcome == "NO_CHANGE"
                else "PROVIDER_COMPLETION_EVIDENCE_MISSING"
            ),
            "reason": (
                "provider exited with an explicit no-change repository result; "
                "canonical completion, delivery, and deployment remain absent"
                if provider_outcome == "NO_CHANGE"
                else "provider exited without canonical completion, delivery, or "
                "deployment evidence"
            ),
            "repository_facts": facts,
            "retry_at": locked.next_recovery_at.isoformat(),
        }
        run.provider_execution_id = ""
        run.ended_at = None
        run.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "current_blocker",
                "provider_execution_id",
                "ended_at",
                "updated_at",
            ]
        )
    add_event(run, "PROVIDER_FINALIZATION_REPOSITORY_INSPECTED", **facts)
    if facts.get("provider_outcome") == "NO_CHANGE":
        add_event(
            run,
            "PROVIDER_COMPLETED_NO_CHANGE",
            outcome="NO_CHANGE",
            baseline_commit=run.baseline_commit,
        )
    add_event(
        run,
        "PROVIDER_COMPLETION_RECOVERY_QUEUED",
        retry_at=locked.next_recovery_at.isoformat(),
    )
    return run


def prepare_execution_cancellation(
    run: ExecutionRun, *, requested_by: str, reason: str
) -> ExecutionCancellation:
    """Persist a cancellation request before asking for confirmation."""
    with transaction.atomic():
        locked = ExecutionRun.objects.select_for_update().get(pk=run.pk)
        try:
            cancellation = locked.cancellation
        except ExecutionCancellation.DoesNotExist:
            cancellation = None
        if cancellation is not None:
            if (
                cancellation.requested_by != requested_by
                or cancellation.reason != reason
            ):
                raise ValueError("CANCELLATION_REQUEST_ALREADY_EXISTS")
            return cancellation
        cancellation = ExecutionCancellation.objects.create(
            run=locked, requested_by=requested_by, reason=reason
        )
    add_event(
        locked,
        "CANCELLATION_CONFIRMATION_REQUIRED",
        requested_by=requested_by,
        reason=reason,
    )
    return cancellation


def confirm_execution_cancellation(
    run: ExecutionRun, *, requested_by: str, confirmation_reference: str
) -> ExecutionCancellation:
    """Bind an authenticated Product Owner confirmation durably."""
    with transaction.atomic():
        locked = ExecutionRun.objects.select_for_update().get(pk=run.pk)
        try:
            cancellation = locked.cancellation
        except ExecutionCancellation.DoesNotExist as error:
            raise ValueError("CANCELLATION_CONFIRMATION_REQUIRED") from error
        if cancellation.requested_by != requested_by:
            raise ValueError("CANCELLATION_REQUESTER_MISMATCH")
        if cancellation.status == ExecutionCancellation.Status.CONFIRMATION_REQUIRED:
            cancellation.confirmation_reference = confirmation_reference
            cancellation.status = ExecutionCancellation.Status.CONFIRMED
            cancellation.save(
                update_fields=["confirmation_reference", "status", "updated_at"]
            )
        elif cancellation.confirmation_reference != confirmation_reference:
            raise ValueError("CANCELLATION_CONFIRMATION_MISMATCH")
        else:
            return cancellation
    add_event(
        locked, "CANCELLATION_CONFIRMED", confirmation_reference=confirmation_reference
    )
    return cancellation


def _complete_cancellation_locked(
    run: ExecutionRun,
    cancellation: ExecutionCancellation,
    *,
    job: ExecutionJob | None,
    acknowledged: bool,
    now: datetime | None = None,
) -> None:
    completed_at = now or timezone.now()
    run.lifecycle = ExecutionRun.Lifecycle.CANCELLED
    run.current_phase = "CANCELLED"
    run.current_blocker = {}
    run.terminal_state = "CANCELLED — PRODUCT OWNER REQUESTED"
    run.ended_at = completed_at
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "current_blocker",
            "terminal_state",
            "ended_at",
            "updated_at",
        ]
    )
    cancellation.status = ExecutionCancellation.Status.CANCELLED
    cancellation.completed_at = completed_at
    if acknowledged and cancellation.provider_acknowledged_at is None:
        cancellation.provider_acknowledged_at = completed_at
    cancellation.save(
        update_fields=[
            "status",
            "completed_at",
            "provider_acknowledged_at",
            "updated_at",
        ]
    )
    if job is not None:
        job.status = ExecutionJob.Status.FAILED
        job.lease_owner = ""
        job.lease_expires_at = None
        job.next_recovery_at = None
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "next_recovery_at",
                "updated_at",
            ]
        )
    contract = run.contract
    if contract.lifecycle == ExecutionContract.Lifecycle.RUNNING:
        contract.lifecycle = ExecutionContract.Lifecycle.CANCELLED
        contract.closure_state = run.terminal_state
        contract.completed_at = completed_at
        contract.save(update_fields=["lifecycle", "closure_state", "completed_at"])


def request_execution_cancellation(
    run: ExecutionRun, *, requested_by: str, reason: str, confirmation_reference: str
) -> tuple[ExecutionRun, str]:
    """Request provider cancellation only after durable confirmation."""
    with transaction.atomic():
        locked = (
            ExecutionRun.objects.select_for_update()
            .select_related("contract")
            .get(pk=run.pk)
        )
        try:
            cancellation = locked.cancellation
        except ExecutionCancellation.DoesNotExist as error:
            raise ValueError("CANCELLATION_CONFIRMATION_REQUIRED") from error
        if (
            cancellation.requested_by,
            cancellation.reason,
            cancellation.confirmation_reference,
        ) != (requested_by, reason, confirmation_reference):
            raise ValueError("CANCELLATION_CONFIRMATION_MISMATCH")
        if locked.lifecycle == ExecutionRun.Lifecycle.CANCELLED:
            return locked, "ALREADY_CANCELLED"
        if locked.lifecycle not in ACTIVE_STATES:
            cancellation.status = ExecutionCancellation.Status.ALREADY_TERMINAL
            cancellation.save(update_fields=["status", "updated_at"])
            return locked, "ALREADY_TERMINAL"
        locked.lifecycle = ExecutionRun.Lifecycle.CANCELLING
        locked.current_phase = "CANCELLING"
        locked.save(update_fields=["lifecycle", "current_phase", "updated_at"])
        cancellation.status = ExecutionCancellation.Status.PROVIDER_CANCELLING
        cancellation.save(update_fields=["status", "updated_at"])
    add_event(
        locked,
        "CANCELLATION_REQUESTED",
        requested_by=requested_by,
        reason=reason,
        confirmation_reference=confirmation_reference,
    )
    try:
        if (
            not locked.provider_execution_id
            or provider(locked.provider_name).status(locked.provider_execution_id)
            == "FINISHED"
        ):
            return reconcile_execution_cancellation(locked), "ALREADY_FINISHED"
        provider(locked.provider_name).cancel(locked.provider_execution_id)
    except OSError:
        add_event(
            locked, "CANCELLATION_PROVIDER_UNRESPONSIVE", provider=locked.provider_name
        )
        return locked, "CANCELLING"
    add_event(locked, "CANCELLATION_PROVIDER_REQUESTED", provider=locked.provider_name)
    return locked, "CANCELLING"


def reconcile_execution_cancellation(run: ExecutionRun) -> ExecutionRun:
    """Finish a pending cancellation after a provider exit or restart."""
    if run.lifecycle != ExecutionRun.Lifecycle.CANCELLING:
        return run
    if (
        run.provider_execution_id
        and provider(run.provider_name).status(run.provider_execution_id) != "FINISHED"
    ):
        return run
    with transaction.atomic():
        locked = (
            ExecutionRun.objects.select_for_update()
            .select_related("contract")
            .get(pk=run.pk)
        )
        if locked.lifecycle != ExecutionRun.Lifecycle.CANCELLING:
            return locked
        job = ExecutionJob.objects.select_for_update().filter(run=locked).first()
        _complete_cancellation_locked(
            locked, locked.cancellation, job=job, acknowledged=True
        )
    add_event(locked, "CANCELLATION_PROVIDER_ACKNOWLEDGED")
    add_event(locked, "EXECUTION_CANCELLED")
    add_event(locked, "CANCELLATION_EVIDENCE_COMPLETED")
    return locked


def cancel_run(
    run: ExecutionRun, *, approval_reference: str, phase: str = "CANCELLED"
) -> ExecutionRun:
    """Legacy internal cancellation boundary retained for remediation callers."""
    if run.lifecycle == ExecutionRun.Lifecycle.CANCELLED:
        return run
    if run.lifecycle not in {
        ExecutionRun.Lifecycle.RUNNING,
        ExecutionRun.Lifecycle.STARTING,
    }:
        raise ValueError("EXECUTION_NOT_CANCELLABLE")
    try:
        if provider(run.provider_name).status(run.provider_execution_id) != "FINISHED":
            provider(run.provider_name).cancel(run.provider_execution_id)
    except OSError as exc:
        raise ValueError("EXECUTION_PROVIDER_UNAVAILABLE") from exc
    run.lifecycle = ExecutionRun.Lifecycle.CANCELLED
    run.current_phase = phase
    run.save(update_fields=["lifecycle", "current_phase", "updated_at"])
    add_event(
        run,
        "EXECUTION_TIMED_OUT" if phase == "TIMED_OUT" else "EXECUTION_CANCELLED",
        approval=approval_reference,
    )
    return run


def complete_run(
    run: ExecutionRun, final_commit_sha: str, completion_data: dict[str, object]
) -> ExecutionRun:
    """Record completion only after the provider-owned run has actually run."""
    if run.lifecycle != ExecutionRun.Lifecycle.RUNNING:
        raise ValueError("RUN_NOT_RUNNING")
    required = {
        "execution_result",
        "gate_results",
        "evidence_manifest",
        "changed_files",
        "failure_classification",
    }
    missing = sorted(required - set(completion_data))
    if missing:
        raise ValueError("RUN_COMPLETION_EVIDENCE_REQUIRED:" + ",".join(missing))
    if (
        not isinstance(completion_data["execution_result"], str)
        or not isinstance(completion_data["gate_results"], dict)
        or not completion_data["gate_results"]
        or not isinstance(completion_data["evidence_manifest"], dict)
        or not completion_data["evidence_manifest"]
        or not isinstance(completion_data["changed_files"], list)
        or not isinstance(completion_data["failure_classification"], (str, type(None)))
    ):
        raise ValueError("RUN_COMPLETION_EVIDENCE_INVALID")
    audit = run.contract.payload.get("execution", {}).get("audit")
    if audit and audit.get("mutation_policy") == "READ_ONLY":
        allowed_prefix = run.evidence_root.rstrip("/") + "/"
        changed_files = completion_data["changed_files"]
        if any(
            not isinstance(path, str) or not path.startswith(allowed_prefix)
            for path in changed_files
        ):
            raise ValueError("READ_ONLY_AUDIT_MUTATION_REJECTED")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=run.workspace_identifier,
        check=False,
        capture_output=True,
        text=True,
    )
    if head.returncode or head.stdout.strip() != final_commit_sha:
        raise ValueError("RUN_FINAL_COMMIT_MISMATCH")
    delivery = verify_and_publish_delivery(run, final_commit_sha, completion_data)
    run.lifecycle = ExecutionRun.Lifecycle.COMPLETED
    run.current_phase = "COMPLETED"
    run.final_commit_sha = final_commit_sha
    # A verified execution is terminal.  Product Owner approval has already
    # authorized this scope; any later review is informational and must not
    # leave the execution lifecycle or scope actionable.
    run.terminal_state = "PASS"
    run.completion_data = completion_data
    run.ended_at = timezone.now()
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "final_commit_sha",
            "terminal_state",
            "completion_data",
            "ended_at",
            "updated_at",
        ]
    )
    try:
        workspace = run.workspace
    except ExecutionWorkspace.DoesNotExist:
        workspace = None
    if workspace is not None:
        manager = WorkspaceManager()
        mark_validating = getattr(manager, "mark_validating", None)
        if callable(mark_validating):
            mark_validating(workspace)
        shutdown_services = getattr(manager, "shutdown_services", None)
        if callable(shutdown_services):
            shutdown_services(workspace)
            add_event(
                run, "RUNTIME_SERVICES_STOPPED", workspace_id=str(workspace.token)
            )
        manager.retain(workspace, run)
        add_event(run, "WORKSPACE_RETAINED", workspace_id=str(workspace.token))
    add_event(run, "EXECUTION_COMPLETED", final_commit_sha=final_commit_sha)
    if delivery is not None:
        add_event(run, "DELIVERY_VERIFIED", remote_sha=delivery.remote_commit_sha)
    return run


def classify_failure(signature: str) -> str:
    text = signature.lower()
    if any(
        word in text for word in ("credential", "permission", "network", "provider")
    ):
        return "unavailable external input"
    if any(word in text for word in ("migration", "makemigrations")):
        return "migration defect"
    if any(word in text for word in ("ruff", "mypy", "lint", "type")):
        return "build/lint/type defect"
    if "business" in text or "product decision" in text:
        return "reserved Product Owner decision"
    return "repository or implementation defect"


def repair_failure(run: ExecutionRun, signature: str) -> str:
    """Record deterministic repair work; never changes gates or tests to force PASS."""
    classification = classify_failure(signature)
    if classification in {
        "reserved Product Owner decision",
        "unavailable external input",
    }:
        raise ValueError("ROUTINE_TECHNICAL_ESCALATION_REJECTED")
    run.attempt_count += 1
    run.lifecycle = ExecutionRun.Lifecycle.REPAIRING
    run.current_phase = "REPAIRING"
    run.save(
        update_fields=["attempt_count", "lifecycle", "current_phase", "updated_at"]
    )
    add_event(run, "ROOT_CAUSE_IDENTIFIED", classification=classification)
    add_event(run, "REPAIR_APPLIED", classification=classification)
    return classification


def record_gate_rerun(run: ExecutionRun, gate: str, passed: bool) -> ExecutionRun:
    """Persist a repair verification rerun on the canonical execution stream."""
    if run.lifecycle != ExecutionRun.Lifecycle.REPAIRING:
        raise ValueError("GATE_RERUN_REQUIRES_REPAIRING_RUN")
    run.gate_rerun_count += 1
    run.current_phase = "VALIDATING"
    run.save(update_fields=["gate_rerun_count", "current_phase", "updated_at"])
    add_event(run, "GATE_RERUN_STARTED", gate=gate)
    if not passed:
        run.current_phase = "REPAIRING"
        run.save(update_fields=["current_phase", "updated_at"])
        add_event(run, "GATE_RERUN_FAILED", gate=gate)
        return run
    add_event(run, "GATE_RERUN_PASSED", gate=gate)
    add_event(run, "REPAIR_VERIFIED", gate=gate)
    run.lifecycle = ExecutionRun.Lifecycle.RUNNING
    run.current_phase = "EXECUTING"
    run.save(update_fields=["lifecycle", "current_phase", "updated_at"])
    return run

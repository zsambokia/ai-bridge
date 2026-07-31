"""Durable reconciliation for interrupted execution jobs.

The controller never invents a scope, contract, or provider run.  It only
returns a stale, checkpointed job to the existing independent worker, or
records why recovery needs review.
"""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from datetime import datetime, timedelta
from typing import Callable

from django.db import transaction
from django.utils import timezone

from .execution import ACTIVE_STATES, add_event
from .models import (
    ExecutionContract,
    ExecutionJob,
    ExecutionRecoveryAttempt,
    ExecutionRun,
    ExecutionWorkspace,
)

MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_BACKOFF_SECONDS = 30
REQUIRED_CHECKPOINT_KEYS = {
    "baseline_commit",
    "working_tree_diff_hash",
    "completed_steps",
    "remaining_steps",
    "last_successful_gate",
    "modified_files",
    "latest_provider_summary",
    "next_recommended_action",
}

RECOVERY_CLASSIFICATIONS = {
    "HEALTHY_ACTIVE",
    "COMPLETED_PENDING_VALIDATION",
    "STALE_LEASE",
    "DEAD_PROVIDER_RECOVERABLE",
    "DEAD_PROVIDER_RESTARTABLE",
    "WORKSPACE_RECOVERABLE",
    "WORKSPACE_CORRUPT_REPLACEMENT_REQUIRED",
    "CONTRACT_INTEGRITY_FAILURE",
    "NON_RECOVERABLE_EXECUTION_FAILURE",
    "EXTERNAL_DEPENDENCY_BLOCKED",
    "TERMINAL_CLEANUP_PENDING",
}


def classify_execution_recovery(
    job: ExecutionJob, *, now: datetime | None = None
) -> dict[str, object]:
    """Classify recovery from durable facts, never a worker's memory.

    The structured result is also suitable for evidence and API consumers:
    every classification declares safe next actions, retry budget and whether
    Product Owner involvement is permitted (it is never required for a normal
    technical recovery).
    """
    observed = now or timezone.now()
    run = job.run
    try:
        workspace = run.workspace
    except ExecutionWorkspace.DoesNotExist:
        workspace = None
    facts: dict[str, object] = {
        "run_lifecycle": run.lifecycle,
        "job_status": job.status,
        "lease_expired": bool(job.lease_expires_at and job.lease_expires_at < observed),
        "checkpoint_resumable": checkpoint_is_resumable(job.checkpoint),
        "workspace_status": workspace.status if workspace else None,
        "provider_execution_present": bool(run.provider_execution_id),
    }
    evidence = [f"execution-run:{run.token}", f"execution-job:{job.token}"]
    retry_budget = max(0, MAX_RECOVERY_ATTEMPTS - job.recovery_attempts)
    classification = "HEALTHY_ACTIVE"
    actions = ["continue_monitoring"]
    if run.contract_hash != run.contract.contract_hash:
        classification, actions = (
            "CONTRACT_INTEGRITY_FAILURE",
            ["fail_closed", "preserve_evidence"],
        )
    elif run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT:
        classification, actions = (
            "EXTERNAL_DEPENDENCY_BLOCKED",
            ["preserve_evidence", "await_external_dependency"],
        )
    elif workspace and workspace.status == ExecutionWorkspace.Status.FAILED:
        classification, actions = (
            "WORKSPACE_CORRUPT_REPLACEMENT_REQUIRED",
            ["replace_workspace", "resume_from_checkpoint"],
        )
    elif (
        workspace
        and workspace.status
        in {
            ExecutionWorkspace.Status.RETAINED,
            ExecutionWorkspace.Status.CLEANUP_PENDING,
        }
        and run.lifecycle not in ACTIVE_STATES
    ):
        classification, actions = (
            "TERMINAL_CLEANUP_PENDING",
            ["retain_until_policy_expiry", "cleanup_when_safe"],
        )
    elif run.lifecycle == ExecutionRun.Lifecycle.VALIDATING:
        classification, actions = (
            "COMPLETED_PENDING_VALIDATION",
            ["resume_validation", "record_validation_evidence"],
        )
    elif job.recovery_attempts >= MAX_RECOVERY_ATTEMPTS:
        classification, actions = (
            "NON_RECOVERABLE_EXECUTION_FAILURE",
            ["fail_closed", "preserve_evidence"],
        )
    elif facts["lease_expired"]:
        classification, actions = (
            "STALE_LEASE",
            ["reclaim_with_new_fencing_token", "classify_provider"],
        )
    elif (
        run.provider_execution_id
        and workspace
        and not provider_pid_is_alive(workspace.provider_pid)
    ):
        classification = (
            "DEAD_PROVIDER_RECOVERABLE"
            if facts["checkpoint_resumable"]
            else "DEAD_PROVIDER_RESTARTABLE"
        )
        actions = [
            "reattach_or_resume"
            if facts["checkpoint_resumable"]
            else "restart_authorized_provider",
            "record_recovery_attempt",
        ]
    elif workspace is None or workspace.status in {
        ExecutionWorkspace.Status.REQUESTED,
        ExecutionWorkspace.Status.READY,
    }:
        classification, actions = (
            "WORKSPACE_RECOVERABLE",
            ["provision_or_reuse_workspace", "resume_authorized_run"],
        )
    return {
        "classification": classification,
        "facts": facts,
        "evidence_references": evidence,
        "permitted_next_actions": actions,
        "retry_budget_remaining": retry_budget,
        "product_owner_involvement": "FORBIDDEN_FOR_TECHNICAL_RECOVERY",
    }


def checkpoint_is_resumable(checkpoint: object) -> bool:
    return isinstance(checkpoint, dict) and REQUIRED_CHECKPOINT_KEYS <= set(checkpoint)


def provider_pid_is_alive(provider_pid: int | None) -> bool:
    """Check a locally-owned provider PID without trusting stale workspace data."""
    if not isinstance(provider_pid, int) or provider_pid <= 0:
        return False
    if os.name == "nt":
        # ``os.kill(pid, 0)`` does not reliably distinguish a terminated PID on
        # Windows.  Query the process handle instead, so dead provider PIDs
        # enter the bounded recovery path rather than terminalising a live run.
        process_query_limited_information = 0x1000
        synchronize = 0x00100000
        still_active = 259
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        handle = kernel32.OpenProcess(
            process_query_limited_information | synchronize,
            False,
            provider_pid,
        )
        if not handle:
            return False
        try:
            exit_code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == still_active
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(provider_pid, 0)
    except OSError:
        return False
    return True


def _converge_run_job_integrity(
    *, observed_at: datetime
) -> list[ExecutionRecoveryAttempt]:
    """Converge impossible run/job pairs before a worker can dispatch them.

    The run is the canonical lifecycle record.  A terminal run must never keep
    dispatchable work, while an active run with a terminal queue decision must
    fail closed rather than inventing a provider outcome.  Each mutation is
    recorded once, making repeated reconciliation idempotent.
    """
    decisions: list[ExecutionRecoveryAttempt] = []
    active_job_states = [
        ExecutionJob.Status.QUEUED,
        ExecutionJob.Status.LEASED,
        ExecutionJob.Status.STARTED,
        ExecutionJob.Status.RECOVERING,
    ]
    terminal_job_states = [
        ExecutionJob.Status.COMPLETED,
        ExecutionJob.Status.FAILED,
        ExecutionJob.Status.REJECTED,
    ]
    for candidate in (
        ExecutionJob.objects.select_related("run")
        .filter(status__in=active_job_states)
        .exclude(run__lifecycle__in=ACTIVE_STATES)
    ):
        with transaction.atomic():
            job = (
                ExecutionJob.objects.select_for_update()
                .select_related("run")
                .get(pk=candidate.pk)
            )
            run = job.run
            if job.status not in active_job_states or run.lifecycle in ACTIVE_STATES:
                continue
            evidence = {
                "observed_at": observed_at.isoformat(),
                "invariant": "terminal run has a terminal job",
                "run_lifecycle": run.lifecycle,
                "previous_job_status": job.status,
                "governed_transition": "TERMINAL_RUN_JOB_CONVERGED",
            }
            job.status = (
                ExecutionJob.Status.COMPLETED
                if run.lifecycle == ExecutionRun.Lifecycle.COMPLETED
                else ExecutionJob.Status.FAILED
            )
            job.lease_owner = ""
            job.lease_expires_at = None
            job.last_heartbeat_at = None
            job.next_recovery_at = None
            job.reconciliation_evidence = [*job.reconciliation_evidence, evidence][-20:]
            job.save(
                update_fields=[
                    "status",
                    "lease_owner",
                    "lease_expires_at",
                    "last_heartbeat_at",
                    "next_recovery_at",
                    "reconciliation_evidence",
                    "updated_at",
                ]
            )
            add_event(run, "RUN_JOB_DIVERGENCE_CONVERGED", **evidence)
            decisions.append(
                ExecutionRecoveryAttempt.objects.create(
                    job=job,
                    outcome=ExecutionRecoveryAttempt.Outcome.NO_ACTION,
                    reason="terminal run prevented stale queue dispatch",
                    evidence=evidence,
                )
            )

    for candidate in ExecutionJob.objects.select_related("run").filter(
        status__in=terminal_job_states,
        run__lifecycle__in=ACTIVE_STATES,
    ):
        with transaction.atomic():
            job = (
                ExecutionJob.objects.select_for_update()
                .select_related("run")
                .get(pk=candidate.pk)
            )
            run = job.run
            if (
                job.status not in terminal_job_states
                or run.lifecycle not in ACTIVE_STATES
            ):
                continue
            evidence = {
                "observed_at": observed_at.isoformat(),
                "invariant": "active run cannot have a terminal job",
                "run_lifecycle": run.lifecycle,
                "job_status": job.status,
                "governed_transition": "ACTIVE_RUN_FAIL_CLOSED",
            }
            run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
            run.current_phase = "RUN_JOB_DIVERGENCE"
            run.current_blocker = {
                "category": "RUN_JOB_DIVERGENCE",
                "reason": (
                    "terminal queue state lacks canonical run completion evidence"
                ),
                "evidence": evidence,
            }
            run.terminal_state = "BLOCKED â€” REQUIRED EXTERNAL INPUT UNAVAILABLE"
            run.ended_at = observed_at
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
            add_event(run, "RUN_JOB_DIVERGENCE_FAIL_CLOSED", **evidence)
            decisions.append(
                ExecutionRecoveryAttempt.objects.create(
                    job=job,
                    outcome=ExecutionRecoveryAttempt.Outcome.NO_ACTION,
                    reason="active run blocked pending missing terminal evidence",
                    evidence=evidence,
                )
            )
    return decisions


def record_checkpoint(
    *, job: ExecutionJob, checkpoint: dict[str, object]
) -> ExecutionJob:
    """Persist a resumable checkpoint and a durable audit event."""
    missing_keys = sorted(REQUIRED_CHECKPOINT_KEYS - set(checkpoint))
    if missing_keys:
        raise ValueError(
            "Execution checkpoint is missing required fields: "
            + ", ".join(missing_keys)
        )
    with transaction.atomic():
        locked_job = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
        locked_job.checkpoint = checkpoint
        locked_job.save(update_fields=["checkpoint", "updated_at"])
        add_event(
            locked_job.run,
            "EXECUTION_CHECKPOINT_RECORDED",
            job_id=locked_job.pk,
            checkpoint_keys=sorted(checkpoint),
        )
    return locked_job


def _terminalize_recovery_review_required(
    *, run: ExecutionRun, evidence: dict[str, object], observed_at: datetime
) -> None:
    """Make an unsafe-recovery decision non-active without losing its evidence.

    A review-required job cannot safely resume, but it must also not retain an
    active execution slot indefinitely.  The phase and blocker keep the review
    record discoverable while the lifecycle records a truthful terminal state.
    """
    run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    run.current_phase = "RECOVERY_REVIEW_REQUIRED"
    if not run.current_blocker:
        run.current_blocker = {
            "category": "RECOVERY_REVIEW_REQUIRED",
            "reason": "checkpoint missing, unsafe, or retry limit reached",
            "evidence": evidence,
        }
    run.terminal_state = "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"
    run.ended_at = observed_at
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
        "RECOVERY_REVIEW_LIFECYCLE_TERMINALIZED",
        **evidence,
        terminal_state=run.terminal_state,
    )


def _terminalize_finished_provider(
    *,
    run: ExecutionRun,
    job: ExecutionJob,
    evidence: dict[str, object],
    observed_at: datetime,
) -> None:
    """Reconcile a verified provider exit without inventing completion evidence."""
    run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    run.current_phase = "PROVIDER_TERMINALIZED"
    run.current_blocker = {
        "category": "PROVIDER_TERMINAL_EVENT",
        "reason": "provider was verified FINISHED before canonical completion",
        "evidence": evidence,
    }
    run.terminal_state = "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"
    run.ended_at = observed_at
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
    job.status = ExecutionJob.Status.FAILED
    job.lease_owner = ""
    job.lease_expires_at = None
    job.next_recovery_at = None
    contract = ExecutionContract.objects.select_for_update().get(pk=run.contract_id)
    if contract.lifecycle == ExecutionContract.Lifecycle.RUNNING:
        contract.lifecycle = ExecutionContract.Lifecycle.CANCELLED
        contract.closure_state = run.terminal_state
        contract.completed_at = observed_at
        contract.save(update_fields=["lifecycle", "closure_state", "completed_at"])
    add_event(
        run,
        "PROVIDER_TERMINAL_RECONCILED",
        **evidence,
        terminal_state=run.terminal_state,
    )


def reconcile_execution_jobs(
    *,
    provider_status: Callable[[str, str], str],
    process_is_alive: Callable[[int | None], bool] = provider_pid_is_alive,
    now: datetime | None = None,
) -> list[ExecutionRecoveryAttempt]:
    """Inspect stale work and make one durable, bounded recovery decision."""
    observed_at = now if now is not None else timezone.now()
    decisions = _converge_run_job_integrity(observed_at=observed_at)

    # Repair pre-existing review-required jobs created before lifecycle
    # terminalization was introduced.  This is deliberately idempotent: once
    # non-active, the job no longer appears in this governed remediation pass.
    review_candidates = ExecutionJob.objects.select_related("run").filter(
        status=ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED,
        run__lifecycle__in=ACTIVE_STATES,
    )
    for candidate in review_candidates:
        with transaction.atomic():
            job = (
                ExecutionJob.objects.select_for_update()
                .select_related("run")
                .get(pk=candidate.pk)
            )
            run = job.run
            if (
                job.status != ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED
                or run.lifecycle not in ACTIVE_STATES
            ):
                continue
            evidence = {
                "observed_at": observed_at.isoformat(),
                "recovery_review_required": True,
                "governed_transition": "TERMINALIZE_REVIEW_REQUIRED",
            }
            _terminalize_recovery_review_required(
                run=run, evidence=evidence, observed_at=observed_at
            )
            attempt = ExecutionRecoveryAttempt.objects.create(
                job=job,
                outcome=ExecutionRecoveryAttempt.Outcome.NO_ACTION,
                reason="review-required lifecycle terminalized without retry",
                evidence=evidence,
            )
            decisions.append(attempt)

    candidates = ExecutionJob.objects.select_related("run").filter(
        status__in=[ExecutionJob.Status.STARTED, ExecutionJob.Status.LEASED],
        run__lifecycle=ExecutionRun.Lifecycle.RUNNING,
    )
    for candidate in candidates:
        workspace = ExecutionWorkspace.objects.filter(run=candidate.run).first()
        provider_pid_missing = bool(
            workspace
            and workspace.status == ExecutionWorkspace.Status.IN_USE
            and workspace.provider_pid
            and not process_is_alive(workspace.provider_pid)
        )
        stale = (
            candidate.lease_expires_at is None
            or candidate.lease_expires_at <= observed_at
            or candidate.last_heartbeat_at is None
            or candidate.last_heartbeat_at <= observed_at - timedelta(seconds=120)
            or provider_pid_missing
        )
        if provider_pid_missing:
            provider_state = "MISSING"
        else:
            try:
                provider_state = provider_status(
                    candidate.run.provider_name, candidate.run.provider_execution_id
                )
            except (OSError, ValueError):
                # An unreachable provider is not terminal evidence.  Keep a live
                # worker untouched, while allowing the existing stale recovery
                # path to use its checkpointed authority.
                provider_state = "MISSING"
        if provider_state != "FINISHED" and not stale:
            continue
        with transaction.atomic():
            job = (
                ExecutionJob.objects.select_for_update()
                .select_related("run")
                .get(pk=candidate.pk)
            )
            if job.next_recovery_at and job.next_recovery_at > observed_at:
                continue
            run = job.run
            workspace = (
                ExecutionWorkspace.objects.select_for_update().filter(run=run).first()
            )
            if (
                workspace
                and workspace.status == ExecutionWorkspace.Status.IN_USE
                and workspace.provider_pid
                and not process_is_alive(workspace.provider_pid)
            ):
                provider_pid_missing = True
                provider_state = "MISSING"
                workspace.status = ExecutionWorkspace.Status.READY
                workspace.provider_pid = None
                workspace.save(update_fields=["status", "provider_pid", "updated_at"])
                add_event(
                    run,
                    "WORKSPACE_PROVIDER_PID_MISSING",
                    workspace_id=str(workspace.token),
                )
            evidence = {
                "observed_at": observed_at.isoformat(),
                "provider_state": provider_state,
                "lease_expires_at": job.lease_expires_at.isoformat()
                if job.lease_expires_at
                else None,
                "checkpoint_resumable": checkpoint_is_resumable(job.checkpoint),
                "workspace_status": workspace.status if workspace else None,
                "provider_pid_missing": provider_pid_missing,
            }
            classification = classify_execution_recovery(job, now=observed_at)
            evidence["recovery_classification"] = classification["classification"]
            evidence["permitted_next_actions"] = classification[
                "permitted_next_actions"
            ]
            if provider_state == "RUNNING":
                job.status = ExecutionJob.Status.QUEUED
                job.lease_owner = ""
                job.lease_expires_at = None
                job.next_recovery_at = None
                job.provider_attempt_metadata = {
                    **job.provider_attempt_metadata,
                    "recovery_action": "REATTACH",
                }
                outcome = ExecutionRecoveryAttempt.Outcome.REATTACH
                reason = "provider remains alive; a new worker may reattach"
                add_event(run, "RECOVERY_REATTACH_QUEUED", **evidence)
            elif provider_state == "FINISHED":
                _terminalize_finished_provider(
                    run=run,
                    job=job,
                    evidence=evidence,
                    observed_at=observed_at,
                )
                outcome = ExecutionRecoveryAttempt.Outcome.REVIEW_REQUIRED
                reason = "provider finished without canonical completion evidence"
            elif job.recovery_attempts < MAX_RECOVERY_ATTEMPTS:
                job.status = ExecutionJob.Status.RECOVERING
                job.recovery_attempts += 1
                job.next_recovery_at = observed_at + timedelta(
                    seconds=RECOVERY_BACKOFF_SECONDS * job.recovery_attempts
                )
                recovery_action = (
                    "RESUME_FROM_CHECKPOINT"
                    if checkpoint_is_resumable(job.checkpoint)
                    else "RESTART_FROM_AUTHORITY"
                )
                job.provider_attempt_metadata = {
                    **job.provider_attempt_metadata,
                    "recovery_action": recovery_action,
                    "recovery_reason": "provider unavailable",
                    "recovery_observed_at": observed_at.isoformat(),
                }
                run.lifecycle = ExecutionRun.Lifecycle.STARTING
                run.current_phase = "RECOVERING"
                run.provider_execution_id = ""
                run.current_blocker = {}
                run.save(
                    update_fields=[
                        "lifecycle",
                        "current_phase",
                        "provider_execution_id",
                        "current_blocker",
                        "updated_at",
                    ]
                )
                outcome = ExecutionRecoveryAttempt.Outcome.RECOVERING
                reason = (
                    "provider unavailable; resumable checkpoint verified"
                    if checkpoint_is_resumable(job.checkpoint)
                    else "provider unavailable; restarting same authoritative run"
                )
                add_event(
                    run,
                    "RECOVERY_CHECKPOINT_QUEUED"
                    if checkpoint_is_resumable(job.checkpoint)
                    else "RECOVERY_RETRY_QUEUED",
                    recovery_action=recovery_action,
                    **evidence,
                )
            else:
                job.status = ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED
                run.current_blocker = {
                    "category": "RECOVERY_REVIEW_REQUIRED",
                    "reason": "checkpoint missing, unsafe, or retry limit reached",
                    "evidence": evidence,
                }
                _terminalize_recovery_review_required(
                    run=run, evidence=evidence, observed_at=observed_at
                )
                outcome = ExecutionRecoveryAttempt.Outcome.REVIEW_REQUIRED
                reason = "provider unavailable and recovery cannot be verified safe"
                add_event(run, "RECOVERY_REVIEW_REQUIRED", **evidence)
            attempt = ExecutionRecoveryAttempt.objects.create(
                job=job, outcome=outcome, reason=reason, evidence=evidence
            )
            history = [
                *job.reconciliation_evidence,
                {"attempt": attempt.pk, **evidence, "outcome": outcome},
            ]
            job.reconciliation_evidence = history[-20:]
            job.save(
                update_fields=[
                    "status",
                    "lease_owner",
                    "lease_expires_at",
                    "last_heartbeat_at",
                    "recovery_attempts",
                    "next_recovery_at",
                    "provider_attempt_metadata",
                    "reconciliation_evidence",
                    "updated_at",
                ]
            )
            decisions.append(attempt)
    return decisions

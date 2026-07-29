"""Durable reconciliation for interrupted execution jobs.

The controller never invents a scope, contract, or provider run.  It only
returns a stale, checkpointed job to the existing independent worker, or
records why recovery needs review.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Callable

from django.db import transaction
from django.utils import timezone

from .execution import ACTIVE_STATES, add_event
from .models import ExecutionJob, ExecutionRecoveryAttempt, ExecutionRun

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


def checkpoint_is_resumable(checkpoint: object) -> bool:
    return isinstance(checkpoint, dict) and REQUIRED_CHECKPOINT_KEYS <= set(checkpoint)


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


def reconcile_execution_jobs(
    *,
    provider_status: Callable[[str, str], str],
    now: datetime | None = None,
) -> list[ExecutionRecoveryAttempt]:
    """Inspect stale work and make one durable, bounded recovery decision."""
    observed_at = now if now is not None else timezone.now()
    decisions: list[ExecutionRecoveryAttempt] = []

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
        stale = (
            candidate.lease_expires_at is None
            or candidate.lease_expires_at <= observed_at
            or candidate.last_heartbeat_at is None
            or candidate.last_heartbeat_at <= observed_at - timedelta(seconds=120)
        )
        if not stale:
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
            try:
                provider_state = provider_status(
                    run.provider_name, run.provider_execution_id
                )
            except (OSError, ValueError):
                # Provider interruption is recoverable input: only a verified
                # checkpoint may move this same authoritative run forward.
                provider_state = "MISSING"
            evidence = {
                "observed_at": observed_at.isoformat(),
                "provider_state": provider_state,
                "lease_expires_at": job.lease_expires_at.isoformat()
                if job.lease_expires_at
                else None,
                "checkpoint_resumable": checkpoint_is_resumable(job.checkpoint),
            }
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
            elif (
                checkpoint_is_resumable(job.checkpoint)
                and job.recovery_attempts < MAX_RECOVERY_ATTEMPTS
            ):
                job.status = ExecutionJob.Status.RECOVERING
                job.recovery_attempts += 1
                job.next_recovery_at = observed_at + timedelta(
                    seconds=RECOVERY_BACKOFF_SECONDS * job.recovery_attempts
                )
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
                reason = "provider unavailable; resumable checkpoint verified"
                add_event(run, "RECOVERY_CHECKPOINT_QUEUED", **evidence)
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
                    "recovery_attempts",
                    "next_recovery_at",
                    "provider_attempt_metadata",
                    "reconciliation_evidence",
                    "updated_at",
                ]
            )
            decisions.append(attempt)
    return decisions

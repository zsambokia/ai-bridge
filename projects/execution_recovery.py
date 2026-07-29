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

from .execution import add_event
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


def reconcile_execution_jobs(
    *,
    provider_status: Callable[[str, str], str],
    now: datetime | None = None,
) -> list[ExecutionRecoveryAttempt]:
    """Inspect stale work and make one durable, bounded recovery decision."""
    observed_at = now if now is not None else timezone.now()
    decisions: list[ExecutionRecoveryAttempt] = []
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
                run.current_phase = "RECOVERY_REVIEW_REQUIRED"
                run.current_blocker = {
                    "category": "RECOVERY_REVIEW_REQUIRED",
                    "reason": "checkpoint missing, unsafe, or retry limit reached",
                    "evidence": evidence,
                }
                run.save(
                    update_fields=["current_phase", "current_blocker", "updated_at"]
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

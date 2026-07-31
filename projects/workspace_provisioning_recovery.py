"""Recovery for a worker interrupted before workspace provisioning completes.

This is deliberately separate from provider reconciliation: a STARTING run has
not established a provider identity yet, so querying a provider cannot make a
safe recovery decision.  The durable queue job, lease and canonical run remain
the only authority needed to restart the same provisioning attempt.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone

from .execution import add_event
from .models import (
    ExecutionJob,
    ExecutionRecoveryAttempt,
    ExecutionRun,
    ExecutionWorkspace,
)

MAX_WORKSPACE_PROVISIONING_RECOVERY_ATTEMPTS = 3
WORKSPACE_PROVISIONING_RECOVERY_DELAY_SECONDS = 30
WORKER_HEARTBEAT_STALE_SECONDS = 120
PROVISIONING_PHASES = {
    "STARTING",
    "WORKSPACE_PROVISIONING",
    "WORKSPACE_RECOVERY_PENDING",
}


def _recovery_evidence(
    job: ExecutionJob,
    *,
    observed_at: datetime,
    reason: str,
    exception_type: str = "",
) -> dict[str, object]:
    return {
        "observed_at": observed_at.isoformat(),
        "reason": reason,
        "exception_type": exception_type,
        "previous_job_status": job.status,
        "previous_run_phase": job.run.current_phase,
        "lease_expires_at": (
            job.lease_expires_at.isoformat() if job.lease_expires_at else None
        ),
        "last_heartbeat_at": (
            job.last_heartbeat_at.isoformat() if job.last_heartbeat_at else None
        ),
        "workspace_present": ExecutionWorkspace.objects.filter(run=job.run).exists(),
        "provider_started": bool(job.run.provider_execution_id),
        "governed_transition": "WORKSPACE_PROVISIONING_RECOVERY",
    }


def queue_workspace_provisioning_recovery(
    job: ExecutionJob,
    *,
    reason: str,
    now: datetime | None = None,
    worker_id: str | None = None,
    exception_type: str = "",
) -> ExecutionRecoveryAttempt | None:
    """Release one provider-free provisioning lease into bounded recovery.

    A worker supplies its identity when it caught an unexpected exception.  A
    reconciler leaves it empty after independently proving the lease stale.
    The function is idempotent under races: a superseded lease simply yields no
    new recovery decision.
    """
    observed_at = now or timezone.now()
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
        run = locked.run
        if (
            run.lifecycle != ExecutionRun.Lifecycle.STARTING
            or run.current_phase not in PROVISIONING_PHASES
            or run.provider_execution_id
            or locked.status != ExecutionJob.Status.LEASED
        ):
            return None
        if worker_id is not None and (
            locked.lease_owner != worker_id
            or locked.lease_fencing_token != job.lease_fencing_token
        ):
            return None

        evidence = _recovery_evidence(
            locked,
            observed_at=observed_at,
            reason=reason,
            exception_type=exception_type,
        )
        locked.lease_owner = ""
        locked.lease_expires_at = None
        locked.last_heartbeat_at = None
        locked.recovery_attempts += 1
        locked.provider_attempt_metadata = {
            **locked.provider_attempt_metadata,
            "recovery_action": "RESTART_WORKSPACE_PROVISIONING",
            "workspace_provisioning_recovery_reason": reason,
        }

        if locked.recovery_attempts <= MAX_WORKSPACE_PROVISIONING_RECOVERY_ATTEMPTS:
            locked.status = ExecutionJob.Status.RECOVERING
            locked.next_recovery_at = observed_at + timedelta(
                seconds=WORKSPACE_PROVISIONING_RECOVERY_DELAY_SECONDS
            )
            run.current_phase = "WORKSPACE_RECOVERY_PENDING"
            run.current_blocker = {
                "category": "WORKSPACE_PROVISIONING_RECOVERY_PENDING",
                "reason": reason,
                "retry_at": locked.next_recovery_at.isoformat(),
                "evidence": evidence,
            }
            run.ended_at = None
            outcome = ExecutionRecoveryAttempt.Outcome.RECOVERING
            attempt_reason = "workspace provisioning queued for bounded recovery"
            event_type = "WORKSPACE_PROVISIONING_RECOVERY_QUEUED"
        else:
            locked.status = ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED
            locked.next_recovery_at = None
            run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
            run.current_phase = "WORKSPACE_PROVISIONING_RECOVERY_EXHAUSTED"
            run.current_blocker = {
                "category": "WORKSPACE_PROVISIONING_RECOVERY_EXHAUSTED",
                "reason": reason,
                "evidence": evidence,
            }
            run.terminal_state = "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"
            run.ended_at = observed_at
            outcome = ExecutionRecoveryAttempt.Outcome.REVIEW_REQUIRED
            attempt_reason = "workspace provisioning recovery retry budget exhausted"
            event_type = "WORKSPACE_PROVISIONING_RECOVERY_EXHAUSTED"

        attempt = ExecutionRecoveryAttempt.objects.create(
            job=locked,
            outcome=outcome,
            reason=attempt_reason,
            evidence=evidence,
        )
        locked.reconciliation_evidence = [
            *locked.reconciliation_evidence,
            {"attempt": attempt.pk, **evidence, "outcome": outcome},
        ][-20:]
        locked.save(
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
            event_type,
            recovery_attempt=locked.recovery_attempts,
            retry_at=(
                locked.next_recovery_at.isoformat() if locked.next_recovery_at else None
            ),
            **evidence,
        )
    return attempt


def reconcile_stale_workspace_provisioning_jobs(
    *, now: datetime | None = None
) -> list[ExecutionRecoveryAttempt]:
    """Recover expired leases before a workspace or provider exists."""
    observed_at = now or timezone.now()
    decisions: list[ExecutionRecoveryAttempt] = []
    candidates = ExecutionJob.objects.select_related("run").filter(
        status=ExecutionJob.Status.LEASED,
        run__lifecycle=ExecutionRun.Lifecycle.STARTING,
        run__current_phase__in=PROVISIONING_PHASES,
        run__provider_execution_id="",
    )
    for candidate in candidates:
        stale = (
            candidate.lease_expires_at is None
            or candidate.lease_expires_at <= observed_at
            or candidate.last_heartbeat_at is None
            or candidate.last_heartbeat_at
            <= observed_at - timedelta(seconds=WORKER_HEARTBEAT_STALE_SECONDS)
        )
        if not stale:
            continue
        decision = queue_workspace_provisioning_recovery(
            candidate,
            reason="STALE_WORKSPACE_PROVISIONING_LEASE",
            now=observed_at,
        )
        if decision is not None:
            decisions.append(decision)
    return decisions

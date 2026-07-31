"""Contract-bound local Codex worker handoff.

This module deliberately does not start a provider.  It makes a locally run
Codex process a durable worker of an already consumed execution instead of
trusting an arbitrary terminal session.  The normal recovery controller owns
interruption handling and is therefore shared with remote workers.
"""

from __future__ import annotations

import re
import subprocess
from datetime import timedelta
from pathlib import Path
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from .contracts import _scope_for_contract, validate_issued_execution_contract
from .execution import add_event, heartbeat_job
from .execution_recovery import record_checkpoint
from .models import ExecutionContract, ExecutionJob, ExecutionRun, McpAuditEvent


def _run_for_token(execution_token: str) -> ExecutionRun:
    try:
        token = UUID(str(execution_token))
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_EXECUTION_TOKEN") from exc
    try:
        return ExecutionRun.objects.select_related("contract", "queue_job").get(
            token=token
        )
    except ExecutionRun.DoesNotExist as exc:
        raise ValueError("EXECUTION_NOT_FOUND") from exc


def _verify_local_binding(run: ExecutionRun, platform_root: Path) -> None:
    contract = run.contract
    if contract.lifecycle not in {
        ExecutionContract.Lifecycle.CONSUMED,
        ExecutionContract.Lifecycle.RUNNING,
    }:
        raise ValueError("CONTRACT_NOT_CONSUMED")
    if run.contract_hash != contract.contract_hash:
        raise ValueError("LOCAL_CODEX_CONTRACT_HASH_MISMATCH")
    validate_issued_execution_contract(contract, platform_root)
    scope = _scope_for_contract(contract)
    declared = contract.payload["approved_scope"]
    if (
        declared.get("identifier") != scope.identifier
        or declared.get("content_hash") != scope.content_hash
        or declared.get("proposal_hash") != scope.record.get("proposal_hash")
    ):
        raise ValueError("LOCAL_CODEX_SCOPE_BINDING_MISMATCH")


def prepare_local_codex(
    *,
    execution_token: str,
    worker_id: str,
    platform_root: Path,
    lease_seconds: int = 120,
) -> ExecutionJob:
    """Register and lease the exact queue job for a local governed session."""
    if not worker_id or lease_seconds <= 0:
        raise ValueError("INVALID_WORKER_LEASE")
    run = _run_for_token(execution_token)
    if run.contract.payload.get("delivery"):
        raise ValueError("LOCAL_CODEX_DELIVERY_REQUIRES_CANONICAL_COMPLETION")
    _verify_local_binding(run, platform_root)
    now = timezone.now()
    with transaction.atomic():
        run = (
            ExecutionRun.objects.select_for_update()
            .select_related("queue_job")
            .get(pk=run.pk)
        )
        job = run.queue_job
        if job.status == ExecutionJob.Status.COMPLETED:
            raise ValueError("LOCAL_CODEX_EXECUTION_COMPLETED")
        if job.status == ExecutionJob.Status.LEASED and job.lease_owner != worker_id:
            if job.lease_expires_at and job.lease_expires_at > now:
                raise ValueError("WORKER_LEASE_OWNED_BY_ANOTHER_WORKER")
        elif job.status not in {
            ExecutionJob.Status.QUEUED,
            ExecutionJob.Status.LEASED,
            ExecutionJob.Status.RECOVERING,
        }:
            raise ValueError("LOCAL_CODEX_JOB_NOT_RECLAIMABLE")
        first_registration = not job.provider_attempt_metadata.get("local_codex")
        job.status = ExecutionJob.Status.LEASED
        job.lease_owner = worker_id
        job.lease_expires_at = now + timedelta(seconds=lease_seconds)
        job.last_heartbeat_at = now
        job.provider_attempt_metadata = {
            **job.provider_attempt_metadata,
            "local_codex": True,
            "worker_id": worker_id,
            "registered_at": now.isoformat(),
        }
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "last_heartbeat_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
        run.lifecycle = ExecutionRun.Lifecycle.RUNNING
        run.current_phase = "LOCAL_CODEX_ACTIVE"
        run.started_at = run.started_at or now
        run.save(
            update_fields=["lifecycle", "current_phase", "started_at", "updated_at"]
        )
        if run.contract.lifecycle == ExecutionContract.Lifecycle.CONSUMED:
            run.contract.lifecycle = ExecutionContract.Lifecycle.RUNNING
            run.contract.save(update_fields=["lifecycle"])
    if first_registration:
        add_event(run, "LOCAL_CODEX_WORKER_REGISTERED", worker=worker_id)
    add_event(run, "LOCAL_CODEX_LEASE_ACQUIRED", worker=worker_id)
    return job


def heartbeat_local_codex(
    *, execution_token: str, worker_id: str, lease_seconds: int = 120
) -> ExecutionJob:
    """Renew a local worker lease without calling a provider."""
    job = _run_for_token(execution_token).queue_job
    renewed = heartbeat_job(job, worker_id, lease_seconds)
    add_event(renewed.run, "LOCAL_CODEX_HEARTBEAT", worker=worker_id)
    return renewed


def checkpoint_local_codex(
    *, execution_token: str, worker_id: str, checkpoint: dict[str, object]
) -> ExecutionJob:
    """Persist a recovery-safe local checkpoint only for the lease owner."""
    job = _run_for_token(execution_token).queue_job
    if job.lease_owner != worker_id or job.status != ExecutionJob.Status.LEASED:
        raise ValueError("WORKER_LEASE_NOT_OWNED")
    recorded = record_checkpoint(job=job, checkpoint=checkpoint)
    add_event(recorded.run, "LOCAL_CODEX_CHECKPOINT_RECORDED", worker=worker_id)
    return recorded


def mark_local_codex_interrupted(
    *, execution_token: str, worker_id: str
) -> ExecutionJob:
    """Record a local-process interruption; recovery decides the next action."""
    job = _run_for_token(execution_token).queue_job
    if job.lease_owner != worker_id or job.status != ExecutionJob.Status.LEASED:
        raise ValueError("WORKER_LEASE_NOT_OWNED")
    job.lease_expires_at = timezone.now() - timedelta(seconds=1)
    job.save(update_fields=["lease_expires_at", "updated_at"])
    add_event(job.run, "LOCAL_CODEX_INTERRUPTED", worker=worker_id)
    return job


def complete_local_codex(
    *,
    execution_token: str,
    worker_id: str,
    final_commit_sha: str,
    evidence_manifest: dict[str, object],
) -> ExecutionRun:
    """Close the same governed run after local evidence and commit verification."""
    if not re.fullmatch(r"[0-9a-f]{40}", final_commit_sha) or not evidence_manifest:
        raise ValueError("LOCAL_CODEX_COMPLETION_EVIDENCE_REQUIRED")
    run = _run_for_token(execution_token)
    job = run.queue_job
    if job.status != ExecutionJob.Status.LEASED or job.lease_owner != worker_id:
        raise ValueError("WORKER_LEASE_NOT_OWNED")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=run.workspace_identifier,
        check=False,
        capture_output=True,
        text=True,
    )
    if head.returncode or head.stdout.strip() != final_commit_sha:
        raise ValueError("RUN_FINAL_COMMIT_MISMATCH")
    with transaction.atomic():
        run = (
            ExecutionRun.objects.select_for_update()
            .select_related("queue_job", "contract")
            .get(pk=run.pk)
        )
        job = run.queue_job
        if job.lease_owner != worker_id or job.status != ExecutionJob.Status.LEASED:
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        run.lifecycle = ExecutionRun.Lifecycle.COMPLETED
        run.current_phase = "COMPLETED"
        run.final_commit_sha = final_commit_sha
        run.terminal_state = "PASS"
        run.completion_data = {
            "execution_result": "LOCAL_CODEX",
            "evidence_manifest": evidence_manifest,
        }
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
        job.status = ExecutionJob.Status.COMPLETED
        job.lease_owner = ""
        job.lease_expires_at = None
        job.save(
            update_fields=["status", "lease_owner", "lease_expires_at", "updated_at"]
        )
        run.contract.lifecycle = ExecutionContract.Lifecycle.COMPLETED
        run.contract.final_commit_sha = final_commit_sha
        run.contract.completion_data = run.completion_data
        run.contract.completed_at = run.ended_at
        run.contract.save(
            update_fields=[
                "lifecycle",
                "final_commit_sha",
                "completion_data",
                "completed_at",
            ]
        )
    add_event(run, "LOCAL_CODEX_EXECUTION_COMPLETED", final_commit_sha=final_commit_sha)
    return run


def record_unverified_local_session(
    *, execution_token: str, session_reference: str
) -> None:
    """Make an arbitrary existing terminal session explicitly untrusted."""
    run = _run_for_token(execution_token)
    if not session_reference:
        raise ValueError("LOCAL_SESSION_REFERENCE_REQUIRED")
    McpAuditEvent.objects.create(
        caller="local-codex-wrapper",
        tool_name="local_codex.attach_existing_session",
        project=run.contract.project,
        outcome="UNVERIFIED",
        details={
            "execution_token": str(run.token),
            "session_reference": session_reference,
        },
    )
    raise ValueError("UNVERIFIED_LOCAL_EXECUTION")

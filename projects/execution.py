"""Canonical execution dispatch, provider boundary and bounded repair control."""

from __future__ import annotations

import json
import subprocess
from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import Protocol

from django.conf import settings
from django.db import IntegrityError, OperationalError, models, transaction
from django.utils import timezone

from .execution_activity import console_line
from .models import (
    ContractConsumption,
    ExecutionContract,
    ExecutionJob,
    ExecutionProgressEvent,
    ExecutionRun,
    ExecutionStartRequest,
    ExecutionWorkspace,
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
    ExecutionRun.Lifecycle.VALIDATING,
    ExecutionRun.Lifecycle.REPAIRING,
    ExecutionRun.Lifecycle.DOCUMENTING,
    ExecutionRun.Lifecycle.CLOSING,
}
MAX_PROVIDER_START_ATTEMPTS = 2

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
            },
        )
        if run.contract_id != contract.pk:
            raise ValueError("EXECUTION_REQUEST_CONTRACT_MISMATCH")
        job, job_created = ExecutionJob.objects.get_or_create(run=run)
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
        job.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "last_heartbeat_at",
                "updated_at",
            ]
        )
    add_event(
        job.run,
        "WORKER_LEASE_RECLAIMED" if reclaimed else "WORKER_LEASE_ACQUIRED",
        worker=worker_id,
    )
    return job


def heartbeat_job(
    job: ExecutionJob, worker_id: str, lease_seconds: int
) -> ExecutionJob:
    """Renew only the lease held by this worker and record durable liveness."""
    now = timezone.now()
    with transaction.atomic():
        job = ExecutionJob.objects.select_for_update().get(pk=job.pk)
        if job.status != ExecutionJob.Status.LEASED or job.lease_owner != worker_id:
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
    now = timezone.now()
    with transaction.atomic():
        locked_job = (
            ExecutionJob.objects.select_for_update()
            .select_related("run", "run__contract")
            .get(pk=job.pk)
        )
        if (
            locked_job.status != ExecutionJob.Status.LEASED
            or locked_job.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        run = locked_job.run
        evidence = {
            "recorded_at": now.isoformat(),
            "classification": "NON_RETRYABLE_CONTRACT_OR_GOVERNANCE_FAILURE",
            "reason": reason,
            "retryable": False,
            "worker": worker_id,
            "contract_id": run.contract_id,
            "contract_hash": run.contract_hash,
            "provider_started": False,
        }
        locked_job.status = ExecutionJob.Status.REJECTED
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
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
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
                return existing
            raise
        except OperationalError:
            if attempt == 2:
                raise
            sleep(0.05 * (attempt + 1))
    if settings.AI_BRIDGE_DEV_EXECUTION_ACTIVITY:
        print(console_line(event), flush=True)
    return event


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
            run, "START_RECOVERED", reason="resuming persisted queued or blocked run"
        )

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
                    event_type = str(details.pop("event_type", "PROVIDER_MESSAGE"))
                    add_event(run, event_type, **details)

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
    if job.status != ExecutionJob.Status.LEASED or job.lease_owner != worker_id:
        raise ValueError("WORKER_LEASE_NOT_OWNED")
    if job.provider_attempt_metadata.get("recovery_action") == "REATTACH":
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
    run = start_run(job.run.contract, job.run.start_request, platform_root)
    job.status = ExecutionJob.Status.STARTED
    job.provider_attempt_metadata = {
        "attempt_count": run.attempt_count,
        "provider_execution_id": run.provider_execution_id,
        "started_at": run.started_at.isoformat() if run.started_at else None,
    }
    job.save(update_fields=["status", "provider_attempt_metadata", "updated_at"])
    add_event(run, "WORKER_DISPATCH_COMPLETED", worker=worker_id)
    return run


def cancel_run(
    run: ExecutionRun, *, approval_reference: str, phase: str = "CANCELLED"
) -> ExecutionRun:
    """Cancel a provider run through the one canonical executor boundary."""
    if run.lifecycle == ExecutionRun.Lifecycle.CANCELLED:
        return run
    if run.lifecycle not in {
        ExecutionRun.Lifecycle.RUNNING,
        ExecutionRun.Lifecycle.STARTING,
    }:
        raise ValueError("EXECUTION_NOT_CANCELLABLE")
    try:
        adapter = provider(run.provider_name)
        if adapter.status(run.provider_execution_id) != "FINISHED":
            adapter.cancel(run.provider_execution_id)
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

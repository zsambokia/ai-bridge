"""Canonical execution dispatch, provider boundary and bounded repair control."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Protocol

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import (
    ContractConsumption,
    ExecutionContract,
    ExecutionProgressEvent,
    ExecutionRun,
    ExecutionStartRequest,
)
from .models import (
    ExecutionProvider as ExecutionProviderRecord,
)
from .providers import (
    CodexCliAdapter,
    ProviderStart,
    adapter_for,
    check_health,
    mark_runtime_unavailable,
    select_provider,
)

ACTIVE_STATES = {
    ExecutionRun.Lifecycle.REQUESTED,
    ExecutionRun.Lifecycle.STARTING,
    ExecutionRun.Lifecycle.RUNNING,
    ExecutionRun.Lifecycle.VALIDATING,
    ExecutionRun.Lifecycle.REPAIRING,
    ExecutionRun.Lifecycle.DOCUMENTING,
    ExecutionRun.Lifecycle.CLOSING,
}
SECRET_MARKERS = ("token", "secret", "password", "authorization", "bearer")
MAX_PROVIDER_START_ATTEMPTS = 2


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
    safe: dict[str, object] = {}
    for key, value in details.items():
        if any(marker in key.lower() for marker in SECRET_MARKERS):
            continue
        rendered = str(value)
        safe[key] = rendered[:500] if isinstance(value, str) else value
    return safe


def add_event(
    run: ExecutionRun, event_type: str, **details: object
) -> ExecutionProgressEvent:
    with transaction.atomic():
        last = (
            ExecutionProgressEvent.objects.select_for_update()
            .filter(run=run)
            .order_by("-sequence")
            .first()
        )
        return ExecutionProgressEvent.objects.create(
            run=run,
            sequence=1 if last is None else last.sequence + 1,
            event_type=event_type,
            details=_safe_details(details),
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
    root: Path,
    audit_event_id: int | None = None,
) -> ExecutionRun:
    """Persist authorization and ownership before an external start is active."""
    if contract.lifecycle != ExecutionContract.Lifecycle.CONSUMED:
        raise ValueError("CONTRACT_NOT_CONSUMED")
    receipt = ContractConsumption.objects.filter(contract=contract).first()
    if receipt is None:
        raise ValueError("CONSUMPTION_RECEIPT_REQUIRED")
    from .contracts import validate_issued_execution_contract

    validate_issued_execution_contract(contract, root)
    execution = contract.payload["execution"]
    recoverable_run = (
        ExecutionRun.objects.filter(
            contract=contract,
            lifecycle=ExecutionRun.Lifecycle.STARTING,
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
            workspace_identifier=str(root),
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
        add_event(run, "START_RECOVERED", reason="resuming persisted blocked run")

    started: ProviderStart | None = None
    failure: Exception | None = None
    for attempt in range(1, MAX_PROVIDER_START_ATTEMPTS + 1):
        run.attempt_count += 1
        run.save(update_fields=["attempt_count", "updated_at"])
        try:
            readiness = check_health(provider_record)
            if readiness["status"] != "HEALTHY":
                raise ValueError("CODEX_RUNTIME_NOT_READY")
            started = selected_provider.start(repository=root, prompt=_prompt(contract))
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
    add_event(
        run,
        "EXECUTOR_STARTED",
        provider=run.provider_name,
        execution_id=started.execution_id,
    )
    contract.lifecycle = ExecutionContract.Lifecycle.RUNNING
    contract.save(update_fields=["lifecycle"])
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
    run.terminal_state = "PASS — READY FOR PRODUCT OWNER REVIEW"
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

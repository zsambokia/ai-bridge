"""Canonical execution dispatch, provider boundary and bounded repair control."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
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


@dataclass(frozen=True)
class ProviderStart:
    execution_id: str
    workspace_identifier: str


class ExecutionProvider(Protocol):
    name: str

    def start(self, *, repository: Path, prompt: str) -> ProviderStart: ...
    def status(self, execution_id: str) -> str: ...
    def cancel(self, execution_id: str) -> None: ...


class CodexCliProvider:
    """Codex CLI adapter; command arguments are fixed and no secret is persisted."""

    name = "codex-cli"

    def start(self, *, repository: Path, prompt: str) -> ProviderStart:
        executable = os.environ.get("BRIDGE_CODEX_EXECUTABLE", "codex")
        process = subprocess.Popen(  # noqa: S603
            [
                executable,
                "exec",
                "--json",
                "--sandbox",
                "workspace-write",
                "-C",
                str(repository),
                prompt,
            ],
            cwd=repository,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
        return ProviderStart(str(process.pid), str(repository))

    def status(self, execution_id: str) -> str:
        try:
            os.kill(int(execution_id), 0)
        except OSError:
            return "FINISHED"
        return "RUNNING"

    def cancel(self, execution_id: str) -> None:
        os.kill(int(execution_id), 15)


def provider() -> ExecutionProvider:
    configured = getattr(settings, "BRIDGE_EXECUTOR_PROVIDER", "codex-cli")
    if configured != "codex-cli":
        raise ValueError("EXECUTOR_PROVIDER_UNAVAILABLE")
    return CodexCliProvider()


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
    execution = contract.payload["execution"]
    return (
        "Execute only the consumed Bridge contract below. Preserve unrelated work, "
        "run the specified validation, and never expose credentials.\n"
        f"Contract: {contract.handoff_identifier}\nIntent: {execution['intent']}\n"
        f"Evidence root: {contract.payload['evidence']['root']}"
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
    if not ContractConsumption.objects.filter(contract=contract).exists():
        raise ValueError("CONSUMPTION_RECEIPT_REQUIRED")
    from .contracts import validate_issued_execution_contract

    validate_issued_execution_contract(contract, root)
    execution = contract.payload["execution"]
    if ExecutionRun.objects.filter(
        contract__project=contract.project,
        branch=execution["target_branch"],
        lifecycle__in=ACTIVE_STATES,
    ).exists():
        raise ValueError("CONFLICTING_ACTIVE_EXECUTION")
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=contract.payload["project"]["repository"],
        branch=execution["target_branch"],
        baseline_commit=execution["baseline_commit"],
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name=provider().name,
        audit_event_id=audit_event_id,
        lifecycle=ExecutionRun.Lifecycle.STARTING,
        current_phase="STARTING",
        evidence_root=contract.payload["evidence"]["root"],
        started_at=timezone.now(),
    )
    add_event(
        run, "PREFLIGHT_COMPLETED", branch=run.branch, baseline=run.baseline_commit
    )
    try:
        started = provider().start(repository=root, prompt=_prompt(contract))
    except (OSError, subprocess.SubprocessError) as exc:
        run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
        run.current_blocker = {
            "category": "unavailable external input",
            "question": "Restore Codex provider access.",
            "evidence": str(exc)[:300],
        }
        run.ended_at = timezone.now()
        run.save(
            update_fields=["lifecycle", "current_blocker", "ended_at", "updated_at"]
        )
        add_event(run, "PROVIDER_FAILURE", classification="unavailable external input")
        raise ValueError("EXECUTOR_START_FAILED") from exc
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

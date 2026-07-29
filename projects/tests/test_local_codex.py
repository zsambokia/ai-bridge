"""Durable, contract-bound handoff tests for a local Codex worker."""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

from projects.contracts import _normalized_hash
from projects.execution import enqueue_run
from projects.execution_recovery import reconcile_execution_jobs
from projects.local_codex import (
    checkpoint_local_codex,
    complete_local_codex,
    heartbeat_local_codex,
    mark_local_codex_interrupted,
    prepare_local_codex,
    record_unverified_local_session,
)
from projects.models import ExecutionContract, ExecutionJob, ExecutionRun, McpAuditEvent
from projects.tests import test_execution


@pytest.fixture
def local_codex_job(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Path, ExecutionContract, ExecutionRun, ExecutionJob]]:
    root, contract, request = next(
        test_execution.consumed_contract.__wrapped__(tmp_path, monkeypatch)  # type: ignore[attr-defined]
    )
    job = enqueue_run(contract, request, root)
    yield root, contract, job.run, job


def _checkpoint() -> dict[str, object]:
    return {
        "baseline_commit": "a" * 40,
        "working_tree_diff_hash": "b" * 64,
        "completed_steps": ["implementation"],
        "remaining_steps": ["release-gates"],
        "last_successful_gate": "pytest",
        "modified_files": ["projects/local_codex.py"],
        "latest_provider_summary": "local process interrupted",
        "next_recommended_action": "resume",
    }


@pytest.mark.django_db
def test_local_worker_is_contract_bound_and_visible_after_reload(
    local_codex_job: tuple[Path, ExecutionContract, ExecutionRun, ExecutionJob],
) -> None:
    root, contract, run, job = local_codex_job

    prepared = prepare_local_codex(
        execution_token=str(run.token), worker_id="codex-local-1", platform_root=root
    )
    # A fresh database read models a Django process reload: no in-memory
    # session is trusted, while the exact job and lease remain visible.
    reloaded = ExecutionJob.objects.get(pk=prepared.pk)
    renewed = heartbeat_local_codex(
        execution_token=str(run.token), worker_id="codex-local-1"
    )

    assert reloaded.pk == job.pk
    assert reloaded.status == ExecutionJob.Status.LEASED
    assert reloaded.last_heartbeat_at is not None
    assert renewed.last_heartbeat_at is not None
    assert renewed.last_heartbeat_at >= reloaded.last_heartbeat_at
    contract.refresh_from_db()
    assert contract.lifecycle == ExecutionContract.Lifecycle.RUNNING
    assert run.events.filter(event_type="LOCAL_CODEX_WORKER_REGISTERED").exists()
    assert run.events.filter(event_type="LOCAL_CODEX_HEARTBEAT").exists()


@pytest.mark.django_db
def test_interrupted_local_worker_recovers_the_same_execution(
    local_codex_job: tuple[Path, ExecutionContract, ExecutionRun, ExecutionJob],
) -> None:
    root, _contract, run, job = local_codex_job
    prepare_local_codex(
        execution_token=str(run.token), worker_id="codex-local-2", platform_root=root
    )
    checkpoint_local_codex(
        execution_token=str(run.token),
        worker_id="codex-local-2",
        checkpoint=_checkpoint(),
    )
    mark_local_codex_interrupted(
        execution_token=str(run.token), worker_id="codex-local-2"
    )

    decisions = reconcile_execution_jobs(provider_status=lambda _name, _id: "MISSING")
    job.refresh_from_db()
    run.refresh_from_db()

    assert len(decisions) == 1
    assert decisions[0].job_id == job.pk
    assert job.status == ExecutionJob.Status.RECOVERING
    assert run.lifecycle == ExecutionRun.Lifecycle.STARTING
    assert ExecutionRun.objects.filter(contract=run.contract).count() == 1
    assert run.events.filter(event_type="LOCAL_CODEX_INTERRUPTED").exists()


@pytest.mark.django_db
def test_local_worker_rejects_scope_drift_and_unverified_session(
    local_codex_job: tuple[Path, ExecutionContract, ExecutionRun, ExecutionJob],
) -> None:
    root, contract, run, _job = local_codex_job
    contract.payload["approved_scope"]["proposal_hash"] = "c" * 64
    contract.contract_hash = _normalized_hash(contract.payload)
    contract.save(update_fields=["payload", "contract_hash"])
    run.contract_hash = contract.contract_hash
    run.save(update_fields=["contract_hash"])

    with pytest.raises(ValueError, match="SCOPE_BINDING_MISMATCH"):
        prepare_local_codex(
            execution_token=str(run.token),
            worker_id="codex-local-3",
            platform_root=root,
        )
    with pytest.raises(ValueError, match="UNVERIFIED_LOCAL_EXECUTION"):
        record_unverified_local_session(
            execution_token=str(run.token), session_reference="unbound-terminal-42"
        )
    assert McpAuditEvent.objects.filter(
        project=run.contract.project, outcome="UNVERIFIED"
    ).exists()


@pytest.mark.django_db
def test_completion_stays_bound_to_the_original_contract(
    local_codex_job: tuple[Path, ExecutionContract, ExecutionRun, ExecutionJob],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, run, job = local_codex_job
    prepare_local_codex(
        execution_token=str(run.token), worker_id="codex-local-4", platform_root=root
    )
    monkeypatch.setattr(
        "projects.local_codex.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, "d" * 40, ""),
    )

    completed = complete_local_codex(
        execution_token=str(run.token),
        worker_id="codex-local-4",
        final_commit_sha="d" * 40,
        evidence_manifest={"audit": "docs/evidence/audit.md", "gates": "PASS"},
    )
    job.refresh_from_db()
    contract.refresh_from_db()

    assert completed.pk == run.pk
    assert completed.contract_id == contract.pk
    assert completed.final_commit_sha == "d" * 40
    assert job.status == ExecutionJob.Status.COMPLETED
    assert contract.lifecycle == ExecutionContract.Lifecycle.COMPLETED
    with pytest.raises(ValueError, match="CONTRACT_NOT_CONSUMED"):
        prepare_local_codex(
            execution_token=str(run.token),
            worker_id="codex-local-4",
            platform_root=root,
        )

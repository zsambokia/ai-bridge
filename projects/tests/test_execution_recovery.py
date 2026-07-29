from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone

from projects.execution import claim_next_job, execute_claimed_job, start_run
from projects.execution_recovery import reconcile_execution_jobs, record_checkpoint
from projects.models import (
    ExecutionContract,
    ExecutionJob,
    ExecutionRecoveryAttempt,
    ExecutionRun,
    ExecutionStartRequest,
)
from projects.tests import test_execution


@pytest.fixture
def recovery_consumed_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[Path, ExecutionContract, ExecutionStartRequest]]:
    yield from test_execution.consumed_contract.__wrapped__(  # type: ignore[attr-defined]
        tmp_path,
        monkeypatch,
    )


@pytest.mark.django_db
def test_stale_dead_provider_recovers_same_run_from_checkpoint(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = recovery_consumed_contract
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        provider_execution_id="dead-provider",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() - timedelta(seconds=1),
        checkpoint={
            "baseline_commit": "a" * 40,
            "working_tree_diff_hash": "b" * 64,
            "completed_steps": ["implementation"],
            "remaining_steps": ["tests"],
            "last_successful_gate": "pytest",
            "modified_files": ["projects/execution.py"],
            "latest_provider_summary": "interrupted",
            "next_recommended_action": "resume",
        },
    )
    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: "MISSING", now=timezone.now()
    )
    job.refresh_from_db()
    run.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.RECOVERING
    assert job.status == ExecutionJob.Status.RECOVERING
    assert run.lifecycle == ExecutionRun.Lifecycle.STARTING
    assert run.provider_execution_id == ""
    job.next_recovery_at = timezone.now() - timedelta(seconds=1)
    job.save()
    claimed = claim_next_job("replacement-worker", 60)
    assert claimed and claimed.pk == job.pk
    assert claimed.run_id == run.pk
    assert (
        reconcile_execution_jobs(
            provider_status=lambda _name, _id: "MISSING", now=timezone.now()
        )
        == []
    )


@pytest.mark.django_db
def test_stale_alive_provider_is_queued_for_worker_reattach(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = recovery_consumed_contract
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        provider_execution_id="still-alive",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() - timedelta(seconds=1),
    )
    decisions = reconcile_execution_jobs(provider_status=lambda _name, _id: "RUNNING")
    job.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.REATTACH
    assert job.status == ExecutionJob.Status.QUEUED
    claimed = claim_next_job("replacement-worker", 60)
    assert claimed is not None
    reattached = execute_claimed_job(claimed, "replacement-worker", root)
    job.refresh_from_db()
    assert reattached.pk == run.pk
    assert reattached.provider_execution_id == "still-alive"
    assert job.provider_attempt_metadata["recovery_action"] == "REATTACHED"
    assert run.events.filter(
        event_type="WORKER_REATTACHED_TO_PROVIDER_EXECUTION"
    ).exists()


@pytest.mark.django_db
def test_missing_checkpoint_restarts_same_authoritative_run(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = recovery_consumed_contract
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        provider_execution_id="gone",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() - timedelta(seconds=1),
    )
    decisions = reconcile_execution_jobs(provider_status=lambda _name, _id: "MISSING")
    job.refresh_from_db()
    run.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.RECOVERING
    assert job.status == ExecutionJob.Status.RECOVERING
    assert job.provider_attempt_metadata["recovery_action"] == "RESTART_FROM_AUTHORITY"
    assert run.lifecycle == ExecutionRun.Lifecycle.STARTING
    assert run.current_phase == "RECOVERING"
    assert run.current_blocker == {}
    assert run.ended_at is None
    assert run.events.filter(event_type="RECOVERY_RETRY_QUEUED").exists()
    return
    assert run.terminal_state == "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"
    assert run.ended_at is not None

    # The historic review decision remains inspectable, but no longer occupies
    # the per-branch active-execution guard for the next governed request.
    next_request = ExecutionStartRequest.objects.create(
        contract=contract, approval=request.approval
    )
    monkeypatch.setattr(
        "projects.execution.provider",
        lambda identity=None: test_execution.StubProvider(),
    )
    next_run = start_run(contract, next_request, root)
    assert next_run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert next_run.pk != run.pk


@pytest.mark.django_db
def test_legacy_review_required_run_is_terminalized_governedly(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = recovery_consumed_contract
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        provider_execution_id="gone",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        current_phase="RECOVERY_REVIEW_REQUIRED",
        current_blocker={"category": "RECOVERY_REVIEW_REQUIRED"},
        evidence_root="docs/evidence/test",
    )
    ExecutionJob.objects.create(
        run=run, status=ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED
    )

    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: "MISSING", now=timezone.now()
    )

    run.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.NO_ACTION
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    assert run.current_phase == "RECOVERY_REVIEW_REQUIRED"
    assert run.events.filter(
        event_type="RECOVERY_REVIEW_LIFECYCLE_TERMINALIZED"
    ).exists()
    assert (
        reconcile_execution_jobs(
            provider_status=lambda _name, _id: "MISSING", now=timezone.now()
        )
        == []
    )


@pytest.mark.django_db
def test_incomplete_checkpoint_is_rejected(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    _root, contract, request = recovery_consumed_contract
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="test",
        provider_name="codex-cli",
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(run=run)

    with pytest.raises(ValueError, match="missing required fields"):
        record_checkpoint(job=job, checkpoint={"baseline_commit": "a" * 40})

    job.refresh_from_db()
    assert job.checkpoint == {}


@pytest.mark.django_db
def test_provider_status_interruption_uses_checkpoint_recovery(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    _root, contract, request = recovery_consumed_contract
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="test",
        provider_name="codex-cli",
        provider_execution_id="interrupted",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() - timedelta(seconds=1),
        checkpoint={
            key: "value"
            for key in [
                "baseline_commit",
                "working_tree_diff_hash",
                "completed_steps",
                "remaining_steps",
                "last_successful_gate",
                "modified_files",
                "latest_provider_summary",
                "next_recommended_action",
            ]
        },
    )

    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: (_ for _ in ()).throw(OSError("offline"))
    )

    job.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.RECOVERING
    assert job.status == ExecutionJob.Status.RECOVERING

from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

import pytest
from django.core.management import call_command
from django.utils import timezone

from projects.execution import (
    claim_next_job,
    execute_claimed_job,
    reject_claimed_job,
    start_run,
)
from projects.execution_recovery import (
    classify_execution_recovery,
    reconcile_execution_jobs,
    record_checkpoint,
)
from projects.management.commands import reconcile_execution_jobs as reconcile_command
from projects.models import (
    ExecutionContract,
    ExecutionJob,
    ExecutionRecoveryAttempt,
    ExecutionRun,
    ExecutionStartRequest,
    ExecutionWorkspace,
)
from projects.tests import test_execution
from projects.workspace import WorkspaceManager


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
def test_finished_provider_is_terminalized_without_inventing_completion(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = recovery_consumed_contract
    contract.lifecycle = ExecutionContract.Lifecycle.RUNNING
    contract.save(update_fields=["lifecycle"])
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        provider_execution_id="finished-provider",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() + timedelta(minutes=5),
        last_heartbeat_at=timezone.now(),
    )

    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: "FINISHED", now=timezone.now()
    )

    run.refresh_from_db()
    job.refresh_from_db()
    contract.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.REVIEW_REQUIRED
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    assert run.current_phase == "PROVIDER_TERMINALIZED"
    assert run.terminal_state == "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"
    assert job.status == ExecutionJob.Status.FAILED
    assert contract.lifecycle == ExecutionContract.Lifecycle.CANCELLED
    assert contract.closure_state == run.terminal_state
    assert run.events.filter(event_type="PROVIDER_TERMINAL_RECONCILED").exists()


@pytest.mark.django_db
def test_recovery_classifier_reports_durable_facts_and_safe_actions(
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
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(run=run, status=ExecutionJob.Status.QUEUED)

    decision = classify_execution_recovery(job)

    assert decision["classification"] == "WORKSPACE_RECOVERABLE"
    facts = decision["facts"]
    assert isinstance(facts, dict)
    assert facts["run_lifecycle"] == ExecutionRun.Lifecycle.RUNNING
    assert decision["permitted_next_actions"] == [
        "provision_or_reuse_workspace",
        "resume_authorized_run",
    ]
    assert decision["product_owner_involvement"] == "FORBIDDEN_FOR_TECHNICAL_RECOVERY"


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
    latest_evidence = job.reconciliation_evidence[-1]
    assert isinstance(latest_evidence, dict)
    assert latest_evidence["recovery_classification"] == "STALE_LEASE"
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


@pytest.mark.django_db
def test_terminal_run_job_divergence_is_converged_before_dispatch(
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
        lifecycle=ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(run=run, status=ExecutionJob.Status.QUEUED)

    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: "MISSING", now=timezone.now()
    )

    job.refresh_from_db()
    assert len(decisions) == 1
    assert job.status == ExecutionJob.Status.FAILED
    assert claim_next_job("worker", 60) is None
    assert run.events.filter(event_type="RUN_JOB_DIVERGENCE_CONVERGED").exists()
    assert (
        reconcile_execution_jobs(
            provider_status=lambda _name, _id: "MISSING", now=timezone.now()
        )
        == []
    )


@pytest.mark.django_db
def test_governed_recovery_e2e_runs_through_management_command(
    recovery_consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise the deployed reconciliation entry point against durable state."""
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
        provider_execution_id="lost-provider",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() - timedelta(seconds=1),
        checkpoint={
            "completed_steps": ["implementation"],
            "remaining_steps": ["gates"],
        },
    )

    class MissingProvider:
        @staticmethod
        def status(_execution_id: str) -> str:
            return "MISSING"

    monkeypatch.setattr(reconcile_command, "provider", lambda _name: MissingProvider())
    call_command("reconcile_execution_jobs", "--once")

    job.refresh_from_db()
    run.refresh_from_db()
    assert job.status == ExecutionJob.Status.RECOVERING
    assert run.lifecycle == ExecutionRun.Lifecycle.STARTING
    assert job.recovery_history.filter(
        outcome=ExecutionRecoveryAttempt.Outcome.RECOVERING
    ).exists()
    job.next_recovery_at = timezone.now() - timedelta(seconds=1)
    job.save(update_fields=["next_recovery_at"])
    claimed = claim_next_job("replacement-worker", 60)
    assert claimed is not None
    assert claimed.pk == job.pk


@pytest.mark.django_db
def test_active_run_with_terminal_job_fails_closed_idempotently(
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
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    ExecutionJob.objects.create(run=run, status=ExecutionJob.Status.FAILED)

    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: "MISSING", now=timezone.now()
    )

    run.refresh_from_db()
    assert len(decisions) == 1
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    assert run.current_phase == "RUN_JOB_DIVERGENCE"
    assert run.events.filter(event_type="RUN_JOB_DIVERGENCE_FAIL_CLOSED").exists()
    assert (
        reconcile_execution_jobs(
            provider_status=lambda _name, _id: "MISSING", now=timezone.now()
        )
        == []
    )


@pytest.mark.django_db
def test_worker_refuses_a_preclaimed_job_after_run_terminalization(
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
        lifecycle=ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.LEASED,
        lease_owner="worker",
        lease_expires_at=timezone.now() + timedelta(minutes=1),
    )

    with pytest.raises(ValueError, match="EXECUTION_RUN_NOT_ACTIVE"):
        execute_claimed_job(job, "worker", root)

    rejected = reject_claimed_job(
        job, "worker", ValueError("EXECUTION_RUN_NOT_ACTIVE")
    )
    run.refresh_from_db()
    assert rejected.status == ExecutionJob.Status.REJECTED
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    assert run.events.filter(
        event_type="WORKER_RUN_LIFECYCLE_RACE_CONVERGED"
    ).exists()


@pytest.mark.django_db
def test_missing_workspace_provider_pid_enters_bounded_recovery(
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
        provider_execution_id="101",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.STARTED,
        lease_expires_at=timezone.now() + timedelta(minutes=5),
        last_heartbeat_at=timezone.now(),
    )
    workspace = ExecutionWorkspace.objects.create(
        run=run,
        status=ExecutionWorkspace.Status.IN_USE,
        provider_pid=101,
    )

    decisions = reconcile_execution_jobs(
        provider_status=lambda _name, _id: pytest.fail("PID loss must not reattach"),
        process_is_alive=lambda _pid: False,
        now=timezone.now(),
    )

    job.refresh_from_db()
    workspace.refresh_from_db()
    assert decisions[0].outcome == ExecutionRecoveryAttempt.Outcome.RECOVERING
    assert job.status == ExecutionJob.Status.RECOVERING
    assert workspace.status == ExecutionWorkspace.Status.READY
    assert workspace.provider_pid is None
    assert run.events.filter(event_type="WORKSPACE_PROVIDER_PID_MISSING").exists()


def test_provider_pid_liveness_rejects_nonexistent_process() -> None:
    """A dead local provider PID must not be mistaken for a live process."""
    from projects.execution_recovery import provider_pid_is_alive

    assert provider_pid_is_alive(2_147_483_647) is False


@pytest.mark.django_db
def test_orphan_workspace_is_retained_once_after_terminal_run(
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
        lifecycle=ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
        evidence_root="docs/evidence/test",
    )
    workspace = ExecutionWorkspace.objects.create(
        run=run,
        status=ExecutionWorkspace.Status.IN_USE,
        provider_pid=101,
    )

    reconciled = WorkspaceManager().reconcile_ownership(now=timezone.now())

    workspace.refresh_from_db()
    assert [item.pk for item in reconciled] == [workspace.pk]
    assert workspace.status == ExecutionWorkspace.Status.RETAINED
    assert workspace.provider_pid is None
    assert run.events.filter(event_type="ORPHAN_WORKSPACE_RETAINED").exists()
    assert WorkspaceManager().reconcile_ownership(now=timezone.now()) == []

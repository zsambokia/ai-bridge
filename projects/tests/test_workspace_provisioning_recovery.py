from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import timedelta
from pathlib import Path
from typing import cast

import pytest
from django.core.management import call_command
from django.utils import timezone

from projects.models import (
    ExecutionContract,
    ExecutionJob,
    ExecutionRecoveryAttempt,
    ExecutionRun,
    ExecutionStartRequest,
)
from projects.tests import test_execution
from projects.workspace_provisioning_recovery import (
    MAX_WORKSPACE_PROVISIONING_RECOVERY_ATTEMPTS,
    queue_workspace_provisioning_recovery,
    reconcile_stale_workspace_provisioning_jobs,
)


@pytest.fixture
def provisioning_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[ExecutionRun, ExecutionJob]]:
    consumed_factory = cast(
        Callable[
            [Path, pytest.MonkeyPatch],
            Iterator[tuple[Path, ExecutionContract, ExecutionStartRequest]],
        ],
        getattr(test_execution.consumed_contract, "__wrapped__"),
    )
    consumed = consumed_factory(tmp_path, monkeypatch)
    _root, contract, request = next(consumed)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="",
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.STARTING,
        current_phase="STARTING",
        evidence_root="docs/evidence/test",
        started_at=timezone.now(),
    )
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.LEASED,
        lease_owner="interrupted-worker",
        lease_expires_at=timezone.now() - timedelta(seconds=1),
        last_heartbeat_at=timezone.now() - timedelta(seconds=121),
    )
    try:
        yield run, job
    finally:
        try:
            next(consumed)
        except StopIteration:
            pass


@pytest.mark.django_db
def test_stale_starting_lease_is_durably_queued_for_workspace_recovery(
    provisioning_run: tuple[ExecutionRun, ExecutionJob],
) -> None:
    run, job = provisioning_run

    decisions = reconcile_stale_workspace_provisioning_jobs(now=timezone.now())

    job.refresh_from_db()
    run.refresh_from_db()
    assert [decision.outcome for decision in decisions] == [
        ExecutionRecoveryAttempt.Outcome.RECOVERING
    ]
    assert job.status == ExecutionJob.Status.RECOVERING
    assert job.lease_owner == ""
    assert job.recovery_attempts == 1
    assert job.next_recovery_at is not None
    assert run.lifecycle == ExecutionRun.Lifecycle.STARTING
    assert run.current_phase == "WORKSPACE_RECOVERY_PENDING"
    assert run.provider_execution_id == ""
    event = run.events.last()
    assert event is not None
    assert event.event_type == "WORKSPACE_PROVISIONING_RECOVERY_QUEUED"
    evidence = job.recovery_history.get().evidence
    assert evidence["workspace_present"] is False
    assert evidence["provider_started"] is False


@pytest.mark.django_db
def test_fresh_starting_lease_is_not_recovered(
    provisioning_run: tuple[ExecutionRun, ExecutionJob],
) -> None:
    run, job = provisioning_run
    now = timezone.now()
    job.lease_expires_at = now + timedelta(seconds=60)
    job.last_heartbeat_at = now
    job.save(update_fields=["lease_expires_at", "last_heartbeat_at", "updated_at"])

    assert reconcile_stale_workspace_provisioning_jobs(now=now) == []
    job.refresh_from_db()
    run.refresh_from_db()
    assert job.status == ExecutionJob.Status.LEASED
    assert run.current_phase == "STARTING"


@pytest.mark.django_db
def test_workspace_provisioning_recovery_exhaustion_is_deterministic(
    provisioning_run: tuple[ExecutionRun, ExecutionJob],
) -> None:
    run, job = provisioning_run
    job.recovery_attempts = MAX_WORKSPACE_PROVISIONING_RECOVERY_ATTEMPTS
    job.save(update_fields=["recovery_attempts", "updated_at"])

    attempt = queue_workspace_provisioning_recovery(
        job,
        reason="TEST_RECOVERY_EXHAUSTION",
        now=timezone.now(),
    )

    assert attempt is not None
    job.refresh_from_db()
    run.refresh_from_db()
    assert attempt.outcome == ExecutionRecoveryAttempt.Outcome.REVIEW_REQUIRED
    assert job.status == ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    assert run.current_phase == "WORKSPACE_PROVISIONING_RECOVERY_EXHAUSTED"
    event = run.events.last()
    assert event is not None
    assert event.event_type == "WORKSPACE_PROVISIONING_RECOVERY_EXHAUSTED"


@pytest.mark.django_db
def test_reconciliation_command_recovers_stale_starting_lease(
    provisioning_run: tuple[ExecutionRun, ExecutionJob],
) -> None:
    _run, job = provisioning_run

    call_command("reconcile_execution_jobs", "--once")

    job.refresh_from_db()
    assert job.status == ExecutionJob.Status.RECOVERING


@pytest.mark.django_db
def test_worker_unhandled_provisioning_exception_is_durably_recoverable(
    provisioning_run: tuple[ExecutionRun, ExecutionJob],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run, job = provisioning_run
    job.status = ExecutionJob.Status.QUEUED
    job.lease_owner = ""
    job.lease_expires_at = None
    job.last_heartbeat_at = None
    job.save(
        update_fields=[
            "status",
            "lease_owner",
            "lease_expires_at",
            "last_heartbeat_at",
            "updated_at",
        ]
    )
    monkeypatch.setattr(
        "projects.management.commands.run_execution_worker.execute_claimed_job",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("interrupted")),
    )

    call_command(
        "run_execution_worker",
        "--once",
        "--worker-id",
        "test-provisioning-worker",
    )

    job.refresh_from_db()
    run.refresh_from_db()
    assert job.status == ExecutionJob.Status.RECOVERING
    assert run.current_phase == "WORKSPACE_RECOVERY_PENDING"
    event = run.events.last()
    assert event is not None
    assert event.event_type == "WORKSPACE_PROVISIONING_RECOVERY_QUEUED"

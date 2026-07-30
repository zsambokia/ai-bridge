"""Acceptance coverage for the local execution break-glass command."""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Iterator, cast

import pytest
from django.core.management import call_command
from django.utils import timezone

from projects.execution import claim_next_job
from projects.force_terminalization import (
    ForceTerminalizationRefused,
    force_terminalize_execution,
)
from projects.models import (
    ExecutionContract,
    ExecutionJob,
    ExecutionProgressEvent,
    ExecutionRun,
    ExecutionStartRequest,
    ExecutionWorkspace,
)
from projects.tests.test_execution import (
    consumed_contract as execution_contract_fixture,
)


@pytest.fixture
def consumed_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Path, ExecutionContract, ExecutionStartRequest]]:
    fixture = cast(
        object,
        getattr(execution_contract_fixture, "__wrapped__"),
    )
    yield from cast(
        Iterator[tuple[Path, ExecutionContract, ExecutionStartRequest]],
        fixture(tmp_path, monkeypatch),  # type: ignore[operator]
    )


def _run(
    contract: object,
    request: object,
    *,
    lifecycle: str = ExecutionRun.Lifecycle.REQUESTED,
    provider_execution_id: str = "",
) -> ExecutionRun:
    return ExecutionRun.objects.create(
        contract=cast(ExecutionContract, contract),
        start_request=cast(ExecutionStartRequest, request),
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash="b" * 64,
        workspace_identifier="C:/safe/workspace",
        provider_name="codex-cli",
        provider_execution_id=provider_execution_id,
        lifecycle=lifecycle,
        current_phase="QUEUED"
        if lifecycle == ExecutionRun.Lifecycle.REQUESTED
        else "EXECUTING",
        evidence_root="docs/evidence/test",
    )


@pytest.mark.django_db
def test_requested_execution_is_cancelled_and_lease_is_cleared(
    consumed_contract: tuple[Path, object, object],
) -> None:
    _, contract, request = consumed_contract
    typed_contract = cast(ExecutionContract, contract)
    run = _run(contract, request)
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.LEASED,
        lease_owner="dead-worker",
        lease_expires_at=timezone.now(),
        last_heartbeat_at=timezone.now(),
    )

    result = force_terminalize_execution(
        run.token, reason="incident", operator="Product Owner", preserve_workspace=True
    )

    run.refresh_from_db()
    job.refresh_from_db()
    assert result.action == "TERMINALIZED"
    assert run.lifecycle == ExecutionRun.Lifecycle.CANCELLED
    typed_contract.refresh_from_db()
    assert typed_contract.lifecycle == ExecutionContract.Lifecycle.CANCELLED
    assert run.ended_at is not None
    assert job.status == ExecutionJob.Status.FAILED
    assert not job.lease_owner and job.lease_expires_at is None
    assert job.last_heartbeat_at is None and job.next_recovery_at is None
    assert claim_next_job("another-worker", 30) is None
    event = run.events.get(event_type="EXECUTION_BREAK_GLASS_TERMINALIZED")
    assert event.details["break_glass"] is True
    assert event.details["last_heartbeat_at"]
    assert event.details["workspace_cleanup_performed"] is False


@pytest.mark.django_db
def test_stale_running_execution_requires_exit_evidence_and_preserves_workspace(
    consumed_contract: tuple[Path, object, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, contract, request = consumed_contract
    run = _run(
        contract,
        request,
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        provider_execution_id="42",
    )
    ExecutionJob.objects.create(run=run, status=ExecutionJob.Status.STARTED)
    workspace = ExecutionWorkspace.objects.create(
        run=run,
        status=ExecutionWorkspace.Status.IN_USE,
        root_path="C:/safe/workspace",
        provider_pid=42,
    )
    # Seed a historical provider-exit projection directly.  Normal event
    # ingestion now terminalizes this event immediately, while this test
    # exercises the explicitly break-glass-only repair of legacy stale data.
    ExecutionProgressEvent.objects.create(
        run=run,
        sequence=1,
        event_type="PROVIDER_COMPLETED",
        details={"provider_event_type": "process.exit", "exit_code": 0},
    )
    monkeypatch.setattr(
        "projects.force_terminalization.provider",
        lambda identity: type(
            "StoppedProvider", (), {"status": lambda self, pid: "FINISHED"}
        )(),
    )

    force_terminalize_execution(
        run.token,
        reason="stale provider",
        operator="Product Owner",
        preserve_workspace=True,
    )

    run.refresh_from_db()
    workspace.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.CANCELLED
    assert workspace.status == ExecutionWorkspace.Status.RETAINED
    assert workspace.provider_pid is None
    assert workspace.root_path == "C:/safe/workspace"
    event = run.events.get(event_type="EXECUTION_BREAK_GLASS_TERMINALIZED")
    assert event.details["provider_pid_state"] == "FINISHED"
    assert event.details["provider_exit_evidence"]["event_type"] == "PROVIDER_COMPLETED"


@pytest.mark.django_db
def test_recovering_restart_of_finished_provider_is_terminalized(
    consumed_contract: tuple[Path, object, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, contract, request = consumed_contract
    typed_contract = cast(ExecutionContract, contract)
    typed_contract.lifecycle = ExecutionContract.Lifecycle.RUNNING
    typed_contract.save(update_fields=["lifecycle"])
    run = _run(contract, request, lifecycle=ExecutionRun.Lifecycle.STARTING)
    run.current_phase = "RECOVERING"
    run.save(update_fields=["current_phase"])
    job = ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.RECOVERING,
        provider_attempt_metadata={"provider_execution_id": "42"},
    )
    workspace = ExecutionWorkspace.objects.create(
        run=run,
        status=ExecutionWorkspace.Status.IN_USE,
        root_path="C:/safe/workspace",
        provider_pid=42,
    )
    # This is a legacy event stored before canonical terminalization existed.
    ExecutionProgressEvent.objects.create(
        run=run,
        sequence=1,
        event_type="PROVIDER_COMPLETED",
        details={"provider_event_type": "process.exit", "exit_code": 0},
    )
    monkeypatch.setattr(
        "projects.force_terminalization.provider",
        lambda identity: type(
            "StoppedProvider", (), {"status": lambda self, pid: "FINISHED"}
        )(),
    )

    result = force_terminalize_execution(
        run.token,
        reason="prevent unsafe restart",
        operator="Product Owner",
        preserve_workspace=True,
    )

    run.refresh_from_db()
    job.refresh_from_db()
    workspace.refresh_from_db()
    typed_contract.refresh_from_db()
    assert result.action == "TERMINALIZED"
    assert run.lifecycle == ExecutionRun.Lifecycle.CANCELLED
    assert job.status == ExecutionJob.Status.FAILED
    assert typed_contract.lifecycle == ExecutionContract.Lifecycle.CANCELLED
    assert workspace.status == ExecutionWorkspace.Status.RETAINED
    assert workspace.provider_pid is None


@pytest.mark.django_db
def test_refuses_a_running_provider_and_leaves_records_unchanged(
    consumed_contract: tuple[Path, object, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, contract, request = consumed_contract
    run = _run(
        contract,
        request,
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        provider_execution_id="42",
    )
    job = ExecutionJob.objects.create(run=run, status=ExecutionJob.Status.STARTED)
    monkeypatch.setattr(
        "projects.force_terminalization.provider",
        lambda identity: type(
            "LiveProvider", (), {"status": lambda self, pid: "RUNNING"}
        )(),
    )

    with pytest.raises(
        ForceTerminalizationRefused, match="PROVIDER_PROCESS_STILL_RUNNING"
    ):
        force_terminalize_execution(
            run.token,
            reason="incident",
            operator="Product Owner",
            preserve_workspace=True,
        )

    run.refresh_from_db()
    job.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert job.status == ExecutionJob.Status.STARTED
    assert not run.events.filter(
        event_type="EXECUTION_BREAK_GLASS_TERMINALIZED"
    ).exists()


@pytest.mark.django_db
def test_dry_run_and_repeat_are_non_destructive_or_idempotent(
    consumed_contract: tuple[Path, object, object],
) -> None:
    _, contract, request = consumed_contract
    run = _run(contract, request)
    job = ExecutionJob.objects.create(run=run)

    dry_run = force_terminalize_execution(
        run.token,
        reason="incident",
        operator="Product Owner",
        preserve_workspace=True,
        dry_run=True,
    )
    run.refresh_from_db()
    job.refresh_from_db()
    assert dry_run.action == "WOULD_TERMINALIZE"
    assert dry_run.run_lifecycle_after == ExecutionRun.Lifecycle.CANCELLED
    assert dry_run.job_status_after == ExecutionJob.Status.FAILED
    assert dry_run.contract_lifecycle_after == ExecutionContract.Lifecycle.CANCELLED
    assert run.lifecycle == ExecutionRun.Lifecycle.REQUESTED
    assert job.status == ExecutionJob.Status.QUEUED

    force_terminalize_execution(
        run.token, reason="incident", operator="Product Owner", preserve_workspace=True
    )
    repeat = force_terminalize_execution(
        run.token, reason="incident", operator="Product Owner", preserve_workspace=True
    )
    assert repeat.idempotent is True
    assert repeat.action == "ALREADY_TERMINAL"
    assert (
        run.events.filter(event_type="EXECUTION_BREAK_GLASS_TERMINALIZED").count() == 1
    )


@pytest.mark.django_db
def test_atomic_rollback_when_audit_append_fails(
    consumed_contract: tuple[Path, object, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, contract, request = consumed_contract
    run = _run(contract, request)
    job = ExecutionJob.objects.create(
        run=run, status=ExecutionJob.Status.LEASED, lease_owner="worker"
    )
    monkeypatch.setattr(
        "projects.force_terminalization.add_event",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("audit failure")),
    )

    with pytest.raises(RuntimeError, match="audit failure"):
        force_terminalize_execution(
            run.token,
            reason="incident",
            operator="Product Owner",
            preserve_workspace=True,
        )

    run.refresh_from_db()
    job.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.REQUESTED
    assert job.status == ExecutionJob.Status.LEASED
    assert job.lease_owner == "worker"


@pytest.mark.django_db
def test_management_command_emits_a_machine_readable_dry_run(
    consumed_contract: tuple[Path, object, object],
) -> None:
    _, contract, request = consumed_contract
    run = _run(contract, request)
    ExecutionJob.objects.create(run=run)
    output = StringIO()

    call_command(
        "force_terminalize_execution",
        str(run.token),
        "--reason",
        "incident",
        "--operator",
        "Product Owner",
        "--preserve-workspace",
        "--dry-run",
        stdout=output,
    )

    assert json.loads(output.getvalue())["action"] == "WOULD_TERMINALIZE"

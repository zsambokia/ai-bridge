"""Execution boundary tests using a consumed canonical v2 contract."""

from __future__ import annotations

from datetime import timedelta
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Iterator

import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from projects.contracts import (
    _normalized_hash,
    consume_execution_contract,
    generate_scope_execution_contract,
    issue_execution_contract,
    validate_execution_contract,
)
from projects.execution import (
    ProviderStart,
    _safe_details,
    add_event,
    claim_next_job,
    complete_run,
    enqueue_run,
    execute_claimed_job,
    heartbeat_job,
    is_non_retryable_execution_failure,
    record_gate_rerun,
    reject_claimed_job,
    repair_failure,
    requeue_workspace_provisioning_failure,
    start_run,
)
from projects.execution_activity import (
    activity_summary,
    event_view,
    heartbeat_projection,
)
from projects.models import (
    ExecutableScope,
    ExecutionContract,
    ExecutionJob,
    ExecutionRun,
    ExecutionStartRequest,
    ExecutionWorkspace,
    GovernanceApproval,
    Project,
)
from projects.scopes import bind_approval, propose_scope, publish_scope
from projects.services import bootstrap_project
from projects.tests.test_services import write_definition
from projects.workspace import WorkspaceManager


class StubProvider:
    name = "stub"

    def start(self, *, repository: Path, prompt: str) -> ProviderStart:
        assert "never expose credentials" in prompt
        return ProviderStart("provider-42", str(repository))

    def status(self, execution_id: str) -> str:
        return "RUNNING"

    def cancel(self, execution_id: str) -> None:
        return None


class ActivityStubProvider(StubProvider):
    def start_with_activity(
        self,
        *,
        repository: Path,
        prompt: str,
        activity_callback: Callable[[dict[str, object]], None],
    ) -> ProviderStart:
        activity_callback(
            {
                "activity_type": "task_started",
                "message": "Codex reported task_started",
            }
        )
        return self.start(repository=repository, prompt=prompt)


class TestWorkspaceManager:
    """Controlled workspace boundary for legacy contract tests.

    These tests intentionally use a synthetic baseline hash; production
    provisioning is exercised separately against a real Git repository.
    """

    def provision(self, run: ExecutionRun) -> ExecutionWorkspace:
        workspace, _ = ExecutionWorkspace.objects.get_or_create(
            run=run,
            defaults={
                "status": ExecutionWorkspace.Status.READY,
                "root_path": run.workspace_identifier,
                "repository_path": run.workspace_identifier,
                "base_commit_sha": run.baseline_commit,
                "base_ref": run.baseline_commit,
                "python_executable": "test-python",
                "environment": {},
                "database_profile": {"mode": "sqlite"},
            },
        )
        workspace.status = ExecutionWorkspace.Status.READY
        workspace.save(update_fields=["status", "updated_at"])
        return workspace

    def descriptor(
        self, workspace: ExecutionWorkspace, run: ExecutionRun
    ) -> dict[str, object]:
        return {
            "cwd": workspace.repository_path,
            "repository_root": workspace.repository_path,
            "repository_url": "https://example.test/repository.git",
            "base_commit_sha": run.baseline_commit,
            "python_executable": "test-python",
            "virtual_environment": "test-venv",
            "environment": {},
            "database_profile": {"mode": "sqlite"},
            "application_database": {"mode": "sqlite"},
            "migration_state": {"status": "APPLIED", "verified": True},
            "seed_state": {"status": "SKIPPED"},
            "runtime_services": [],
            "provider_environment": {},
            "health_state": "HEALTHY",
            "workspace_id": str(workspace.token),
            "execution_token": str(run.token),
        }

    def mark_in_use(
        self, workspace: ExecutionWorkspace, provider_pid: int | None = None
    ) -> None:
        workspace.status = ExecutionWorkspace.Status.IN_USE
        workspace.provider_pid = provider_pid
        workspace.save(update_fields=["status", "provider_pid", "updated_at"])

    def retain(self, workspace: ExecutionWorkspace, run: ExecutionRun) -> None:
        workspace.status = ExecutionWorkspace.Status.RETAINED
        workspace.save(update_fields=["status", "updated_at"])

    def mark_validating(self, workspace: ExecutionWorkspace) -> None:
        workspace.status = ExecutionWorkspace.Status.VALIDATING
        workspace.save(update_fields=["status", "updated_at"])


@pytest.fixture
def consumed_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Path, ExecutionContract, ExecutionStartRequest]]:
    definition = write_definition(tmp_path)
    for target in ("projects.services", "projects.contracts"):
        monkeypatch.setattr(
            f"{target}._repository_identity", lambda root: "example/generic-project"
        )
        monkeypatch.setattr(f"{target}._current_branch", lambda root: "main")
        monkeypatch.setattr(f"{target}._head_sha", lambda root: "a" * 40)
    monkeypatch.setattr("projects.contracts._baseline_exists", lambda root, sha: True)
    monkeypatch.setattr(
        "projects.contracts._is_descendant_of", lambda root, ancestor, head: True
    )
    monkeypatch.setattr(
        "projects.execution.check_health", lambda entry: {"status": "HEALTHY"}
    )
    monkeypatch.setattr("projects.execution.WorkspaceManager", TestWorkspaceManager)
    assert bootstrap_project(definition, "docs/sprints/SPRINT_003.md", tmp_path).success
    project = Project.objects.get(project_id="generic-project")
    scope = propose_scope(
        project, "Run the provider only after consumption.", kind="WORK_ITEM"
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-010-run",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    scope = publish_scope(bind_approval(scope, approval.reference), tmp_path)
    contract = generate_scope_execution_contract(scope, tmp_path)
    contract = issue_execution_contract(
        validate_execution_contract(contract, tmp_path), tmp_path
    )
    contract = consume_execution_contract(
        contract,
        tmp_path,
        expected_hash=contract.contract_hash,
        provider_identity="codex-cli",
        observed_baseline="a" * 40,
        schema_version="2.0",
        idempotency_key="run-010",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    yield tmp_path, contract, request


@pytest.mark.django_db
def test_provider_starts_only_after_consumption(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert contract.lifecycle == "RUNNING"
    assert list(run.events.values_list("sequence", "event_type")) == [
        (1, "PREFLIGHT_COMPLETED"),
        (2, "WORKSPACE_REQUESTED"),
        (3, "WORKSPACE_PROVISIONING_STARTED"),
        (4, "WORKSPACE_REPOSITORY_READY"),
        (5, "WORKSPACE_VENV_READY"),
        (6, "WORKSPACE_DEPENDENCIES_READY"),
        (7, "WORKSPACE_DATABASE_READY"),
        (8, "APPLICATION_DATABASE_CREATED"),
        (9, "APPLICATION_MIGRATED"),
        (10, "APPLICATION_SEED_SKIPPED"),
        (11, "RUNTIME_SERVICES_SKIPPED"),
        (12, "WORKSPACE_PREFLIGHT_PASSED"),
        (13, "WORKSPACE_READY"),
        (14, "EXECUTOR_STARTED"),
        (15, "EXECUTION_ACTIVITY_STARTED"),
    ]


@pytest.mark.django_db
def test_provider_terminal_event_closes_the_canonical_lifecycle(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    job = ExecutionJob.objects.create(run=run, status=ExecutionJob.Status.STARTED)

    add_event(run, "PROVIDER_OUTPUT", activity_type="turn.completed")

    run.refresh_from_db()
    job.refresh_from_db()
    contract.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    assert run.current_phase == "PROVIDER_TERMINALIZED"
    assert run.terminal_state == "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"
    assert job.status == ExecutionJob.Status.FAILED
    assert contract.lifecycle == ExecutionContract.Lifecycle.CANCELLED
    assert contract.closure_state == run.terminal_state
    assert run.events.filter(
        event_type="PROVIDER_TERMINAL_LIFECYCLE_TERMINALIZED"
    ).exists()


@pytest.mark.django_db
def test_workspace_cleanup_is_token_scoped_and_idempotent(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    workspace_root = tmp_path / "managed-workspaces"
    monkeypatch.setattr(settings, "BRIDGE_WORKSPACE_ROOT", workspace_root)
    monkeypatch.setattr(settings, "BRIDGE_REPOSITORY_CACHE_ROOT", tmp_path / "cache")
    run = start_run(contract, request, root)
    workspace = run.workspace
    path = workspace_root / str(workspace.token)
    path.mkdir(parents=True)
    (path / "marker.txt").write_text("workspace only", encoding="utf-8")
    workspace.root_path = str(path)
    workspace.status = ExecutionWorkspace.Status.RETAINED
    workspace.retention_until = timezone.now() - timedelta(seconds=1)
    workspace.save(
        update_fields=["root_path", "status", "retention_until", "updated_at"]
    )

    manager = WorkspaceManager()
    assert [item.pk for item in manager.reconcile_cleanup()] == [workspace.pk]
    workspace.refresh_from_db()
    assert workspace.status == ExecutionWorkspace.Status.CLEANED
    assert not path.exists()
    assert run.events.filter(event_type="WORKSPACE_CLEANUP_STARTED").exists()
    assert run.events.filter(event_type="WORKSPACE_CLEANED").exists()
    assert manager.reconcile_cleanup() == []


@pytest.mark.django_db
def test_workspace_failure_can_be_requeued_without_provider_execution(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = consumed_contract
    job = enqueue_run(contract, request, root)
    run = job.run
    job.status = ExecutionJob.Status.FAILED
    job.save(update_fields=["status", "updated_at"])
    run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
    run.current_phase = "WORKSPACE_FAILED"
    run.current_blocker = {"reason": "WORKSPACE_PROVISIONING_FAILED"}
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "current_blocker",
            "updated_at",
        ]
    )

    requeued = requeue_workspace_provisioning_failure(run)

    requeued.refresh_from_db()
    assert requeued.status == ExecutionJob.Status.QUEUED
    assert requeued.provider_attempt_metadata["recovery_action"] == (
        "RESTART_WORKSPACE_PROVISIONING"
    )
    assert run.events.filter(
        event_type="WORKSPACE_PROVISIONING_REQUEUED"
    ).exists()


@pytest.mark.django_db
def test_start_recovers_an_unbound_starting_run(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    stale_run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=contract.payload["project"]["repository"],
        branch=contract.payload["execution"]["target_branch"],
        baseline_commit=contract.payload["execution"]["baseline_commit"],
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.STARTING,
        current_phase="STARTING",
        evidence_root=contract.payload["evidence"]["root"],
        started_at=None,
    )
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )

    run = start_run(contract, request, root)

    assert run.pk == stale_run.pk
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert ExecutionRun.objects.filter(contract=contract).count() == 1
    assert list(run.events.values_list("sequence", "event_type")) == [
        (1, "START_RECOVERED"),
        (2, "WORKSPACE_REQUESTED"),
        (3, "WORKSPACE_PROVISIONING_STARTED"),
        (4, "WORKSPACE_REPOSITORY_READY"),
        (5, "WORKSPACE_VENV_READY"),
        (6, "WORKSPACE_DEPENDENCIES_READY"),
        (7, "WORKSPACE_DATABASE_READY"),
        (8, "APPLICATION_DATABASE_CREATED"),
        (9, "APPLICATION_MIGRATED"),
        (10, "APPLICATION_SEED_SKIPPED"),
        (11, "RUNTIME_SERVICES_SKIPPED"),
        (12, "WORKSPACE_PREFLIGHT_PASSED"),
        (13, "WORKSPACE_READY"),
        (14, "EXECUTOR_STARTED"),
        (15, "EXECUTION_ACTIVITY_STARTED"),
    ]


@pytest.mark.django_db
def test_start_recovers_a_cancelled_run_with_its_original_request(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    cancelled_run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=contract.payload["project"]["repository"],
        branch=contract.payload["execution"]["target_branch"],
        baseline_commit=contract.payload["execution"]["baseline_commit"],
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        provider_execution_id="cancelled-provider",
        lifecycle=ExecutionRun.Lifecycle.CANCELLED,
        current_phase="CANCELLED",
        evidence_root=contract.payload["evidence"]["root"],
        started_at=None,
    )
    contract.lifecycle = ExecutionContract.Lifecycle.RUNNING
    contract.save(update_fields=["lifecycle"])
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )

    run = start_run(contract, request, root)

    assert run.pk == cancelled_run.pk
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert ExecutionRun.objects.filter(contract=contract).count() == 1
    assert run.provider_execution_id == "provider-42"


@pytest.mark.django_db
def test_start_retries_a_transient_provider_launch_once(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract

    class TransientProvider(StubProvider):
        launches = 0

        def start(self, *, repository: Path, prompt: str) -> ProviderStart:
            self.launches += 1
            if self.launches == 1:
                raise ValueError("CODEX_SUBPROCESS_EXITED_EARLY")
            return ProviderStart("provider-43", str(repository))

    transient = TransientProvider()
    monkeypatch.setattr("projects.execution.provider", lambda identity=None: transient)

    run = start_run(contract, request, root)

    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert run.attempt_count == 2
    assert list(run.events.values_list("sequence", "event_type")) == [
        (1, "PREFLIGHT_COMPLETED"),
        (2, "WORKSPACE_REQUESTED"),
        (3, "WORKSPACE_PROVISIONING_STARTED"),
        (4, "WORKSPACE_REPOSITORY_READY"),
        (5, "WORKSPACE_VENV_READY"),
        (6, "WORKSPACE_DEPENDENCIES_READY"),
        (7, "WORKSPACE_DATABASE_READY"),
        (8, "APPLICATION_DATABASE_CREATED"),
        (9, "APPLICATION_MIGRATED"),
        (10, "APPLICATION_SEED_SKIPPED"),
        (11, "RUNTIME_SERVICES_SKIPPED"),
        (12, "WORKSPACE_PREFLIGHT_PASSED"),
        (13, "WORKSPACE_READY"),
        (14, "PROVIDER_START_RETRYING"),
        (15, "EXECUTOR_STARTED"),
        (16, "EXECUTION_ACTIVITY_STARTED"),
    ]


@pytest.mark.django_db
def test_completion_requires_a_real_completed_run(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: ActivityStubProvider()
    )
    run = start_run(contract, request, root)
    completion: dict[str, object] = {
        "execution_result": "PASS",
        "gate_results": {"pytest": "PASS"},
        "evidence_manifest": {"closure_report": "report"},
        "changed_files": [],
        "failure_classification": None,
    }
    monkeypatch.setattr(
        "projects.execution.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="b" * 40 + "\n"),
    )
    completed = complete_run(run, "b" * 40, completion)
    assert completed.lifecycle == ExecutionRun.Lifecycle.COMPLETED
    assert completed.terminal_state == "PASS"
    assert completed.completion_data == completion


@pytest.mark.django_db
def test_read_only_audit_cannot_report_a_repository_mutation(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    contract.payload["execution"]["audit"] = {"mutation_policy": "READ_ONLY"}
    contract.contract_hash = _normalized_hash(contract.payload)
    contract.save(update_fields=["contract_hash"])
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    completion: dict[str, object] = {
        "execution_result": "PASS",
        "gate_results": {"pytest": "PASS"},
        "evidence_manifest": {"closure_report": "report"},
        "changed_files": ["projects/execution.py"],
        "failure_classification": None,
    }
    with pytest.raises(ValueError, match="READ_ONLY_AUDIT_MUTATION_REJECTED"):
        complete_run(run, "b" * 40, completion)


def test_secret_filter_redacts_credential_named_fields() -> None:
    assert _safe_details({"token": "x", "message": "okay"}) == {
        "token": "[REDACTED]",
        "message": "okay",
    }
    assert _safe_details({"message": "Bearer xyz"}) == {"message": "[REDACTED]"}


@pytest.mark.django_db
def test_activity_summary_is_derived_from_canonical_run_and_events(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: ActivityStubProvider()
    )
    run = start_run(contract, request, root)

    summary = activity_summary(run)

    assert summary["phase"] == "EXECUTING"
    assert len(summary["checklist"]) == 8
    assert (
        next(item for item in summary["checklist"] if item["id"] == "execution")[
            "status"
        ]
        == "IN_PROGRESS"
    )
    event = event_view(run.events.get(event_type="EXECUTOR_STARTED"))
    assert event["actor"] == "Codex"
    assert event["title"] == "Codex execution started"
    provider_event = event_view(run.events.get(event_type="PROVIDER_MESSAGE"))
    assert provider_event["details"] == {
        "activity_type": "task_started",
        "message": "Codex reported task_started",
    }


@pytest.mark.django_db
def test_heartbeat_is_derived_without_mutating_a_run(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    original_updated_at = run.updated_at
    latest = run.events.order_by("-sequence").first()
    assert latest is not None

    projection = heartbeat_projection(
        run, observed_at=latest.created_at + timedelta(seconds=901)
    )

    run.refresh_from_db()
    assert projection["heartbeat_status"] == "POSSIBLY_STALLED"
    assert projection["latest_event_type"] == "EXECUTION_ACTIVITY_STARTED"
    assert run.updated_at == original_updated_at


@pytest.mark.django_db
def test_repair_gate_rerun_updates_the_derived_activity_checklist(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: ActivityStubProvider()
    )
    run = start_run(contract, request, root)

    assert repair_failure(run, "ruff check failed") == "build/lint/type defect"
    repairing = activity_summary(run)
    assert (
        next(item for item in repairing["checklist"] if item["id"] == "repair")[
            "status"
        ]
        == "FAILED_REPAIRING"
    )

    record_gate_rerun(run, "ruff check .", passed=True)
    run.refresh_from_db()
    summary = activity_summary(run)
    assert run.gate_rerun_count == 1
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert (
        next(item for item in summary["checklist"] if item["id"] == "repair")["status"]
        == "COMPLETED"
    )
    assert list(
        run.events.filter(
            event_type__in={
                "ROOT_CAUSE_IDENTIFIED",
                "REPAIR_APPLIED",
                "GATE_RERUN_STARTED",
                "GATE_RERUN_PASSED",
                "REPAIR_VERIFIED",
            }
        ).values_list("event_type", flat=True)
    ) == [
        "ROOT_CAUSE_IDENTIFIED",
        "REPAIR_APPLIED",
        "GATE_RERUN_STARTED",
        "GATE_RERUN_PASSED",
        "REPAIR_VERIFIED",
    ]


@pytest.mark.django_db
def test_durable_queue_is_claimed_by_an_independent_worker(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )

    job = enqueue_run(contract, request, root)
    assert job.status == ExecutionJob.Status.QUEUED
    assert job.run.lifecycle == ExecutionRun.Lifecycle.REQUESTED
    assert job.run.events.get().event_type == "EXECUTION_ENQUEUED"

    claimed = claim_next_job("worker-a", 60)
    assert claimed is not None
    run = execute_claimed_job(claimed, "worker-a", root)

    claimed.refresh_from_db()
    assert claimed.status == ExecutionJob.Status.STARTED
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert "WORKER_LEASE_ACQUIRED" in list(
        run.events.values_list("event_type", flat=True)
    )


@pytest.mark.django_db
def test_expired_worker_lease_is_reclaimed_without_losing_the_execution(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = consumed_contract
    job = enqueue_run(contract, request, root)
    first = claim_next_job("worker-a", 60)
    assert first is not None
    job.lease_expires_at = timezone.now() - timedelta(seconds=1)
    job.save(update_fields=["lease_expires_at"])

    reclaimed = claim_next_job("worker-b", 60)
    assert reclaimed is not None
    assert reclaimed.pk == job.pk
    assert reclaimed.lease_owner == "worker-b"
    assert reclaimed.run.events.filter(event_type="WORKER_LEASE_RECLAIMED").exists()


@pytest.mark.django_db
def test_expired_worker_cannot_write_after_a_fenced_reclaim(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = consumed_contract
    job = enqueue_run(contract, request, root)
    first = claim_next_job("worker-a", 60)
    assert first is not None
    job.refresh_from_db()
    job.lease_expires_at = timezone.now() - timedelta(seconds=1)
    job.save(update_fields=["lease_expires_at"])

    reclaimed = claim_next_job("worker-b", 60)
    assert reclaimed is not None
    assert reclaimed.lease_fencing_token == first.lease_fencing_token + 1
    with pytest.raises(ValueError, match="WORKER_FENCING_TOKEN_STALE"):
        heartbeat_job(first, "worker-a", 60)


@pytest.mark.django_db
def test_worker_command_starts_a_queued_job_outside_the_web_process(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    monkeypatch.setattr(
        "projects.management.commands.run_execution_worker.settings.BASE_DIR", root
    )
    job = enqueue_run(contract, request, root)

    stdout = StringIO()
    call_command(
        "run_execution_worker",
        "--once",
        "--worker-id",
        "worker-command",
        stdout=stdout,
    )

    job.refresh_from_db()
    assert job.status == ExecutionJob.Status.STARTED
    assert job.run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert str(job.run.token) in stdout.getvalue()


@pytest.mark.django_db
def test_invalid_contract_is_rejected_without_provider_or_reclaim(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
) -> None:
    root, contract, request = consumed_contract
    job = enqueue_run(contract, request, root)
    payload = contract.payload.copy()
    payload["approved_scope"] = payload["approved_scope"].copy()
    del payload["approved_scope"]["proposal_hash"]
    contract.payload = payload
    contract.contract_hash = _normalized_hash(payload)
    contract.save(update_fields=["payload", "contract_hash"])

    claimed = claim_next_job("worker-a", 60)
    assert claimed is not None
    with pytest.raises(
        ValueError, match="CONTRACT_INTEGRITY_FAILURE:SCOPE_BINDING_MISMATCH"
    ) as raised:
        execute_claimed_job(claimed, "worker-a", root)
    assert is_non_retryable_execution_failure(raised.value)
    reject_claimed_job(claimed, "worker-a", raised.value)

    job.refresh_from_db()
    job.run.refresh_from_db()
    assert job.status == ExecutionJob.Status.REJECTED
    assert job.lease_owner == ""
    assert job.lease_expires_at is None
    assert job.run.lifecycle == ExecutionRun.Lifecycle.FAILED_GOVERNANCE
    assert job.run.provider_execution_id == ""
    assert job.run.events.filter(event_type="EXECUTION_JOB_REJECTED").exists()
    assert job.reconciliation_evidence[-1]["retryable"] is False
    assert claim_next_job("worker-b", 60) is None


@pytest.mark.django_db
def test_worker_continues_from_rejected_contract_to_next_valid_job(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, invalid_contract, invalid_request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    monkeypatch.setattr(
        "projects.management.commands.run_execution_worker.settings.BASE_DIR", root
    )
    invalid_job = enqueue_run(invalid_contract, invalid_request, root)
    invalid_payload = invalid_contract.payload.copy()
    invalid_payload["approved_scope"] = invalid_payload["approved_scope"].copy()
    del invalid_payload["approved_scope"]["proposal_hash"]
    invalid_contract.payload = invalid_payload
    invalid_contract.contract_hash = _normalized_hash(invalid_payload)
    invalid_contract.save(update_fields=["payload", "contract_hash"])

    scope = ExecutableScope.objects.get(
        identifier=invalid_payload["approved_scope"]["identifier"]
    )
    second_invalid_contract = generate_scope_execution_contract(scope, root)
    second_invalid_contract = issue_execution_contract(
        validate_execution_contract(second_invalid_contract, root), root
    )
    second_invalid_contract = consume_execution_contract(
        second_invalid_contract,
        root,
        expected_hash=second_invalid_contract.contract_hash,
        provider_identity="codex-cli",
        observed_baseline="a" * 40,
        schema_version="2.0",
        idempotency_key="run-011",
    )
    second_invalid_request = ExecutionStartRequest.objects.create(
        contract=second_invalid_contract, approval=invalid_request.approval
    )
    second_invalid_job = enqueue_run(
        second_invalid_contract, second_invalid_request, root
    )
    second_invalid_payload = second_invalid_contract.payload.copy()
    second_invalid_payload["approved_scope"] = second_invalid_payload[
        "approved_scope"
    ].copy()
    del second_invalid_payload["approved_scope"]["proposal_hash"]
    second_invalid_contract.payload = second_invalid_payload
    second_invalid_contract.contract_hash = _normalized_hash(second_invalid_payload)
    second_invalid_contract.save(update_fields=["payload", "contract_hash"])

    valid_contract = generate_scope_execution_contract(scope, root)
    valid_contract = issue_execution_contract(
        validate_execution_contract(valid_contract, root), root
    )
    valid_contract = consume_execution_contract(
        valid_contract,
        root,
        expected_hash=valid_contract.contract_hash,
        provider_identity="codex-cli",
        observed_baseline="a" * 40,
        schema_version="2.0",
        idempotency_key="run-012",
    )
    valid_request = ExecutionStartRequest.objects.create(
        contract=valid_contract, approval=invalid_request.approval
    )
    valid_job = enqueue_run(valid_contract, valid_request, root)

    stdout = StringIO()
    call_command(
        "run_execution_worker",
        "--max-jobs",
        "3",
        "--worker-id",
        "worker-command",
        stdout=stdout,
    )

    invalid_job.refresh_from_db()
    second_invalid_job.refresh_from_db()
    valid_job.refresh_from_db()
    assert invalid_job.status == ExecutionJob.Status.REJECTED
    assert invalid_job.run.provider_execution_id == ""
    assert second_invalid_job.status == ExecutionJob.Status.REJECTED
    assert second_invalid_job.run.provider_execution_id == ""
    assert valid_job.status == ExecutionJob.Status.STARTED
    assert valid_job.run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert "Continuing worker" in stdout.getvalue()

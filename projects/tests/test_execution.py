"""Execution boundary tests using a consumed canonical v2 contract."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Iterator

import pytest

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
    complete_run,
    reconcile_provider_completion,
    record_gate_rerun,
    repair_failure,
    start_factory_development,
    start_run,
    watchdog_recover_runs,
)
from projects.execution_activity import (
    activity_summary,
    event_view,
    heartbeat_projection,
)
from projects.models import (
    ExecutionContract,
    ExecutionRun,
    ExecutionStartRequest,
    GovernanceApproval,
    Project,
)
from projects.scopes import bind_approval, propose_scope, publish_scope
from projects.services import bootstrap_project
from projects.tests.test_services import write_definition


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


class FinishedStubProvider(StubProvider):
    def status(self, execution_id: str) -> str:
        return "FINISHED"


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
        (2, "EXECUTOR_STARTED"),
        (3, "EXECUTION_ACTIVITY_STARTED"),
    ]


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
        (2, "EXECUTOR_STARTED"),
        (3, "EXECUTION_ACTIVITY_STARTED"),
    ]


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
        (2, "PROVIDER_START_RETRYING"),
        (3, "EXECUTOR_STARTED"),
        (4, "EXECUTION_ACTIVITY_STARTED"),
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
    assert completed.completion_data == completion


@pytest.mark.django_db
def test_finished_provider_is_reconciled_once_into_validation(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: FinishedStubProvider()
    )

    reconciled = reconcile_provider_completion(run)
    second = reconcile_provider_completion(reconciled)

    assert reconciled.lifecycle == ExecutionRun.Lifecycle.VALIDATING
    assert reconciled.current_phase == "VALIDATING"
    assert second.pk == run.pk
    assert list(
        run.events.filter(
            event_type__in={"PROVIDER_FINISHED", "VALIDATION_CONTINUATION_READY"}
        ).values_list("event_type", flat=True)
    ) == ["PROVIDER_FINISHED", "VALIDATION_CONTINUATION_READY"]


@pytest.mark.django_db
def test_factory_profile_uses_durable_po_authority_without_a_contract(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, _request = consumed_contract
    project = contract.project
    project.project_id = "ai-bridge"
    project.repository_full_name = "zsambokia/ai-bridge"
    project.save(update_fields=["project_id", "repository_full_name"])
    monkeypatch.setattr("projects.execution.project_repository_root", lambda *_: root)
    monkeypatch.setattr(
        "projects.execution.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="c" * 40 + "\n"),
    )
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )

    run = start_factory_development(
        project,
        "PO-bootstrap-factory-001",
        "Repair the execution lifecycle.",
        root,
    )

    assert run.contract_id is None
    assert run.start_request_id is None
    assert run.execution_profile == ExecutionRun.Profile.FACTORY_DEVELOPMENT
    assert run.authority_reference == "PO-bootstrap-factory-001"
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    summary = activity_summary(run)
    assert summary["product_owner_progress"]["mode"] == "FACTORY_DEVELOPMENT"
    assert (
        summary["product_owner_progress"]["approval_reference"]
        == "PO-bootstrap-factory-001"
    )


@pytest.mark.django_db
def test_watchdog_counts_each_finished_provider_only_once(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: FinishedStubProvider()
    )

    assert watchdog_recover_runs() == 1
    assert watchdog_recover_runs() == 0
    run.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.VALIDATING


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


def test_secret_filter_removes_credential_named_fields() -> None:
    assert _safe_details({"token": "x", "message": "okay"}) == {"message": "okay"}
    assert _safe_details({"message": "Bearer xyz"}) == {"message": "[redacted]"}


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
    provider_event = event_view(run.events.get(event_type="PROVIDER_OUTPUT"))
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

"""Execution boundary tests using a consumed canonical v2 contract."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Iterator

import pytest

from projects.contracts import (
    _normalized_hash,
    consume_execution_contract,
    generate_scope_execution_contract,
    issue_execution_contract,
    validate_execution_contract,
)
from projects.execution import ProviderStart, _safe_details, complete_run, start_run
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
    ]


@pytest.mark.django_db
def test_completion_requires_a_real_completed_run(
    consumed_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = consumed_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
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

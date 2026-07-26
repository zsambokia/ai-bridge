"""Acceptance tests for the contract-bound external execution boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.contracts import (
    consume_execution_contract,
    generate_execution_contract,
    issue_execution_contract,
    validate_execution_contract,
)
from projects.execution import (
    ProviderStart,
    _safe_details,
    add_event,
    classify_failure,
    repair_failure,
    start_run,
)
from projects.models import (
    ExecutionContract,
    ExecutionRun,
    ExecutionStartRequest,
    GovernanceApproval,
    Project,
)
from projects.services import bootstrap_project
from projects.tests.test_services import write_definition


class StubProvider:
    name = "stub"

    def start(self, *, repository: Path, prompt: str) -> ProviderStart:
        assert "never expose credentials" in prompt
        return ProviderStart("provider-42", str(repository / "external-workspace"))

    def status(self, execution_id: str) -> str:
        return "RUNNING"

    def cancel(self, execution_id: str) -> None:
        return None


@pytest.fixture
def contract_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Project]:
    definition = write_definition(tmp_path)
    monkeypatch.setattr(
        "projects.services._repository_identity", lambda root: "example/generic-project"
    )
    monkeypatch.setattr("projects.services._current_branch", lambda root: "main")
    monkeypatch.setattr("projects.services._head_sha", lambda root: "a" * 40)
    monkeypatch.setattr("projects.contracts._head_sha", lambda root: "a" * 40)
    monkeypatch.setattr("projects.contracts._current_branch", lambda root: "main")
    monkeypatch.setattr(
        "projects.contracts._repository_identity",
        lambda root: "example/generic-project",
    )
    monkeypatch.setattr(
        "projects.contracts._baseline_exists", lambda root, baseline: True
    )
    monkeypatch.setattr(
        "projects.contracts._is_descendant_of", lambda root, ancestor, head: True
    )
    assert bootstrap_project(definition, "docs/sprints/SPRINT_003.md", tmp_path).success
    return tmp_path, Project.objects.get(project_id="generic-project")


def _consume(contract: ExecutionContract, root: Path) -> None:
    validated = validate_execution_contract(contract, root)
    consume_execution_contract(issue_execution_contract(validated), root)


@pytest.mark.django_db
def test_start_persists_audit_and_ordered_events_before_provider_run(
    contract_project: tuple[Path, Project], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, project = contract_project
    contract = generate_execution_contract(
        project, "docs/sprints/SPRINT_003.md", "FEATURE", "Dispatch work.", root
    )
    _consume(contract, root)
    approval = GovernanceApproval.objects.create(
        reference="execution-start",
        project=project,
        approved_action="execution.request_start",
        approved_by="po",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    monkeypatch.setattr("projects.execution.provider", lambda: StubProvider())

    run = start_run(contract, request, root)

    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert run.provider_execution_id == "provider-42"
    assert list(run.events.values_list("sequence", "event_type")) == [
        (1, "PREFLIGHT_COMPLETED"),
        (2, "EXECUTOR_STARTED"),
    ]


@pytest.mark.django_db
def test_progress_events_are_ordered_and_secret_free(
    contract_project: tuple[Path, Project], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, project = contract_project
    contract = generate_execution_contract(
        project, "docs/sprints/SPRINT_003.md", "FEATURE", "Dispatch work.", root
    )
    _consume(contract, root)
    approval = GovernanceApproval.objects.create(
        reference="event-start",
        project=project,
        approved_action="execution.request_start",
        approved_by="po",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    monkeypatch.setattr("projects.execution.provider", lambda: StubProvider())
    run = start_run(contract, request, root)

    event = add_event(run, "PROGRESS", api_token="hidden", detail="safe")

    assert event.sequence == 3
    assert event.details == {"detail": "safe"}


@pytest.mark.parametrize(
    ("signature", "expected"),
    [
        ("ruff E501", "build/lint/type defect"),
        ("makemigrations changed", "migration defect"),
        ("provider network unavailable", "unavailable external input"),
        ("needs product decision", "reserved Product Owner decision"),
    ],
)
def test_failure_classification_is_deterministic(signature: str, expected: str) -> None:
    assert classify_failure(signature) == expected


@pytest.mark.django_db
def test_routine_failure_enters_repair_and_external_failure_does_not(
    contract_project: tuple[Path, Project], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, project = contract_project
    contract = generate_execution_contract(
        project, "docs/sprints/SPRINT_003.md", "FEATURE", "Dispatch work.", root
    )
    _consume(contract, root)
    approval = GovernanceApproval.objects.create(
        reference="repair-start",
        project=project,
        approved_action="execution.request_start",
        approved_by="po",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    monkeypatch.setattr("projects.execution.provider", lambda: StubProvider())
    run = start_run(contract, request, root)

    assert repair_failure(run, "ruff E501") == "build/lint/type defect"
    assert run.attempt_count == 1
    with pytest.raises(ValueError, match="ROUTINE_TECHNICAL_ESCALATION_REJECTED"):
        repair_failure(run, "provider network unavailable")


def test_secret_filter_removes_credential_named_fields() -> None:
    assert _safe_details({"token": "x", "message": "okay"}) == {"message": "okay"}

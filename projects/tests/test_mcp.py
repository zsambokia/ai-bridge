"""MCP registration and canonical-scope authority coverage."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.mcp import invoke_operation, registered_operations
from projects.models import GovernanceApproval, Project, ProjectResolutionContinuation
from projects.scopes import bind_approval, propose_scope, publish_scope


def _ready_project(project_id: str, repository: str) -> Project:
    return Project.objects.create(
        project_id=project_id,
        display_name=f"{project_id} project",
        repository_full_name=repository,
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


@pytest.mark.django_db
def test_registered_surface_contains_canonical_lifecycle_only() -> None:
    operations = set(registered_operations())
    assert {
        "scope.classify",
        "sprint.propose",
        "work_item.propose",
        "scope.validate",
        "scope.approve",
        "scope.publish",
        "scope.get",
        "scope.contract.generate",
        "scope.complete",
        "scope.cancel",
        "scope.supersede",
        "validate_execution_contract",
        "issue_execution_contract",
        "consume_execution_contract",
        "complete_execution_contract",
    }.issubset(operations)
    assert "generate_execution_contract" not in operations
    assert "generate_execution_context" not in operations


@pytest.mark.django_db
def test_ambiguous_resolution_requires_input_and_continues_same_state(
    tmp_path: Path,
) -> None:
    first = _ready_project("bridge-alpha", "example/bridge-alpha")
    second = _ready_project("bridge-beta", "example/bridge-beta")
    response = invoke_operation("resolve_project", {"query": "bridge"}, tmp_path)
    token = response["continuation_token"]
    assert response["status"] == "USER_INPUT_REQUIRED"
    resumed = invoke_operation(
        "continue_project_resolution",
        {"continuation_token": token, "selected_project_id": second.project_id},
        tmp_path,
    )
    assert resumed["project"]["project_id"] == second.project_id
    assert (
        ProjectResolutionContinuation.objects.get(token=token).consumed_at is not None
    )
    assert first.project_id != second.project_id


@pytest.mark.django_db
def test_scope_operations_are_the_authoritative_context_path(tmp_path: Path) -> None:
    project = _ready_project("canonical", "example/canonical")
    scope = propose_scope(project, "Authoritative scope.", kind="WORK_ITEM")
    approval = GovernanceApproval.objects.create(
        reference="PO-mcp",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    scope = publish_scope(bind_approval(scope, approval.reference), tmp_path)
    response = invoke_operation(
        "scope.get", {"scope_identifier": scope.identifier}, tmp_path
    )
    assert response["status"] == "SCOPE_RETRIEVED"
    assert response["scope"]["content_hash"] == scope.content_hash
    assert (
        invoke_operation("generate_execution_context", {}, tmp_path)["status"]
        == "INVALID_OPERATION"
    )


@pytest.mark.django_db
def test_legacy_contract_operation_is_visible_but_fails_closed_without_orki(
    tmp_path: Path,
) -> None:
    project = _ready_project("gated-contract", "example/gated-contract")
    scope = propose_scope(project, "Normal governed work.", kind="WORK_ITEM")

    assert invoke_operation(
        "scope.contract.generate",
        {"scope_identifier": scope.identifier},
        tmp_path,
    ) == {"status": "ORCHESTRATION_GATE_REQUIRED"}

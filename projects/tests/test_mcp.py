"""Acceptance coverage for the lightweight MCP execution foundation."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.mcp import invoke_operation, registered_operations
from projects.models import Project, ProjectResolutionContinuation
from projects.services import bootstrap_project
from projects.tests.test_services import write_definition


def _ready_project(project_id: str, repository: str) -> Project:
    return Project.objects.create(
        project_id=project_id,
        display_name=f"{project_id} project",
        repository_full_name=repository,
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


@pytest.mark.django_db
def test_governance_operations_remain_registered_for_internal_services() -> None:
    assert {
        "continue_project_resolution",
        "generate_execution_context",
        "generate_execution_contract",
        "validate_execution_contract",
        "issue_execution_contract",
        "get_execution_contract",
        "render_execution_handoff",
        "consume_execution_contract",
        "complete_execution_contract",
        "supersede_execution_contract",
        "revoke_execution_contract",
        "resolve_project",
    }.issubset(set(registered_operations()))
    assert {
        "scope.classify",
        "sprint.propose",
        "work_item.propose",
        "scope.validate",
        "scope.approve",
        "scope.publish",
        "scope.get",
        "scope.contract.generate",
    }.issubset(set(registered_operations()))


@pytest.mark.django_db
def test_ambiguous_resolution_requires_input_and_continues_same_state(
    tmp_path: Path,
) -> None:
    first = _ready_project("bridge-alpha", "example/bridge-alpha")
    second = _ready_project("bridge-beta", "example/bridge-beta")

    response = invoke_operation("resolve_project", {"query": "bridge"}, tmp_path)

    assert response["status"] == "USER_INPUT_REQUIRED"
    token = response["continuation_token"]
    assert {item["project_id"] for item in response["candidates"]} == {
        first.project_id,
        second.project_id,
    }
    assert ProjectResolutionContinuation.objects.get(token=token).consumed_at is None

    resumed = invoke_operation(
        "continue_project_resolution",
        {"continuation_token": token, "selected_project_id": second.project_id},
        tmp_path,
    )

    assert resumed == {
        "status": "PROJECT_RESOLVED",
        "project": {
            "project_id": second.project_id,
            "display_name": second.display_name,
            "repository_full_name": second.repository_full_name,
        },
    }
    assert (
        ProjectResolutionContinuation.objects.get(token=token).selected_project_id
        == second.project_id
    )


@pytest.mark.django_db
def test_execution_context_is_generated_from_registry_context_and_definition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    definition_path = write_definition(tmp_path)
    monkeypatch.setattr(
        "projects.services._repository_identity", lambda root: "example/generic-project"
    )
    monkeypatch.setattr("projects.services._current_branch", lambda root: "main")
    monkeypatch.setattr("projects.services._head_sha", lambda root: "a" * 40)
    root = tmp_path
    result = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)
    assert result.success

    response = invoke_operation(
        "generate_execution_context",
        {
            "project_id": "generic-project",
            "approved_sprint_path": "docs/sprints/SPRINT_003.md",
        },
        root,
    )

    assert response["status"] == "EXECUTION_CONTEXT_GENERATED"
    context = response["execution_context"]
    assert response["codex_execution_package"] == context
    assert context["target_repository"] == "example/generic-project"
    assert context["target_branch"] == "main"
    assert context["baseline_commit"] == "a" * 40
    assert context["approved_sprint_path"] == "docs/sprints/SPRINT_003.md"
    assert context["binding_documents"]["constitution_path"].endswith(
        "BRIDGE_CONSTITUTION.md"
    )
    assert context["release_gates"][0]["command"] == "python -m pytest"
    assert context["evidence_root"] == "docs/evidence/sprint-003"
    assert context["allowed_terminal_states"] == [
        "PASS â€” READY FOR PRODUCT OWNER REVIEW"
    ]


@pytest.mark.django_db
def test_execution_context_never_guesses_a_project(tmp_path: Path) -> None:
    response = invoke_operation(
        "generate_execution_context",
        {"approved_sprint_path": "docs/sprints/SPRINT_003.md"},
        tmp_path,
    )

    assert response["status"] == "USER_INPUT_REQUIRED"

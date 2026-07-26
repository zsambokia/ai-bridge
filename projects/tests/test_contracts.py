"""Acceptance tests for canonical execution-contract generation and MCP flow."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.contracts import (
    _normalized_hash,
    generate_execution_contract,
    issue_execution_contract,
    render_execution_handoff,
    validate_execution_contract,
)
from projects.mcp import invoke_operation, registered_operations
from projects.models import ExecutionContract, Project
from projects.services import bootstrap_project
from projects.tests.test_services import write_definition


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
    monkeypatch.setattr(
        "projects.contracts._baseline_exists", lambda root, baseline: True
    )
    assert bootstrap_project(definition, "docs/sprints/SPRINT_003.md", tmp_path).success
    return tmp_path, Project.objects.get(project_id="generic-project")


def _draft(root: Path, project: Project) -> ExecutionContract:
    return generate_execution_contract(
        project,
        "docs/sprints/SPRINT_003.md",
        "BUGFIX",
        "Prove governed contract issuance.",
        root,
    )


@pytest.mark.django_db
def test_contract_is_reproducible_then_issued_immutably(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    draft = _draft(root, project)
    assert draft.contract_hash == _normalized_hash(draft.payload)

    validated = validate_execution_contract(draft, root)
    issued = issue_execution_contract(validated)
    assert issued.lifecycle == ExecutionContract.Lifecycle.ISSUED
    assert issued.contract_hash == _normalized_hash(issued.payload)

    issued.payload = {"tampered": True}
    with pytest.raises(ValueError, match="IMMUTABLE"):
        issued.save()


@pytest.mark.django_db
def test_contract_rejects_missing_or_unapproved_sprint(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    with pytest.raises(ValueError, match="SPRINT_NOT_FOUND"):
        generate_execution_contract(
            project, "docs/sprints/missing.md", "BUGFIX", "x", root
        )

    sprint = root / "docs/sprints/unapproved.md"
    sprint.write_text("# Draft\n", encoding="utf-8")
    with pytest.raises(ValueError, match="SPRINT_NOT_APPROVED"):
        generate_execution_contract(
            project, "docs/sprints/unapproved.md", "BUGFIX", "x", root
        )


@pytest.mark.django_db
def test_contract_rejects_missing_binding_and_project_sprint_mismatch(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    (root / "docs/constitution/BRIDGE_CONSTITUTION.md").unlink()
    with pytest.raises(ValueError, match="BINDING_DOCUMENT_MISSING"):
        _draft(root, project)

    write_definition(root)
    sprint = root / "docs/sprints/SPRINT_003.md"
    sprint.write_text(
        "**Status:** APPROVED FOR CODEX EXECUTION\n**Project:** Other\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="PROJECT_SPRINT_MISMATCH"):
        _draft(root, project)


@pytest.mark.django_db
def test_evidence_collision_unique_identifiers_and_stored_render(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    first = issue_execution_contract(
        validate_execution_contract(_draft(root, project), root)
    )
    second = validate_execution_contract(_draft(root, project), root)
    assert first.handoff_identifier != second.handoff_identifier
    with pytest.raises(ValueError, match="EVIDENCE_PATH_COLLISION"):
        issue_execution_contract(second)
    rendered = render_execution_handoff(first)
    assert first.handoff_identifier in rendered
    assert first.contract_hash in rendered
    assert first.payload["execution"]["baseline_commit"] in rendered


@pytest.mark.django_db
def test_complete_mcp_contract_flow_uses_registered_surface(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    assert {
        "generate_execution_contract",
        "validate_execution_contract",
        "issue_execution_contract",
        "get_execution_contract",
        "render_execution_handoff",
    }.issubset(registered_operations())
    generated = invoke_operation(
        "generate_execution_contract",
        {
            "project_id": project.project_id,
            "approved_sprint_path": "docs/sprints/SPRINT_003.md",
            "task_type": "BUGFIX",
            "intent": "MCP flow.",
        },
        root,
    )
    identifier = generated["execution_contract"]["handoff_identifier"]
    assert generated["status"] == "EXECUTION_CONTRACT_GENERATED"
    assert (
        invoke_operation(
            "validate_execution_contract", {"handoff_identifier": identifier}, root
        )["status"]
        == "EXECUTION_CONTRACT_VALIDATED"
    )
    assert (
        invoke_operation(
            "issue_execution_contract", {"handoff_identifier": identifier}, root
        )["status"]
        == "EXECUTION_CONTRACT_ISSUED"
    )
    retrieved = invoke_operation(
        "get_execution_contract", {"handoff_identifier": identifier}, root
    )
    rendered = invoke_operation(
        "render_execution_handoff", {"handoff_identifier": identifier}, root
    )
    assert (
        retrieved["execution_contract"]["contract_hash"] in rendered["rendered_handoff"]
    )

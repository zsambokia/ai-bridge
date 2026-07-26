"""Acceptance tests for canonical execution-contract generation and MCP flow."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.contract_policy import resolve_policy
from projects.contracts import (
    _normalized_hash,
    complete_execution_contract,
    consume_execution_contract,
    generate_execution_contract,
    issue_execution_contract,
    render_execution_handoff,
    validate_execution_contract,
    validate_issued_execution_contract,
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
def test_contract_rejects_repository_mismatch_and_missing_baseline(
    contract_project: tuple[Path, Project], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, project = contract_project
    monkeypatch.setattr(
        "projects.contracts._repository_identity", lambda root: "other/repository"
    )
    with pytest.raises(ValueError, match="REPOSITORY_IDENTITY_MISMATCH"):
        _draft(root, project)

    monkeypatch.setattr(
        "projects.contracts._repository_identity",
        lambda root: "example/generic-project",
    )
    monkeypatch.setattr(
        "projects.contracts._baseline_exists", lambda root, baseline: False
    )
    with pytest.raises(ValueError, match="BASELINE_COMMIT_NOT_FOUND"):
        _draft(root, project)


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


@pytest.mark.django_db
def test_policy_profiles_are_deterministic_and_distinct(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    bugfix = generate_execution_contract(
        project,
        "docs/sprints/SPRINT_003.md",
        "CONFIGURATION",
        "Host repair.",
        root,
        execution_level="BUGFIX",
    )
    sprint = generate_execution_contract(
        project,
        "docs/sprints/SPRINT_003.md",
        "FEATURE",
        "Feature.",
        root,
        execution_level="SPRINT",
    )
    epic = generate_execution_contract(
        project,
        "docs/sprints/SPRINT_003.md",
        "SELF_DEVELOPMENT",
        "Epic plan.",
        root,
        execution_level="EPIC",
        child_contract_identifiers=["child-sprint-006"],
    )
    assert bugfix.payload["policy"]["required_assessment_depth"] == "standard"
    assert sprint.payload["policy"]["required_assessment_depth"] == "extended"
    assert epic.payload["policy"]["child_contract_required"] is True
    assert resolve_policy("BUGFIX", "CONFIGURATION") == resolve_policy(
        "BUGFIX", "CONFIGURATION"
    )


@pytest.mark.django_db
def test_risk_only_strengthens_and_epic_cannot_be_consumed(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    ordinary = resolve_policy("BUGFIX", "CONFIGURATION")
    risk = resolve_policy("BUGFIX", "CONFIGURATION", ["SECURITY_RELEVANT"])
    assert set(ordinary["required_evidence_artifacts"]).issubset(
        risk["required_evidence_artifacts"]
    )
    epic = generate_execution_contract(
        project,
        "docs/sprints/SPRINT_003.md",
        "SELF_DEVELOPMENT",
        "Epic plan.",
        root,
        execution_level="EPIC",
        child_contract_identifiers=["child-sprint-006"],
    )
    epic = issue_execution_contract(validate_execution_contract(epic, root))
    with pytest.raises(ValueError, match="EPIC_CHILD_CONTRACT_REQUIRED"):
        consume_execution_contract(epic, root)


@pytest.mark.django_db
def test_contract_completion_binds_final_commit(
    contract_project: tuple[Path, Project],
) -> None:
    root, project = contract_project
    contract = generate_execution_contract(
        project,
        "docs/sprints/SPRINT_003.md",
        "BUGFIX",
        "Fix.",
        root,
        execution_level="BUGFIX",
    )
    contract = issue_execution_contract(validate_execution_contract(contract, root))
    contract = consume_execution_contract(contract, root)
    completed = complete_execution_contract(
        contract, "b" * 40, "PASS â€” READY FOR PRODUCT OWNER REVIEW"
    )
    assert completed.final_commit_sha == "b" * 40
    assert completed.lifecycle == ExecutionContract.Lifecycle.COMPLETED


@pytest.mark.django_db
def test_issued_repository_contract_survives_its_own_publication_commit(
    contract_project: tuple[Path, Project], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, project = contract_project
    validated = validate_execution_contract(_draft(root, project), root)
    contract = issue_execution_contract(validated)
    assert contract.payload["execution"]["baseline_rule"] == "DESCENDANT_OF"

    # The publication commit is a descendant of the validated baseline.  This
    # is the exact case that made an EXACT contract unconsumable on publication.
    monkeypatch.setattr("projects.contracts._head_sha", lambda root: "b" * 40)
    monkeypatch.setattr(
        "projects.contracts._is_descendant_of", lambda root, ancestor, head: True
    )
    validate_issued_execution_contract(contract, root)

    contract.payload["execution"]["baseline_rule"] = "EXACT"
    contract.contract_hash = _normalized_hash(contract.payload)
    with pytest.raises(ValueError, match="BASELINE_EXACT_MISMATCH"):
        validate_issued_execution_contract(contract, root)

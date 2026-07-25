"""Acceptance scenarios for Project Registry and Context bootstrap."""

from __future__ import annotations

from pathlib import Path

import pytest

from projects.models import Project, ProjectContext
from projects.services import (
    bootstrap_project,
    create_project_context,
    load_project_definition,
    refresh_context_status,
)


def write_definition(root: Path, extra_project: str = "") -> Path:
    """Create a complete generic static definition and its source documents."""
    for relative in (
        "AGENTS.md",
        "docs/constitution/BRIDGE_CONSTITUTION.md",
        "docs/workflows/EVIDENCE_DRIVEN_SPRINT.md",
        "docs/contracts/HANDOFF_EXECUTION_CONTRACT.md",
        "docs/roadmap/ROADMAP.md",
        "docs/akb/CURRENT_STATE.md",
        "docs/sprints/SPRINT_003.md",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Status: APPROVED FOR CODEX EXECUTION\n", encoding="utf-8")
    definition = root / ".bridge/project.yaml"
    definition.parent.mkdir(parents=True, exist_ok=True)
    definition.write_text(
        """project:
  id: generic-project
  name: Generic Project
  project_type: platform
{extra_project}repository:
  full_name: example/generic-project
  default_branch: main
  integration_branch: main
paths:
  agents: AGENTS.md
  constitution: docs/constitution/BRIDGE_CONSTITUTION.md
  execution_workflow: docs/workflows/EVIDENCE_DRIVEN_SPRINT.md
  handoff_contract: docs/contracts/HANDOFF_EXECUTION_CONTRACT.md
  roadmap: docs/roadmap/ROADMAP.md
  primary_current_state: docs/akb/CURRENT_STATE.md
release_gates:
  repository_wide:
    - id: tests
      command: python -m pytest
        """.format(extra_project=extra_project),
        encoding="utf-8",
    )
    return definition


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    definition = write_definition(tmp_path)
    monkeypatch.setattr(
        "projects.services._repository_identity", lambda root: "example/generic-project"
    )
    monkeypatch.setattr("projects.services._current_branch", lambda root: "main")
    monkeypatch.setattr("projects.services._head_sha", lambda root: "a" * 40)
    return tmp_path, definition


@pytest.mark.django_db
def test_valid_definition_loads_and_bootstrap_creates_ready_valid_context(
    project_root: tuple[Path, Path],
) -> None:
    root, definition_path = project_root
    definition = load_project_definition(definition_path, root)
    assert definition.project_id == "generic-project"

    result = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)

    assert result.success is True
    assert result.onboarding_status == Project.OnboardingStatus.READY
    project = Project.objects.get(project_id="generic-project")
    context = project.contexts.get()
    assert context.validation_status == ProjectContext.ValidationStatus.VALID
    assert context.constitution_path.endswith("BRIDGE_CONSTITUTION.md")
    assert context.release_gate_configuration[0]["command"] == "python -m pytest"


@pytest.mark.django_db
def test_repeated_bootstrap_is_idempotent(project_root: tuple[Path, Path]) -> None:
    root, definition_path = project_root
    first = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)
    second = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)

    assert first.success and second.success
    assert Project.objects.count() == 1
    assert ProjectContext.objects.count() == 1
    assert second.context_created is False


@pytest.mark.django_db
def test_invalid_definition_is_rejected(project_root: tuple[Path, Path]) -> None:
    root, _ = project_root
    invalid = write_definition(root, "  onboarding_status: ready\n")

    result = bootstrap_project(invalid, "docs/sprints/SPRINT_003.md", root)

    assert result.success is False
    assert "runtime state" in result.errors[0]
    assert Project.objects.count() == 0


@pytest.mark.django_db
def test_missing_governance_document_marks_onboarding_invalid(
    project_root: tuple[Path, Path],
) -> None:
    root, definition_path = project_root
    (root / "docs/roadmap/ROADMAP.md").unlink()

    result = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)

    assert result.success is False
    project = Project.objects.get(project_id="generic-project")
    assert project.onboarding_status == Project.OnboardingStatus.INVALID
    assert "governance document" in result.errors[0]


@pytest.mark.django_db
def test_duplicate_repository_identity_is_rejected(
    project_root: tuple[Path, Path],
) -> None:
    root, definition_path = project_root
    Project.objects.create(
        project_id="other-project",
        display_name="Other",
        repository_full_name="example/generic-project",
        definition_path=".bridge/other.yaml",
    )

    result = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)

    assert result.success is False
    assert "already registered" in result.errors[0]
    assert Project.objects.count() == 1


@pytest.mark.django_db
def test_not_ready_project_cannot_create_context(
    project_root: tuple[Path, Path],
) -> None:
    root, definition_path = project_root
    definition = load_project_definition(definition_path, root)
    project = Project.objects.create(
        project_id=definition.project_id,
        display_name=definition.display_name,
        repository_full_name=definition.repository_full_name,
        definition_path=definition.definition_path,
        onboarding_status=Project.OnboardingStatus.PENDING,
    )

    with pytest.raises(ValueError, match="READY"):
        create_project_context(project, definition, "docs/sprints/SPRINT_003.md", root)


@pytest.mark.django_db
def test_invalid_source_creates_invalid_context(
    project_root: tuple[Path, Path],
) -> None:
    root, definition_path = project_root
    definition = load_project_definition(definition_path, root)
    project = Project.objects.create(
        project_id=definition.project_id,
        display_name=definition.display_name,
        repository_full_name=definition.repository_full_name,
        definition_path=definition.definition_path,
        onboarding_status=Project.OnboardingStatus.READY,
    )

    context = create_project_context(
        project, definition, "docs/sprints/missing.md", root
    )

    assert context.validation_status == ProjectContext.ValidationStatus.INVALID
    assert "unavailable" in context.validation_reason


@pytest.mark.django_db
def test_differing_commit_makes_context_stale(project_root: tuple[Path, Path]) -> None:
    root, definition_path = project_root
    result = bootstrap_project(definition_path, "docs/sprints/SPRINT_003.md", root)
    assert result.success
    context = ProjectContext.objects.get()

    refresh_context_status(context, "b" * 40)

    context.refresh_from_db()
    assert context.validation_status == ProjectContext.ValidationStatus.STALE

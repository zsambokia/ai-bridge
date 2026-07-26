"""Canonical execution-context construction from Project runtime records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from uuid import uuid4

from .models import ExecutableScope, Project, ProjectContext
from .scopes import approved_scope
from .services import load_project_definition


@dataclass(frozen=True)
class ExecutionContext:
    """Repository-bound inputs shared by every execution representation."""

    execution_id: str
    project_id: str
    target_repository: str
    target_branch: str
    baseline_commit: str
    baseline_rule: str
    approved_sprint_path: str
    binding_documents: dict[str, str]
    release_gates: list[dict[str, object]]
    evidence_root: str
    allowed_terminal_states: list[str]

    def as_dict(self) -> dict[str, object]:
        """Return the MCP and Codex-package representation of this context."""
        return asdict(self)


def _sprint_slug(sprint_path: str) -> str:
    return Path(sprint_path).stem.lower().replace("_", "-")


def build_execution_context(
    project: Project, approved_sprint_path: str, repository_root: Path
) -> ExecutionContext:
    """Build one context without guessing Project, Sprint, or repository inputs."""
    if project.lifecycle != Project.Lifecycle.ACTIVE:
        raise ValueError("PROJECT_NOT_ACTIVE")
    if project.onboarding_status != Project.OnboardingStatus.READY:
        raise ValueError("PROJECT_NOT_READY")
    context = project.contexts.filter(
        validation_status=ProjectContext.ValidationStatus.VALID
    ).first()
    if context is None:
        raise ValueError("PROJECT_CONTEXT_NOT_VALID")

    definition = load_project_definition(
        repository_root / project.definition_path, repository_root
    )
    if (
        definition.project_id != project.project_id
        or definition.repository_full_name != project.repository_full_name
        or context.repository_full_name != project.repository_full_name
    ):
        raise ValueError("PROJECT_REGISTRY_DEFINITION_CONFLICT")
    try:
        scope = ExecutableScope.objects.get(
            project=project, published_path=approved_sprint_path
        )
    except ExecutableScope.DoesNotExist as exc:
        raise ValueError("SCOPE_NOT_CANONICAL") from exc
    approved_scope(scope)

    evidence_root = definition.evidence_path_template.format(
        sprint_slug=_sprint_slug(approved_sprint_path)
    )
    return ExecutionContext(
        execution_id=f"bridge:{project.project_id}:{_sprint_slug(approved_sprint_path)}:{uuid4()}",
        project_id=project.project_id,
        target_repository=project.repository_full_name,
        target_branch=definition.integration_branch,
        baseline_commit=context.source_commit_sha,
        baseline_rule="EXACT",
        approved_sprint_path=approved_sprint_path,
        binding_documents={
            "agents_path": definition.paths["agents"],
            "constitution_path": context.constitution_path,
            "workflow_path": definition.paths["execution_workflow"],
            "handoff_contract_path": definition.paths["handoff_contract"],
            "roadmap_path": context.roadmap_path,
            "akb_current_state_path": context.current_state_path,
        },
        release_gates=definition.release_gates,
        evidence_root=evidence_root,
        allowed_terminal_states=definition.allowed_terminal_states,
    )

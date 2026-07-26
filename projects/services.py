"""Generic bootstrap, definition validation, and Context services."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml
from django.db import IntegrityError, transaction

from .models import Project, ProjectContext

FORBIDDEN_RUNTIME_KEYS = {"status", "onboarding_status", "capabilities"}


@dataclass(frozen=True)
class ProjectDefinition:
    """Validated static inputs needed by the canonical Project domain."""

    project_id: str
    display_name: str
    repository_full_name: str
    default_branch: str
    integration_branch: str
    definition_path: str
    paths: dict[str, str]
    release_gates: list[dict[str, Any]]
    evidence_path_template: str
    allowed_terminal_states: list[str]


@dataclass
class BootstrapResult:
    """Structured, machine-readable outcome of the bootstrap operation."""

    success: bool
    project_id: str | None = None
    onboarding_status: str = Project.OnboardingStatus.INVALID
    registry_created: bool = False
    context_created: bool = False
    context_status: str | None = None
    errors: list[str] = field(default_factory=list)

    def as_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


def _mapping(value: Any, name: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{name} must be a mapping")
    return {}


def _string(mapping: dict[str, Any], name: str, errors: list[str]) -> str:
    value = mapping.get(name)
    if isinstance(value, str) and value.strip():
        return value
    errors.append(f"{name} must be a non-empty string")
    return ""


def load_project_definition(path: Path, repository_root: Path) -> ProjectDefinition:
    """Load and structurally validate one static Project Definition."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Project Definition cannot be read: {exc}") from exc

    errors: list[str] = []
    root = _mapping(raw, "Project Definition", errors)
    project = _mapping(root.get("project"), "project", errors)
    repository = _mapping(root.get("repository"), "repository", errors)
    paths = _mapping(root.get("paths"), "paths", errors)
    release_gates = _mapping(root.get("release_gates"), "release_gates", errors)
    evidence = _mapping(root.get("evidence"), "evidence", errors)
    execution = _mapping(root.get("execution"), "execution", errors)

    forbidden = FORBIDDEN_RUNTIME_KEYS.intersection(project)
    forbidden.update(FORBIDDEN_RUNTIME_KEYS.intersection(root))
    if forbidden:
        errors.append(
            "static Project Definition contains runtime state: "
            + ", ".join(sorted(forbidden))
        )

    project_id = _string(project, "id", errors)
    display_name = _string(project, "name", errors)
    repository_full_name = _string(repository, "full_name", errors)
    default_branch = _string(repository, "default_branch", errors)
    integration_branch = _string(repository, "integration_branch", errors)
    for required_path in (
        "agents",
        "constitution",
        "execution_workflow",
        "handoff_contract",
        "roadmap",
        "primary_current_state",
    ):
        _string(paths, required_path, errors)
    commands = release_gates.get("repository_wide")
    if not isinstance(commands, list) or not commands:
        errors.append("release_gates.repository_wide must be a non-empty list")
        commands = []
    for index, command in enumerate(commands):
        if not isinstance(command, dict) or not isinstance(command.get("command"), str):
            errors.append(f"release_gates.repository_wide[{index}] needs a command")
    evidence_path_template = _string(evidence, "path_template", errors)
    allowed_terminal_states = execution.get("allowed_terminal_states")
    if (
        not isinstance(allowed_terminal_states, list)
        or not allowed_terminal_states
        or not all(
            isinstance(state, str) and state.strip()
            for state in allowed_terminal_states
        )
    ):
        errors.append("execution.allowed_terminal_states must be a non-empty list")
        allowed_terminal_states = []

    if errors:
        raise ValueError("; ".join(errors))
    relative_path = path.resolve().relative_to(repository_root.resolve()).as_posix()
    return ProjectDefinition(
        project_id=project_id,
        display_name=display_name,
        repository_full_name=repository_full_name,
        default_branch=default_branch,
        integration_branch=integration_branch,
        definition_path=relative_path,
        paths={key: str(value) for key, value in paths.items()},
        release_gates=[dict(item) for item in commands],
        evidence_path_template=evidence_path_template,
        allowed_terminal_states=list(allowed_terminal_states),
    )


def _command_resolvable(command: str) -> bool:
    tokens = shlex.split(command, posix=False)
    if not tokens:
        return False
    executable = tokens[0]
    if executable in {"python", "python3", sys.executable}:
        return True
    if shutil.which(executable):
        return True
    suffix = ".exe" if sys.platform == "win32" else ""
    return (Path(sys.executable).parent / f"{executable}{suffix}").exists()


def _repository_identity(repository_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    remote = result.stdout.strip().removesuffix(".git")
    if remote.startswith("git@") and ":" in remote:
        return remote.split(":", maxsplit=1)[1]
    if "://" in remote:
        return remote.split("://", maxsplit=1)[1].split("/", maxsplit=1)[1]
    return remote or None


def assess_onboarding(
    definition: ProjectDefinition, repository_root: Path
) -> list[str]:
    """Return every observable readiness failure for a Project Definition."""
    errors: list[str] = []
    if _repository_identity(repository_root) != definition.repository_full_name:
        errors.append("repository identity is missing, ambiguous, or does not match")
    for label, configured_path in definition.paths.items():
        if label.endswith("_root"):
            continue
        if not (repository_root / configured_path).is_file():
            errors.append(
                f"required governance document is unavailable: {configured_path}"
            )
    for gate in definition.release_gates:
        command = str(gate["command"])
        if not _command_resolvable(command):
            errors.append(f"Release Gate command is not resolvable: {command}")
    return errors


def _head_sha(repository_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError("current repository commit cannot be resolved")
    return result.stdout.strip()


def _current_branch(repository_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def create_project_context(
    project: Project,
    definition: ProjectDefinition,
    sprint_path: str,
    repository_root: Path,
) -> ProjectContext:
    """Create the first Context from one READY canonical Registry record."""
    if project.onboarding_status != Project.OnboardingStatus.READY:
        raise ValueError("Project Context requires onboarding status READY")
    source_paths = {
        "constitution_path": definition.paths["constitution"],
        "roadmap_path": definition.paths["roadmap"],
        "current_state_path": definition.paths["primary_current_state"],
        "sprint_path": sprint_path,
    }
    unavailable = [
        path for path in source_paths.values() if not (repository_root / path).is_file()
    ]
    status = ProjectContext.ValidationStatus.VALID
    reason = ""
    if unavailable:
        status = ProjectContext.ValidationStatus.INVALID
        reason = "required Context source is unavailable: " + ", ".join(unavailable)
    return ProjectContext.objects.create(
        project=project,
        repository_full_name=definition.repository_full_name,
        release_gate_configuration=definition.release_gates,
        validation_status=status,
        validation_reason=reason,
        source_commit_sha=_head_sha(repository_root),
        **source_paths,
    )


def refresh_context_status(
    context: ProjectContext, current_commit: str
) -> ProjectContext:
    """Mark a valid Context stale when its deterministic source commit changes."""
    if (
        context.validation_status == ProjectContext.ValidationStatus.VALID
        and context.source_commit_sha != current_commit
    ):
        context.validation_status = ProjectContext.ValidationStatus.STALE
        context.validation_reason = (
            "current repository commit differs from Context source commit"
        )
        context.save(update_fields=["validation_status", "validation_reason"])
    return context


def bootstrap_project(
    definition_path: Path,
    sprint_path: str,
    repository_root: Path,
    contract_mode: str = "BOOTSTRAP",
) -> BootstrapResult:
    """Idempotently register a Project and create its first valid Context."""
    if contract_mode != "BOOTSTRAP":
        return BootstrapResult(
            success=False, errors=["first Context requires BOOTSTRAP mode"]
        )
    try:
        definition = load_project_definition(definition_path, repository_root)
    except ValueError as exc:
        return BootstrapResult(success=False, errors=[str(exc)])

    readiness_errors = assess_onboarding(definition, repository_root)
    if _current_branch(repository_root) not in {
        definition.default_branch,
        definition.integration_branch,
    }:
        readiness_errors.append(
            "execution branch is missing or is not a configured branch"
        )
    sprint_document = repository_root / sprint_path
    if (
        not sprint_document.is_file()
        or "Status: APPROVED FOR CODEX EXECUTION"
        not in sprint_document.read_text(encoding="utf-8")
    ):
        readiness_errors.append("approved Sprint specification is unavailable")
    existing_by_repository = Project.objects.filter(
        repository_full_name=definition.repository_full_name
    ).exclude(project_id=definition.project_id)
    if existing_by_repository.exists():
        return BootstrapResult(
            success=False,
            project_id=definition.project_id,
            errors=["repository identity is already registered by another Project"],
        )

    try:
        with transaction.atomic():
            project, created = Project.objects.update_or_create(
                project_id=definition.project_id,
                defaults={
                    "display_name": definition.display_name,
                    "repository_full_name": definition.repository_full_name,
                    "definition_path": definition.definition_path,
                    "lifecycle": Project.Lifecycle.ACTIVE,
                    "onboarding_status": (
                        Project.OnboardingStatus.INVALID
                        if readiness_errors
                        else Project.OnboardingStatus.READY
                    ),
                    "onboarding_reason": "; ".join(readiness_errors),
                },
            )
    except IntegrityError:
        return BootstrapResult(
            success=False,
            project_id=definition.project_id,
            errors=["conflicting Project Registry identity"],
        )

    if readiness_errors:
        return BootstrapResult(
            success=False,
            project_id=project.project_id,
            onboarding_status=project.onboarding_status,
            registry_created=created,
            errors=readiness_errors,
        )
    existing_context = project.contexts.filter(
        validation_status=ProjectContext.ValidationStatus.VALID
    ).first()
    if existing_context:
        refresh_context_status(existing_context, _head_sha(repository_root))
        if existing_context.validation_status == ProjectContext.ValidationStatus.VALID:
            return BootstrapResult(
                success=True,
                project_id=project.project_id,
                onboarding_status=project.onboarding_status,
                registry_created=created,
                context_status=existing_context.validation_status,
            )
    context = create_project_context(project, definition, sprint_path, repository_root)
    return BootstrapResult(
        success=context.validation_status == ProjectContext.ValidationStatus.VALID,
        project_id=project.project_id,
        onboarding_status=project.onboarding_status,
        registry_created=created,
        context_created=True,
        context_status=context.validation_status,
        errors=[context.validation_reason] if context.validation_reason else [],
    )

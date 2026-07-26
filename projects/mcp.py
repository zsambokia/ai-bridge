"""Small, registered MCP-facing operations for the canonical Project domain."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from django.utils import timezone

from .execution_context import build_execution_context
from .models import Project, ProjectResolutionContinuation

McpHandler = Callable[[dict[str, Any], Path], dict[str, Any]]
_OPERATIONS: dict[str, McpHandler] = {}


def mcp_operation(name: str) -> Callable[[McpHandler], McpHandler]:
    """Register an operation on the one lightweight MCP adapter."""

    def register(handler: McpHandler) -> McpHandler:
        _OPERATIONS[name] = handler
        return handler

    return register


def registered_operations() -> tuple[str, ...]:
    """Expose the registered operations for transport discovery and tests."""
    return tuple(sorted(_OPERATIONS))


def invoke_operation(
    operation: str, payload: dict[str, Any], repository_root: Path
) -> dict[str, Any]:
    """Invoke a registered operation; arbitrary names are never inferred."""
    handler = _OPERATIONS.get(operation)
    if handler is None:
        return {
            "status": "INVALID_OPERATION",
            "error": "MCP operation is not registered",
        }
    return handler(payload, repository_root)


def _project_view(project: Project) -> dict[str, str]:
    return {
        "project_id": project.project_id,
        "display_name": project.display_name,
        "repository_full_name": project.repository_full_name,
    }


@mcp_operation("resolve_project")
def resolve_project(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    """Resolve exactly one active, ready Project or request an explicit choice."""
    del repository_root
    query = str(payload.get("query", "")).strip()
    if not query:
        return {"status": "USER_INPUT_REQUIRED", "prompt": "Provide a project query."}
    available = Project.objects.filter(
        lifecycle=Project.Lifecycle.ACTIVE,
        onboarding_status=Project.OnboardingStatus.READY,
    )
    candidates = list(
        available.filter(project_id__icontains=query)
        | available.filter(display_name__icontains=query)
        | available.filter(repository_full_name__icontains=query)
    )
    # A union is deliberately deduplicated at the application boundary.
    candidates = list(
        {candidate.project_id: candidate for candidate in candidates}.values()
    )
    if not candidates:
        return {
            "status": "PROJECT_NOT_FOUND",
            "error": "No registered Project matches.",
        }
    if len(candidates) == 1:
        return {"status": "PROJECT_RESOLVED", "project": _project_view(candidates[0])}
    continuation = ProjectResolutionContinuation.objects.create(
        candidate_project_ids=[candidate.project_id for candidate in candidates]
    )
    return {
        "status": "USER_INPUT_REQUIRED",
        "prompt": "Select one project_id from the supplied candidates.",
        "continuation_token": str(continuation.token),
        "candidates": [_project_view(candidate) for candidate in candidates],
    }


@mcp_operation("continue_project_resolution")
def continue_project_resolution(
    payload: dict[str, Any], repository_root: Path
) -> dict[str, Any]:
    """Resume one durable resolution and consume it only after a valid choice."""
    del repository_root
    token = payload.get("continuation_token")
    selected_project_id = str(payload.get("selected_project_id", "")).strip()
    if not isinstance(token, str):
        return {
            "status": "INVALID_CONTINUATION",
            "error": "Continuation token is unknown.",
        }
    try:
        continuation = ProjectResolutionContinuation.objects.get(token=token)
    except (ProjectResolutionContinuation.DoesNotExist, ValueError, TypeError):
        return {
            "status": "INVALID_CONTINUATION",
            "error": "Continuation token is unknown.",
        }
    if continuation.consumed_at is not None:
        return {
            "status": "CONTINUATION_CONSUMED",
            "error": "Continuation token was already used.",
        }
    if selected_project_id not in continuation.candidate_project_ids:
        return {
            "status": "INVALID_SELECTION",
            "error": "Selected project is not a candidate.",
        }
    try:
        project = Project.objects.get(
            project_id=selected_project_id,
            lifecycle=Project.Lifecycle.ACTIVE,
            onboarding_status=Project.OnboardingStatus.READY,
        )
    except Project.DoesNotExist:
        return {
            "status": "INVALID_SELECTION",
            "error": "Selected project is not available.",
        }
    continuation.selected_project_id = project.project_id
    continuation.consumed_at = timezone.now()
    continuation.save(update_fields=["selected_project_id", "consumed_at"])
    return {"status": "PROJECT_RESOLVED", "project": _project_view(project)}


@mcp_operation("generate_execution_context")
def generate_execution_context(
    payload: dict[str, Any], repository_root: Path
) -> dict[str, Any]:
    """Generate the repository-bound package after an explicit Project selection."""
    project_id = str(payload.get("project_id", "")).strip()
    sprint_path = str(payload.get("approved_sprint_path", "")).strip()
    if not project_id or not sprint_path:
        return {
            "status": "USER_INPUT_REQUIRED",
            "prompt": "Provide project_id and approved_sprint_path.",
        }
    try:
        project = Project.objects.get(project_id=project_id)
        context = build_execution_context(project, sprint_path, repository_root)
    except Project.DoesNotExist:
        return {"status": "PROJECT_NOT_FOUND", "error": "Project is not registered."}
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Context cannot be generated."}
    package = context.as_dict()
    return {
        "status": "EXECUTION_CONTEXT_GENERATED",
        "execution_context": package,
        # This is intentionally the same canonical object, not a second
        # handoff format. The explicit alias is the representation consumed
        # by Codex today; other renderings can be derived later.
        "codex_execution_package": package,
    }

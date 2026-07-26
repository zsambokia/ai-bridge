"""Small, registered MCP-facing operations for the canonical Project domain."""
# ruff: noqa: E501

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.utils import timezone

from .contracts import (
    complete_execution_contract,
    consume_execution_contract,
    generate_scope_execution_contract,
    issue_execution_contract,
    render_execution_handoff,
    revoke_execution_contract,
    supersede_execution_contract,
    validate_execution_contract,
)
from .execution_context import build_execution_context
from .models import (
    ExecutableScope,
    ExecutionContract,
    Project,
    ProjectResolutionContinuation,
)
from .scopes import (
    answer_clarifications,
    bind_approval,
    classify_request,
    close_scope,
    propose_scope,
    publish_scope,
    render_scope,
    review_scope,
    validate_scope_record,
)

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
        candidate_project_ids=[candidate.project_id for candidate in candidates],
        expires_at=timezone.now() + timedelta(minutes=30),
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
    if (
        continuation.expires_at is not None
        and continuation.expires_at <= timezone.now()
    ):
        return {
            "status": "CONTINUATION_EXPIRED",
            "error": "Continuation token expired; resolve the project again.",
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


def _contract_view(contract: ExecutionContract) -> dict[str, Any]:
    return {
        "handoff_identifier": contract.handoff_identifier,
        "lifecycle": contract.lifecycle,
        "contract_hash": contract.contract_hash,
        "payload": contract.payload,
    }


@mcp_operation("validate_execution_contract")
def validate_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    """Validate a generated draft before its immutable issuance."""
    identifier = str(payload.get("handoff_identifier", "")).strip()
    try:
        contract = ExecutionContract.objects.get(handoff_identifier=identifier)
        contract = validate_execution_contract(contract, repository_root)
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Contract cannot be validated."}
    return {
        "status": "EXECUTION_CONTRACT_VALIDATED",
        "execution_contract": _contract_view(contract),
    }


@mcp_operation("issue_execution_contract")
def issue_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    """Issue a validated contract; no request input can alter its payload."""
    identifier = str(payload.get("handoff_identifier", "")).strip()
    try:
        contract = issue_execution_contract(
            ExecutionContract.objects.get(handoff_identifier=identifier),
            repository_root,
        )
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Contract cannot be issued."}
    return {
        "status": "EXECUTION_CONTRACT_ISSUED",
        "execution_contract": _contract_view(contract),
    }


@mcp_operation("get_execution_contract")
def get_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    """Retrieve the durable machine-readable contract by its identifier."""
    del repository_root
    identifier = str(payload.get("handoff_identifier", "")).strip()
    try:
        contract = ExecutionContract.objects.get(handoff_identifier=identifier)
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    return {
        "status": "EXECUTION_CONTRACT_RETRIEVED",
        "execution_contract": _contract_view(contract),
    }


@mcp_operation("render_execution_handoff")
def render_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    """Render the stored payload without a second handoff representation."""
    del repository_root
    identifier = str(payload.get("handoff_identifier", "")).strip()
    try:
        contract = ExecutionContract.objects.get(handoff_identifier=identifier)
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    return {
        "status": "EXECUTION_HANDOFF_RENDERED",
        "handoff_identifier": contract.handoff_identifier,
        "rendered_handoff": render_execution_handoff(contract),
    }


def _find_contract(payload: dict[str, Any]) -> ExecutionContract:
    return ExecutionContract.objects.get(
        handoff_identifier=str(payload.get("handoff_identifier", "")).strip()
    )


@mcp_operation("consume_execution_contract")
def consume_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    try:
        contract = consume_execution_contract(
            _find_contract(payload),
            repository_root,
            expected_hash=str(payload.get("expected_contract_hash", "")),
            provider_identity=str(payload.get("provider_identity", "")),
            observed_baseline=str(payload.get("observed_baseline", "")),
            schema_version=str(payload.get("schema_version", "")),
            idempotency_key=str(payload.get("idempotency_key", "")),
        )
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Contract cannot be consumed."}
    return {
        "status": "EXECUTION_CONTRACT_CONSUMED",
        "execution_contract": _contract_view(contract),
    }


@mcp_operation("complete_execution_contract")
def complete_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        contract = complete_execution_contract(
            _find_contract(payload),
            str(payload.get("final_commit_sha", "")),
            str(payload.get("closure_state", "")),
            payload.get("completion_data"),
        )
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Contract cannot be completed."}
    return {
        "status": "EXECUTION_CONTRACT_COMPLETED",
        "execution_contract": _contract_view(contract),
    }


@mcp_operation("supersede_execution_contract")
def supersede_contract(
    payload: dict[str, Any], repository_root: Path
) -> dict[str, Any]:
    del repository_root
    try:
        contract = supersede_execution_contract(
            _find_contract(payload),
            ExecutionContract.objects.get(
                handoff_identifier=str(
                    payload.get("replacement_handoff_identifier", "")
                ).strip()
            ),
        )
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Contract cannot be superseded."}
    return {
        "status": "EXECUTION_CONTRACT_SUPERSEDED",
        "execution_contract": _contract_view(contract),
    }


@mcp_operation("revoke_execution_contract")
def revoke_contract(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        contract = revoke_execution_contract(_find_contract(payload))
    except ExecutionContract.DoesNotExist:
        return {
            "status": "CONTRACT_NOT_FOUND",
            "error": "Handoff identifier is unknown.",
        }
    except ValueError as exc:
        return {"status": str(exc), "error": "Execution Contract cannot be revoked."}
    return {
        "status": "EXECUTION_CONTRACT_REVOKED",
        "execution_contract": _contract_view(contract),
    }


def _scope(payload: dict[str, Any]) -> ExecutableScope:
    return ExecutableScope.objects.get(
        identifier=str(payload.get("scope_identifier", "")).strip()
    )


@mcp_operation("scope.classify")
def scope_classify(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        return {
            "status": "SCOPE_CLASSIFIED",
            "classification": classify_request(
                str(payload.get("request", "")), requested_kind=payload.get("kind")
            ),
        }
    except ValueError as exc:
        return {"status": str(exc)}


def _propose(payload: dict[str, Any], root: Path, kind: str) -> dict[str, Any]:
    del root
    try:
        scope = propose_scope(
            Project.objects.get(project_id=str(payload.get("project_id", ""))),
            str(payload.get("request", "")),
            kind=kind,
            title=payload.get("title"),
            task_type=payload.get("task_type"),
            execution_level=str(payload.get("execution_level", "TASK")),
            risk_modifiers=list(payload.get("risk_modifiers", [])),
        )
        review = review_scope(scope)
        return {
            "status": review["clarification_state"]
            if review["clarification_state"] == "CLARIFICATION_REQUIRED"
            else "SCOPE_PROPOSED",
            "scope": scope.record,
            "proposal_review": review,
        }
    except Project.DoesNotExist:
        return {"status": "PROJECT_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


@mcp_operation("sprint.propose")
def sprint_propose(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    return _propose(payload, repository_root, "SPRINT")


@mcp_operation("work_item.propose")
def work_item_propose(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    return _propose(payload, repository_root, "WORK_ITEM")


@mcp_operation("work_item.validate")
@mcp_operation("sprint.validate")
@mcp_operation("scope.validate")
def scope_validate(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        scope = _scope(payload)
        validate_scope_record(scope.record, scope.project)
        return {"status": "SCOPE_VALID", "scope": scope.record}
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


@mcp_operation("work_item.approve")
@mcp_operation("sprint.approve")
@mcp_operation("scope.approve")
def scope_approve(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        scope = bind_approval(
            _scope(payload), str(payload.get("approval_reference", ""))
        )
        return {"status": "SCOPE_APPROVED", "scope": scope.record}
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


@mcp_operation("work_item.publish")
@mcp_operation("sprint.publish")
@mcp_operation("scope.publish")
def scope_publish(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    try:
        scope = publish_scope(_scope(payload), repository_root)
        return {
            "status": "SCOPE_PUBLISHED",
            "scope": scope.record,
            "published_path": scope.published_path,
        }
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


@mcp_operation("work_item.get")
@mcp_operation("sprint.get")
@mcp_operation("scope.get")
def scope_get(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        scope = _scope(payload)
        return {
            "status": "SCOPE_RETRIEVED",
            "scope": scope.record,
            "published_path": scope.published_path,
            "proposal_review": review_scope(scope),
        }
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}


@mcp_operation("scope.review")
def scope_review(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    del repository_root
    try:
        return {
            "status": "PROPOSAL_REVIEW",
            "proposal_review": review_scope(_scope(payload)),
        }
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}


@mcp_operation("scope.answer_clarifications")
def scope_answer_clarifications(
    payload: dict[str, Any], repository_root: Path
) -> dict[str, Any]:
    del repository_root
    try:
        scope = answer_clarifications(_scope(payload), dict(payload.get("answers", {})))
        return {
            "status": "SCOPE_REVISED",
            "scope": scope.record,
            "proposal_review": review_scope(scope),
        }
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


@mcp_operation("scope.contract.generate")
def scope_contract_generate(
    payload: dict[str, Any], repository_root: Path
) -> dict[str, Any]:
    try:
        contract = generate_scope_execution_contract(
            _scope(payload),
            repository_root,
        )
        return {
            "status": "EXECUTION_CONTRACT_GENERATED",
            "execution_contract": _contract_view(contract),
        }
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


def _close_scope(
    payload: dict[str, Any], status: str, repository_root: Path
) -> dict[str, Any]:
    try:
        scope = close_scope(_scope(payload), status)
        if scope.published_path:
            (repository_root / scope.published_path).write_text(
                render_scope(scope), encoding="utf-8"
            )
        return {"status": f"SCOPE_{status}", "scope": scope.record}
    except ExecutableScope.DoesNotExist:
        return {"status": "SCOPE_NOT_FOUND"}
    except ValueError as exc:
        return {"status": str(exc)}


@mcp_operation("scope.complete")
def scope_complete(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    return _close_scope(payload, "COMPLETED", repository_root)


@mcp_operation("scope.cancel")
def scope_cancel(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    return _close_scope(payload, "CANCELLED", repository_root)


@mcp_operation("scope.supersede")
def scope_supersede(payload: dict[str, Any], repository_root: Path) -> dict[str, Any]:
    return _close_scope(payload, "SUPERSEDED", repository_root)

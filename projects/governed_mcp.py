"""Governed public MCP tool registry; HTTP only adapts this canonical surface."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from django.conf import settings

from .contract_policy import resolve_policy
from .mcp import invoke_operation
from .models import (
    ExecutionContract,
    ExecutionPreparation,
    ExecutionStartRequest,
    GovernanceApproval,
    McpAuditEvent,
    McpIdempotencyRecord,
    Project,
)

TOOL_SURFACE_VERSION = "2026-07-26.1"
READ_ONLY = "READ_ONLY"
PREPARATORY_STATE = "PREPARATORY_STATE"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
LIFECYCLE_MUTATION = "LIFECYCLE_MUTATION"
EXECUTION_BOUNDARY = "EXECUTION_BOUNDARY"
MUTATING = {
    PREPARATORY_STATE,
    APPROVAL_REQUIRED,
    LIFECYCLE_MUTATION,
    EXECUTION_BOUNDARY,
}


def _schema(
    properties: dict[str, Any] | None = None, required: list[str] | None = None
) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": False,
    }


_PROJECT = {"project_id": {"type": "string", "minLength": 1, "maxLength": 128}}
_APPROVAL = {"approval_reference": {"type": "string", "minLength": 1, "maxLength": 128}}
_IDEMPOTENCY = {"idempotency_key": {"type": "string", "minLength": 8, "maxLength": 128}}


def _tool(
    name: str,
    description: str,
    classification: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": _schema(properties, required),
        "outputSchema": {"type": "object"},
        "annotations": {
            "readOnlyHint": classification == READ_ONLY,
            "destructiveHint": classification
            in {LIFECYCLE_MUTATION, EXECUTION_BOUNDARY},
            "idempotentHint": classification in {READ_ONLY, PREPARATORY_STATE},
            "openWorldHint": False,
        },
        "_classification": classification,
    }


_TOOLS = [
    _tool(
        "factory.get_status",
        "Read-only Bridge service status and visible projects.",
        READ_ONLY,
    ),
    _tool(
        "factory.list_capabilities",
        "List the versioned governed MCP capabilities available to this caller.",
        READ_ONLY,
    ),
    _tool(
        "project.list",
        "List visible ready projects; optional filters never reveal hidden projects.",
        READ_ONLY,
        {
            "query": {"type": "string", "maxLength": 128},
            "repository": {"type": "string", "maxLength": 255},
            "lifecycle": {"type": "string", "enum": ["ACTIVE", "INACTIVE"]},
            "onboarding_status": {
                "type": "string", "enum": ["PENDING", "READY", "INVALID"]
            },
        },
    ),
    _tool(
        "project.resolve",
        "Resolve a project query; ambiguous matches return a continuation token.",
        READ_ONLY,
        {"query": {"type": "string", "minLength": 1, "maxLength": 128}},
        ["query"],
    ),
    _tool(
        "project.continue_resolution",
        "Select one candidate from a prior ambiguous project resolution.",
        PREPARATORY_STATE,
        {
            "continuation_token": {"type": "string"},
            "project_id": _PROJECT["project_id"],
            **_IDEMPOTENCY,
        },
        ["continuation_token", "project_id", "idempotency_key"],
    ),
    _tool(
        "project.get",
        "Get one visible project record.",
        READ_ONLY,
        _PROJECT,
        ["project_id"],
    ),
    _tool(
        "project.get_context",
        "Get a bounded execution context for a visible project and approved Sprint.",
        READ_ONLY,
        {
            **_PROJECT,
            "sprint_path": {
                "type": "string",
                "pattern": "^docs/sprints/[A-Za-z0-9_.-]+\\.md$",
            },
        },
        ["project_id", "sprint_path"],
    ),
    _tool(
        "akb.search",
        "Search bounded project AKB documents; returns at most ten safe snippets.",
        READ_ONLY,
        {
            **_PROJECT,
            "query": {"type": "string", "minLength": 1, "maxLength": 200},
            "limit": {"type": "integer", "minimum": 1, "maximum": 10},
            "categories": {
                "type": "array",
                "maxItems": 2,
                "items": {"type": "string", "enum": ["current-state", "roadmap"]},
            },
        },
        ["project_id", "query"],
    ),
    _tool(
        "akb.get_document",
        "Get one allowed AKB document by returned document id.",
        READ_ONLY,
        {
            **_PROJECT,
            "document_id": {"type": "string", "enum": ["current-state", "roadmap"]},
        },
        ["project_id", "document_id"],
    ),
    _tool(
        "execution.prepare",
        "Create a non-issuing execution preparation for an approved Sprint.",
        PREPARATORY_STATE,
        {
            **_PROJECT,
            "intent": {"type": "string", "minLength": 1, "maxLength": 1000},
            "execution_level": {
                "type": "string",
                "enum": ["HOTFIX", "BUGFIX", "TASK", "SPRINT", "EPIC"],
            },
            "task_type": {
                "type": "string",
                "enum": [
                    "FEATURE",
                    "BUGFIX",
                    "MIGRATION",
                    "RECOVERY",
                    "DOCUMENTATION",
                    "RELEASE",
                    "SELF_DEVELOPMENT",
                    "ONBOARDING",
                    "SECURITY",
                    "CONFIGURATION",
                ],
            },
            "risk_modifiers": {"type": "array", "maxItems": 16},
            "sprint_path": {
                "type": "string",
                "pattern": "^docs/sprints/[A-Za-z0-9_.-]+\\.md$",
            },
            **_IDEMPOTENCY,
        },
        [
            "project_id",
            "intent",
            "execution_level",
            "task_type",
            "risk_modifiers",
            "sprint_path",
            "idempotency_key",
        ],
    ),
    _tool(
        "execution.get_status",
        "Read an execution preparation status.",
        READ_ONLY,
        {"preparation_token": {"type": "string"}},
        ["preparation_token"],
    ),
    _tool(
        "execution.continue",
        "Resume a durable, non-executing preparation without client-side state.",
        PREPARATORY_STATE,
        {"preparation_token": {"type": "string"}, **_IDEMPOTENCY},
        ["preparation_token", "idempotency_key"],
    ),
    _tool(
        "execution.render_handoff",
        "Render a bounded handoff from an execution preparation.",
        READ_ONLY,
        {"preparation_token": {"type": "string"}},
        ["preparation_token"],
    ),
    _tool(
        "execution.request_start",
        "Create a durable start request for a consumed approved contract.",
        EXECUTION_BOUNDARY,
        {"handoff_identifier": {"type": "string"}, **_APPROVAL, **_IDEMPOTENCY},
        ["handoff_identifier", "approval_reference", "idempotency_key"],
    ),
]
for action, classification in [
    ("generate", PREPARATORY_STATE),
    ("validate", PREPARATORY_STATE),
    ("issue", APPROVAL_REQUIRED),
    ("consume", LIFECYCLE_MUTATION),
    ("complete", LIFECYCLE_MUTATION),
    ("supersede", LIFECYCLE_MUTATION),
    ("revoke", LIFECYCLE_MUTATION),
]:
    props = {"handoff_identifier": {"type": "string"}, **_IDEMPOTENCY}
    required = ["handoff_identifier", "idempotency_key"]
    if action == "generate":
        props = {
            **_PROJECT,
            "sprint_path": {"type": "string"},
            "intent": {"type": "string", "minLength": 1, "maxLength": 1000},
            "execution_level": {
                "type": "string",
                "enum": ["HOTFIX", "BUGFIX", "TASK", "SPRINT", "EPIC"],
            },
            "task_type": {
                "type": "string",
                "enum": [
                    "FEATURE",
                    "BUGFIX",
                    "MIGRATION",
                    "RECOVERY",
                    "DOCUMENTATION",
                    "RELEASE",
                    "SELF_DEVELOPMENT",
                    "ONBOARDING",
                    "SECURITY",
                    "CONFIGURATION",
                ],
            },
            "risk_modifiers": {
                "type": "array",
                "maxItems": 16,
                "items": {
                    "type": "string",
                    "enum": [
                        "AUTHENTICATION_OR_AUTHORIZATION",
                        "CROSS_REPOSITORY",
                        "EXTERNAL_INTEGRATION",
                        "IRREVERSIBLE_OPERATION",
                        "PUBLIC_API_OR_PROTOCOL",
                    ],
                },
            },
            "preparation_token": {"type": "string"},
            **_IDEMPOTENCY,
        }
        required = [
            "project_id",
            "sprint_path",
            "intent",
            "execution_level",
            "task_type",
            "risk_modifiers",
            "preparation_token",
            "idempotency_key",
        ]
    if classification in {APPROVAL_REQUIRED, LIFECYCLE_MUTATION}:
        props = {**props, **_APPROVAL}
        required.append("approval_reference")
    _TOOLS.append(
        _tool(
            f"contract.{action}",
            f"Governed contract lifecycle action: {action}.",
            classification,
            props,
            required,
        )
    )
_TOOLS.extend(
    [
        _tool(
            "contract.get_status",
            "Read a governed execution contract lifecycle status.",
            READ_ONLY,
            {"handoff_identifier": {"type": "string"}},
            ["handoff_identifier"],
        ),
        _tool(
            "contract.render_handoff",
            "Read a bounded contract handoff.",
            READ_ONLY,
            {"handoff_identifier": {"type": "string"}},
            ["handoff_identifier"],
        ),
    ]
)
# Lifecycle operations are intentionally strict; their durable reasons and
# replacement bindings are required by the canonical domain service.
for tool in _TOOLS:
    if tool["name"] == "contract.complete":
        tool["inputSchema"] = _schema(
            {
                "handoff_identifier": {"type": "string"},
                "final_commit_sha": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "closure_state": {
                    "type": "string",
                    "enum": [
                        "PASS — READY FOR PRODUCT OWNER REVIEW",
                        "BLOCKED — BUSINESS DECISION REQUIRED",
                        "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE",
                    ],
                },
                **_APPROVAL,
                **_IDEMPOTENCY,
            },
            [
                "handoff_identifier",
                "final_commit_sha",
                "closure_state",
                "approval_reference",
                "idempotency_key",
            ],
        )
    elif tool["name"] == "contract.supersede":
        tool["inputSchema"] = _schema(
            {
                "handoff_identifier": {"type": "string"},
                "replacement_handoff_identifier": {"type": "string"},
                "reason": {"type": "string", "minLength": 1, "maxLength": 500},
                **_APPROVAL,
                **_IDEMPOTENCY,
            },
            [
                "handoff_identifier",
                "replacement_handoff_identifier",
                "reason",
                "approval_reference",
                "idempotency_key",
            ],
        )
    elif tool["name"] == "contract.revoke":
        tool["inputSchema"] = _schema(
            {
                "handoff_identifier": {"type": "string"},
                "reason": {"type": "string", "minLength": 1, "maxLength": 500},
                **_APPROVAL,
                **_IDEMPOTENCY,
            },
            ["handoff_identifier", "reason", "approval_reference", "idempotency_key"],
        )
TOOLS = {tool["name"]: tool for tool in _TOOLS}


def public_tools() -> list[dict[str, Any]]:
    """Return stable tool metadata without internal classification fields."""
    return [
        {key: value for key, value in tool.items() if key != "_classification"}
        for tool in _TOOLS
    ]


def _project(arguments: dict[str, Any]) -> Project:
    try:
        return Project.objects.get(
            project_id=arguments["project_id"],
            lifecycle=Project.Lifecycle.ACTIVE,
            onboarding_status=Project.OnboardingStatus.READY,
        )
    except Project.DoesNotExist:
        raise ValueError("PROJECT_NOT_VISIBLE: select a ready visible project.")


def _approval(
    arguments: dict[str, Any], project: Project, action: str
) -> GovernanceApproval:
    try:
        approval = GovernanceApproval.objects.get(
            reference=arguments["approval_reference"],
            project=project,
            revoked_at__isnull=True,
        )
    except GovernanceApproval.DoesNotExist:
        raise ValueError(
            "APPROVAL_REQUIRED: provide a durable, non-revoked approval reference."
        )
    if approval.approved_action not in {action, "ALL_GOVERNED_MUTATIONS"}:
        raise ValueError("APPROVAL_ACTION_NOT_AUTHORIZED")
    return approval


def _audit(
    caller: str,
    tool: str,
    project: Project | None,
    outcome: str,
    details: dict[str, Any],
) -> None:
    McpAuditEvent.objects.create(
        caller=caller, tool_name=tool, project=project, outcome=outcome, details=details
    )


def _idempotent(
    caller: str, tool: str, arguments: dict[str, Any]
) -> dict[str, Any] | None:
    if tool not in TOOLS or TOOLS[tool]["_classification"] not in MUTATING:
        return None
    key = arguments.get("idempotency_key")
    if not isinstance(key, str):
        raise ValueError("IDEMPOTENCY_KEY_REQUIRED")
    fingerprint = hashlib.sha256(
        json.dumps(arguments, sort_keys=True).encode()
    ).hexdigest()
    record = McpIdempotencyRecord.objects.filter(
        caller=caller, tool_name=tool, key=key
    ).first()
    if record:
        if record.request_fingerprint != fingerprint:
            raise ValueError("IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST")
        return record.result
    return None


def _store_idempotent(
    caller: str, tool: str, arguments: dict[str, Any], result: dict[str, Any]
) -> None:
    if TOOLS[tool]["_classification"] in MUTATING:
        McpIdempotencyRecord.objects.create(
            caller=caller,
            tool_name=tool,
            key=arguments["idempotency_key"],
            request_fingerprint=hashlib.sha256(
                json.dumps(arguments, sort_keys=True).encode()
            ).hexdigest(),
            result=result,
        )


def _akb(project: Project, document_id: str) -> tuple[str, str]:
    if project.project_id != "ai-bridge":
        raise ValueError("AKB_DOCUMENT_NOT_AVAILABLE")
    allowed = {
        "current-state": "docs/akb/CURRENT_STATE.md",
        "roadmap": "docs/roadmap/ROADMAP.md",
    }
    if document_id not in allowed:
        raise ValueError("AKB_DOCUMENT_NOT_AVAILABLE")
    return document_id, (Path(settings.BASE_DIR) / allowed[document_id]).read_text(
        encoding="utf-8"
    )[:12000]


def invoke_public_tool(
    name: str, arguments: Any, caller: str = "bearer-token"
) -> dict[str, Any]:
    """Authorize, validate and invoke one safe public tool."""
    if name not in TOOLS:
        raise ValueError("UNKNOWN_TOOL")
    if not isinstance(arguments, dict):
        raise ValueError("ARGUMENTS_OBJECT_REQUIRED")
    tool = TOOLS[name]
    schema = tool["inputSchema"]
    unknown = set(arguments).difference(schema["properties"])
    missing = [key for key in schema["required"] if key not in arguments]
    if unknown or missing:
        raise ValueError(
            "INVALID_ARGUMENTS: remove unknown properties and provide "
            "required properties"
        )
    for key, value in arguments.items():
        definition = schema["properties"][key]
        expected = definition.get("type")
        if expected == "string" and not isinstance(value, str):
            raise ValueError(f"INVALID_ARGUMENT_TYPE: {key} must be a string")
        if expected == "array" and not isinstance(value, list):
            raise ValueError(f"INVALID_ARGUMENT_TYPE: {key} must be an array")
        if expected == "integer" and (
            not isinstance(value, int) or isinstance(value, bool)
        ):
            raise ValueError(f"INVALID_ARGUMENT_TYPE: {key} must be an integer")
        if "enum" in definition and value not in definition["enum"]:
            raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} is not an allowed value")
        if isinstance(value, list):
            if len(value) > definition.get("maxItems", 2**31):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} has too many items")
            item_definition = definition.get("items", {})
            item_enum = item_definition.get("enum")
            if item_enum is not None and any(item not in item_enum for item in value):
                raise ValueError(
                    f"INVALID_ARGUMENT_VALUE: {key} contains an invalid item"
                )
        if isinstance(value, str):
            if len(value) < definition.get("minLength", 0):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} is too short")
            if len(value) > definition.get("maxLength", 2**31):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} is too long")
            if (
                "pattern" in definition
                and re.fullmatch(definition["pattern"], value) is None
            ):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} has invalid format")
        if isinstance(value, int) and not isinstance(value, bool):
            if value < definition.get("minimum", -(2**31)):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} is too small")
            if value > definition.get("maximum", 2**31):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key} is too large")
    replay = _idempotent(caller, name, arguments)
    if replay is not None:
        return {**replay, "idempotent_replay": True}
    project = _project(arguments) if "project_id" in arguments else None
    try:
        if name == "factory.get_status":
            projects = list(
                Project.objects.filter(lifecycle="ACTIVE", onboarding_status="READY")
                .order_by("project_id")
                .values(
                    "project_id",
                    "repository_full_name",
                    "lifecycle",
                    "onboarding_status",
                )
            )
            result = {
                "service": "ai-bridge",
                "transport": "streamable-http",
                "protocol_version": "2025-03-26",
                "tool_surface_version": TOOL_SURFACE_VERSION,
                "project_count": len(projects),
                "projects": projects,
            }
        elif name == "factory.list_capabilities":
            result = {
                "tool_surface_version": TOOL_SURFACE_VERSION,
                "tools": [
                    {"name": t["name"], "classification": t["_classification"]}
                    for t in _TOOLS
                ],
            }
        elif name == "project.list":
            visible_projects = Project.objects.filter(
                lifecycle="ACTIVE", onboarding_status="READY"
            )
            if arguments.get("query"):
                visible_projects = visible_projects.filter(
                    display_name__icontains=arguments["query"]
                )
            if arguments.get("repository"):
                visible_projects = visible_projects.filter(
                    repository_full_name__icontains=arguments["repository"]
                )
            if arguments.get("lifecycle"):
                visible_projects = visible_projects.filter(
                    lifecycle=arguments["lifecycle"]
                )
            if arguments.get("onboarding_status"):
                visible_projects = visible_projects.filter(
                    onboarding_status=arguments["onboarding_status"]
                )
            result = {
                "projects": list(
                    visible_projects.values(
                        "project_id", "display_name", "repository_full_name"
                    )
                )
            }
        elif name == "project.resolve":
            result = invoke_operation(
                "resolve_project",
                {"query": arguments["query"]},
                Path(settings.BASE_DIR),
            )
        elif name == "project.continue_resolution":
            result = invoke_operation(
                "continue_project_resolution",
                {
                    "continuation_token": arguments["continuation_token"],
                    "selected_project_id": arguments["project_id"],
                },
                Path(settings.BASE_DIR),
            )
        elif name == "project.get":
            assert project is not None
            result = {
                "project_id": project.project_id,
                "display_name": project.display_name,
                "repository": project.repository_full_name,
                "status": project.onboarding_status,
            }
        elif name == "project.get_context":
            assert project is not None
            result = invoke_operation(
                "generate_execution_context",
                {
                    "project_id": project.project_id,
                    "approved_sprint_path": arguments["sprint_path"],
                },
                Path(settings.BASE_DIR),
            )
        elif name == "akb.get_document":
            assert project is not None
            ident, content = _akb(project, arguments["document_id"])
            result = {"document_id": ident, "content": content}
        elif name == "akb.search":
            assert project is not None
            hits = []
            for ident in arguments.get("categories", ["current-state", "roadmap"]):
                _, content = _akb(project, ident)
                for line in content.splitlines():
                    if arguments["query"].lower() in line.lower():
                        hits.append({"document_id": ident, "snippet": line[:500]})
            limit = arguments.get("limit", 10)
            result = {
                "results": [
                    {**hit, "rank": index + 1, "accepted": True}
                    for index, hit in enumerate(hits[:limit])
                ],
                "result_limit": limit,
                "search_capability": "bounded deterministic accepted-document search",
            }
        elif name == "execution.prepare":
            assert project is not None
            policy = resolve_policy(
                arguments["execution_level"],
                arguments["task_type"],
                arguments["risk_modifiers"],
            )
            execution_context = invoke_operation(
                "generate_execution_context",
                {
                    "project_id": project.project_id,
                    "approved_sprint_path": arguments["sprint_path"],
                },
                Path(settings.BASE_DIR),
            )
            preparation_data = {
                "intent": arguments["intent"],
                "execution_level": arguments["execution_level"],
                "task_type": arguments["task_type"],
                "risk_modifiers": arguments["risk_modifiers"],
                "resolved_policy": policy,
                "execution_context": execution_context,
                "missing_product_owner_inputs": [],
                "approved_sprint_required": True,
            }
            prep = ExecutionPreparation.objects.create(
                project=project,
                sprint_path=arguments["sprint_path"],
                preparation_data=preparation_data,
            )
            result = {
                "status": "EXECUTION_PREPARED",
                "preparation_token": str(prep.token),
                "execution_context": execution_context,
                "resolved_policy": policy,
                "missing_product_owner_inputs": [],
                "approved_sprint_required": True,
                "next_allowed_action": "contract.generate",
                "next_tool": "contract.generate",
            }
        elif name in {
            "execution.get_status",
            "execution.continue",
            "execution.render_handoff",
        }:
            prep = ExecutionPreparation.objects.get(
                token=arguments["preparation_token"]
            )
            result = {
                "status": prep.status,
                "preparation_token": str(prep.token),
                "project_id": prep.project.project_id,
                "sprint_path": prep.sprint_path,
                "resolved_policy": prep.preparation_data.get("resolved_policy", {}),
                "missing_product_owner_inputs": prep.preparation_data.get(
                    "missing_product_owner_inputs", []
                ),
                "next_allowed_action": "contract.generate",
            }
            if name == "execution.render_handoff":
                result["handoff"] = (
                    f"Execution preparation {prep.token}\n"
                    f"Project: {prep.project.project_id}\n"
                    f"Sprint: {prep.sprint_path}\n"
                    f"Intent: {prep.preparation_data.get('intent', '')}\n"
                    f"Next allowed action: contract.generate"
                )
        elif name == "execution.request_start":
            contract = ExecutionContract.objects.get(
                handoff_identifier=arguments["handoff_identifier"],
                lifecycle=ExecutionContract.Lifecycle.CONSUMED,
            )
            approval = _approval(arguments, contract.project, "execution.request_start")
            req = ExecutionStartRequest.objects.create(
                contract=contract, approval=approval
            )
            result = {
                "status": req.status,
                "request_id": req.pk,
                "next_action": req.next_action,
            }
        elif name.startswith("contract."):
            action = name.split(".")[1]
            op = {
                "generate": "generate_execution_contract",
                "validate": "validate_execution_contract",
                "issue": "issue_execution_contract",
                "consume": "consume_execution_contract",
                "complete": "complete_execution_contract",
                "supersede": "supersede_execution_contract",
                "revoke": "revoke_execution_contract",
                "get_status": "get_execution_contract",
                "render_handoff": "render_execution_handoff",
            }[action]
            payload = {"handoff_identifier": arguments.get("handoff_identifier", "")}
            if action == "generate":
                assert project is not None
                prep = ExecutionPreparation.objects.get(
                    token=arguments["preparation_token"], project=project
                )
                if prep.sprint_path != arguments["sprint_path"]:
                    raise ValueError("PREPARATION_SPRINT_MISMATCH")
                payload = {
                    "project_id": project.project_id,
                    "approved_sprint_path": arguments["sprint_path"],
                    "task_type": arguments["task_type"],
                    "intent": arguments["intent"],
                    "execution_level": arguments["execution_level"],
                    "risk_modifiers": arguments["risk_modifiers"],
                }
            elif action == "complete":
                payload.update(
                    {
                        "final_commit_sha": arguments["final_commit_sha"],
                        "closure_state": arguments["closure_state"],
                    }
                )
            elif action == "supersede":
                payload["replacement_handoff_identifier"] = arguments[
                    "replacement_handoff_identifier"
                ]
            elif action == "revoke":
                payload["reason"] = arguments["reason"]
            if tool["_classification"] in {APPROVAL_REQUIRED, LIFECYCLE_MUTATION}:
                contract = ExecutionContract.objects.get(
                    handoff_identifier=payload["handoff_identifier"]
                )
                _approval(arguments, contract.project, f"contract.{action}")
            result = invoke_operation(op, payload, Path(settings.BASE_DIR))
        else:
            raise ValueError("TOOL_NOT_IMPLEMENTED")
        _store_idempotent(caller, name, arguments, result)
        _audit(caller, name, project, "SUCCESS", {"status": result.get("status", "OK")})
        return result
    except Exception as exc:
        _audit(caller, name, project, "REJECTED", {"code": str(exc)[:200]})
        raise

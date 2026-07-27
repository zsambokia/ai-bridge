"""Governed public MCP tool registry; HTTP only adapts this canonical surface."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from django.conf import settings

from .contract_policy import EXECUTION_LEVELS, RISK_MODIFIERS, TASK_TYPES
from .contracts import (
    complete_execution_contract,
    consume_execution_contract,
    generate_scope_execution_contract,
    issue_execution_contract,
    validate_execution_contract,
)
from .execution import add_event, complete_run, provider, start_run
from .mcp import invoke_operation
from .models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionContract,
    ExecutionPreparation,
    ExecutionProgressEvent,
    ExecutionProvider,
    ExecutionRun,
    ExecutionStartRequest,
    GovernanceApproval,
    McpAuditEvent,
    McpIdempotencyRecord,
    Project,
)
from .providers import public_provider
from .scopes import (
    answer_clarifications,
    approved_scope,
    bind_approval,
    publish_scope,
    review_scope,
)
from .services import project_repository_root

TOOL_SURFACE_VERSION = "2026-07-27.1"
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
_PRODUCT_OWNER_CONFIRMATIONS = {
    "igen",
    "igen jo lesz",
    "jo lesz igy",
    "mehet",
    "rendben csinald meg",
}


def _schema(
    properties: dict[str, Any] | None = None, required: list[str] | None = None
) -> dict[str, Any]:
    properties = properties or {}
    required = required or []
    unknown_required = set(required).difference(properties)
    if unknown_required:
        raise ValueError(
            "MCP_SCHEMA_INVALID: required properties are not declared: "
            + ", ".join(sorted(unknown_required))
        )
    return {
        "type": "object",
        "properties": properties,
        "required": required,
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
        "provider.list",
        "List safe provider registry summaries; no configuration or credentials.",
        READ_ONLY,
    ),
    _tool(
        "provider.get",
        "Get one safe provider registry summary.",
        READ_ONLY,
        {"provider_id": {"type": "string", "minLength": 1, "maxLength": 64}},
        ["provider_id"],
    ),
    _tool(
        "provider.capabilities",
        "Get published capabilities for one provider.",
        READ_ONLY,
        {"provider_id": {"type": "string", "minLength": 1, "maxLength": 64}},
        ["provider_id"],
    ),
    _tool(
        "provider.health",
        "Get the last safe, non-secret provider health projection.",
        READ_ONLY,
        {"provider_id": {"type": "string", "minLength": 1, "maxLength": 64}},
        ["provider_id"],
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
                "type": "string",
                "enum": ["PENDING", "READY", "INVALID"],
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
        "Get a bounded context for one canonical, approved executable scope.",
        READ_ONLY,
        {
            **_PROJECT,
            "scope_identifier": {"type": "string", "minLength": 1},
        },
        ["project_id", "scope_identifier"],
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
        "Create a non-issuing preparation from an approved canonical scope.",
        PREPARATORY_STATE,
        {
            **_PROJECT,
            "scope_identifier": {"type": "string", "minLength": 1},
            **_IDEMPOTENCY,
        },
        [
            "project_id",
            "scope_identifier",
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
        "Authorize and start a consumed contract through the canonical provider.",
        EXECUTION_BOUNDARY,
        {"handoff_identifier": {"type": "string"}, **_APPROVAL, **_IDEMPOTENCY},
        ["handoff_identifier", "approval_reference", "idempotency_key"],
    ),
    _tool(
        "execution.get_run_status",
        "Read a bounded execution-run status.",
        READ_ONLY,
        {"execution_token": {"type": "string"}},
        ["execution_token"],
    ),
    _tool(
        "execution.list_events",
        "List ordered bounded events for one execution run.",
        READ_ONLY,
        {"execution_token": {"type": "string"}},
        ["execution_token"],
    ),
    _tool(
        "execution.cancel",
        "Cancel one active execution with durable Product Owner authority.",
        EXECUTION_BOUNDARY,
        {"execution_token": {"type": "string"}, **_APPROVAL, **_IDEMPOTENCY},
        ["execution_token", "approval_reference", "idempotency_key"],
    ),
    _tool(
        "execution.evidence_summary",
        "Read final execution evidence binding metadata.",
        READ_ONLY,
        {"execution_token": {"type": "string"}},
        ["execution_token"],
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
            "scope_identifier": {"type": "string", "minLength": 1},
            "preparation_token": {"type": "string"},
            **_IDEMPOTENCY,
        }
        required = [
            "project_id",
            "scope_identifier",
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
            "scope.classify",
            "Classify a natural-language request without creating authority.",
            READ_ONLY,
            {"request": {"type": "string", "minLength": 1, "maxLength": 4000}},
            ["request"],
        ),
        *[
            _tool(
                name,
                "Propose a canonical Bridge-managed executable scope.",
                PREPARATORY_STATE,
                {
                    **_PROJECT,
                    "request": {"type": "string", "minLength": 1, "maxLength": 4000},
                    "title": {"type": "string", "maxLength": 160},
                    "task_type": {"type": "string", "enum": sorted(TASK_TYPES)},
                    "work_type": {"type": "string", "enum": sorted(TASK_TYPES)},
                    "audit_target": {"type": "string", "maxLength": 4000},
                    "audit_questions": {"type": "array", "items": {"type": "string"}},
                    "required_inventory": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "required_classifications": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "mutation_policy": {
                        "type": "string",
                        "enum": ["READ_ONLY", "REPAIR_ALLOWED"],
                    },
                    "repair_rule": {"type": "string", "maxLength": 1000},
                    "acceptance_checks": {"type": "array", "items": {"type": "string"}},
                    "execution_level": {
                        "type": "string",
                        "enum": sorted(EXECUTION_LEVELS),
                    },
                    "risk_modifiers": {
                        "type": "array",
                        "maxItems": len(RISK_MODIFIERS),
                        "items": {"type": "string", "enum": sorted(RISK_MODIFIERS)},
                    },
                    **_IDEMPOTENCY,
                },
                ["project_id", "request", "idempotency_key"],
            )
            for name in ("sprint.propose", "work_item.propose")
        ],
        _tool(
            "scope.validate",
            "Validate one canonical scope record and projection.",
            READ_ONLY,
            {"scope_identifier": {"type": "string", "minLength": 1}},
            ["scope_identifier"],
        ),
        _tool(
            "scope.approve",
            "Bind durable Product Owner execution approval to a scope.",
            APPROVAL_REQUIRED,
            {
                "scope_identifier": {"type": "string", "minLength": 1},
                **_APPROVAL,
                **_IDEMPOTENCY,
            },
            ["scope_identifier", "approval_reference", "idempotency_key"],
        ),
        _tool(
            "scope.publish",
            "Publish a deterministic projection of an approved scope.",
            LIFECYCLE_MUTATION,
            {"scope_identifier": {"type": "string", "minLength": 1}, **_IDEMPOTENCY},
            ["scope_identifier", "idempotency_key"],
        ),
        _tool(
            "scope.get",
            "Retrieve canonical scope data and publication path.",
            READ_ONLY,
            {"scope_identifier": {"type": "string", "minLength": 1}},
            ["scope_identifier"],
        ),
        _tool(
            "scope.review",
            "Return the exact pending proposal and any clarification questions.",
            READ_ONLY,
            {**_PROJECT, "scope_identifier": {"type": "string", "minLength": 1}},
            ["project_id", "scope_identifier"],
        ),
        _tool(
            "scope.answer_clarifications",
            "Record complete clarification answers and create a new proposal version.",
            PREPARATORY_STATE,
            {
                **_PROJECT,
                "scope_identifier": {"type": "string", "minLength": 1},
                "answers": {"type": "object"},
                **_IDEMPOTENCY,
            },
            ["project_id", "scope_identifier", "answers", "idempotency_key"],
        ),
        _tool(
            "scope.confirm_and_execute",
            (
                "Advanced structured confirmation: bind a reviewed proposal with "
                "its already-displayed version, hash, and durable Product Owner "
                "context."
            ),
            EXECUTION_BOUNDARY,
            {
                **_PROJECT,
                "scope_identifier": {"type": "string", "minLength": 1},
                "proposal_version": {"type": "integer", "minimum": 1},
                "proposal_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "product_owner_identity": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
                "confirmation_reference": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                },
                **_IDEMPOTENCY,
            },
            [
                "project_id",
                "scope_identifier",
                "proposal_version",
                "proposal_hash",
                "product_owner_identity",
                "confirmation_reference",
                "idempotency_key",
            ],
        ),
        _tool(
            "conversation.confirm",
            (
                "Confirm the exact pending proposal from an authenticated Product "
                "Owner reply. Supply only the displayed scope and affirmative "
                "reply; identity, confirmation reference, proposal binding, and "
                "retry key are derived by the governed service."
            ),
            EXECUTION_BOUNDARY,
            {
                **_PROJECT,
                "scope_identifier": {"type": "string", "minLength": 1},
                "confirmation_text": {"type": "string", "minLength": 1},
            },
            [
                "project_id",
                "scope_identifier",
                "confirmation_text",
            ],
        ),
        _tool(
            "scope.orchestration_status",
            "Read the durable state of a conversational confirmation flow.",
            READ_ONLY,
            {**_PROJECT, "scope_identifier": {"type": "string", "minLength": 1}},
            ["project_id", "scope_identifier"],
        ),
        _tool(
            "scope.complete_execution",
            "Verify a finished provider run and record its evidence-backed result.",
            EXECUTION_BOUNDARY,
            {
                **_PROJECT,
                "scope_identifier": {"type": "string", "minLength": 1},
                "orchestration_token": {"type": "string", "minLength": 36},
                "final_commit_sha": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{40}$",
                },
                "completion_data": {"type": "object"},
                **_IDEMPOTENCY,
            },
            [
                "project_id",
                "scope_identifier",
                "orchestration_token",
                "final_commit_sha",
                "completion_data",
                "idempotency_key",
            ],
        ),
        _tool(
            "scope.contract.generate",
            "Generate an AI Bridge-issued provider-neutral scope contract.",
            PREPARATORY_STATE,
            {"scope_identifier": {"type": "string", "minLength": 1}, **_IDEMPOTENCY},
            ["scope_identifier", "idempotency_key"],
        ),
        *[
            _tool(
                f"scope.{action}",
                f"Close an executable scope as {status.lower()}.",
                LIFECYCLE_MUTATION,
                {
                    "scope_identifier": {"type": "string", "minLength": 1},
                    **_APPROVAL,
                    **_IDEMPOTENCY,
                },
                ["scope_identifier", "approval_reference", "idempotency_key"],
            )
            for action, status in (
                ("complete", "COMPLETED"),
                ("cancel", "CANCELLED"),
                ("supersede", "SUPERSEDED"),
            )
        ],
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
    if tool["name"] == "contract.consume":
        tool["inputSchema"] = _schema(
            {
                "handoff_identifier": {"type": "string"},
                "expected_contract_hash": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{64}$",
                },
                "provider_identity": {"type": "string", "minLength": 1},
                "observed_baseline": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "schema_version": {"type": "string", "const": "2.0"},
                **_APPROVAL,
                **_IDEMPOTENCY,
            },
            [
                "handoff_identifier",
                "expected_contract_hash",
                "provider_identity",
                "observed_baseline",
                "schema_version",
                "approval_reference",
                "idempotency_key",
            ],
        )
    elif tool["name"] == "contract.complete":
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
                "execution_result": {"type": "string", "minLength": 1},
                "gate_results": {"type": "object"},
                "evidence_manifest": {"type": "object"},
                "changed_files": {"type": "array"},
                "failure_classification": {"type": "string"},
                **_APPROVAL,
                **_IDEMPOTENCY,
            },
            [
                "handoff_identifier",
                "final_commit_sha",
                "closure_state",
                "execution_result",
                "gate_results",
                "evidence_manifest",
                "changed_files",
                "failure_classification",
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


def _validate_arguments(schema: dict[str, Any], arguments: dict[str, Any]) -> None:
    """Apply the public JSON-schema subset used by the governed tool registry."""
    properties = schema["properties"]
    unknown = sorted(set(arguments).difference(properties))
    missing = sorted(key for key in schema["required"] if key not in arguments)
    errors = [f"unknown property: {key}" for key in unknown]
    errors.extend(f"missing required property: {key}" for key in missing)
    if errors:
        raise ValueError("INVALID_ARGUMENTS: " + "; ".join(errors))

    expected_types = {
        "string": str,
        "array": list,
        "integer": int,
        "object": dict,
        "boolean": bool,
    }
    for key, value in arguments.items():
        definition = properties[key]
        expected = definition.get("type")
        expected_type = expected_types.get(expected)
        invalid_integer = expected == "integer" and isinstance(value, bool)
        if expected_type is not None and (
            not isinstance(value, expected_type) or invalid_integer
        ):
            raise ValueError(f"INVALID_ARGUMENT_TYPE: {key}: expected {expected}")
        if "const" in definition and value != definition["const"]:
            raise ValueError(
                f"INVALID_ARGUMENT_VALUE: {key}: expected {definition['const']!r}"
            )
        if "enum" in definition and value not in definition["enum"]:
            raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: unsupported value")
        if isinstance(value, list):
            if len(value) > definition.get("maxItems", 2**31):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: too many items")
            item_definition = definition.get("items", {})
            item_type = item_definition.get("type")
            item_python_type = expected_types.get(item_type)
            for index, item in enumerate(value):
                if item_python_type is not None and not isinstance(
                    item, item_python_type
                ):
                    raise ValueError(
                        f"INVALID_ARGUMENT_TYPE: {key}[{index}]: expected {item_type}"
                    )
                if "enum" in item_definition and item not in item_definition["enum"]:
                    raise ValueError(
                        f"INVALID_ARGUMENT_VALUE: {key}[{index}]: unsupported value"
                    )
        if isinstance(value, str):
            if len(value) < definition.get("minLength", 0):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: too short")
            if len(value) > definition.get("maxLength", 2**31):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: too long")
            if (
                "pattern" in definition
                and re.fullmatch(definition["pattern"], value) is None
            ):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: invalid format")
        if isinstance(value, int) and not isinstance(value, bool):
            if value < definition.get("minimum", -(2**31)):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: too small")
            if value > definition.get("maximum", 2**31):
                raise ValueError(f"INVALID_ARGUMENT_VALUE: {key}: too large")


def _project(arguments: dict[str, Any]) -> Project:
    try:
        return Project.objects.get(
            project_id=arguments["project_id"],
            lifecycle=Project.Lifecycle.ACTIVE,
            onboarding_status=Project.OnboardingStatus.READY,
        )
    except Project.DoesNotExist:
        raise ValueError("PROJECT_NOT_VISIBLE: select a ready visible project.")


def _derived_conversation_confirmation(
    arguments: dict[str, Any], caller: str
) -> dict[str, Any]:
    """Bind a simple conversational reply to authenticated MCP request context.

    The public tool intentionally accepts no caller-controlled approval identity,
    reference, proposal version/hash, or idempotency key.  A stable fingerprint
    of the authenticated MCP connection and exact current proposal produces all
    durable values before the ordinary canonical orchestration is entered.
    """
    if _normalise_confirmation(arguments["confirmation_text"]) not in (
        _PRODUCT_OWNER_CONFIRMATIONS
    ):
        raise ValueError("PRODUCT_OWNER_CONFIRMATION_REQUIRED")
    project = _project(arguments)
    scope = ExecutableScope.objects.get(
        project=project, identifier=arguments["scope_identifier"]
    )
    caller_fingerprint = hashlib.sha256(caller.encode("utf-8")).hexdigest()
    product_owner_identity = f"authenticated-mcp-caller:{caller_fingerprint}"
    existing = (
        ConversationOrchestration.objects.filter(
            scope=scope, product_owner_identity=product_owner_identity
        )
        .order_by("created_at")
        .first()
    )
    if existing is not None:
        proposal_version = existing.proposal_version
        proposal_hash = existing.proposal_hash
    else:
        review = review_scope(scope)
        if not review["confirmation_eligible"]:
            raise ValueError("CLARIFICATION_REQUIRED")
        proposal_version = review["proposal_version"]
        proposal_hash = review["proposal_hash"]
    binding = {
        "caller": caller_fingerprint,
        "project_id": project.project_id,
        "scope_identifier": scope.identifier,
        "proposal_version": proposal_version,
        "proposal_hash": proposal_hash,
    }
    digest = hashlib.sha256(
        json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "project_id": arguments["project_id"],
        "scope_identifier": arguments["scope_identifier"],
        "confirmation_text": "igen",
        "product_owner_identity": product_owner_identity,
        "confirmation_reference": f"conversation-confirmation:v1:{digest}",
        "idempotency_key": f"conversation-confirm:v1:{digest}",
    }


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
    if approval.approved_action not in {
        action,
        "ALL_GOVERNED_MUTATIONS",
        "AUTHORIZE_EXECUTION",
        "ALL",
    }:
        raise ValueError("APPROVAL_ACTION_NOT_AUTHORIZED")
    return approval


def _approval_for_contract(
    arguments: dict[str, Any], contract: ExecutionContract, action: str
) -> GovernanceApproval:
    approval = _approval(arguments, contract.project, action)
    declared = contract.payload.get("approved_scope", {})
    if contract.payload.get("schema_version") != "2.0" or not declared:
        raise ValueError("CONTRACT_AUTHORITY_REQUIRED")
    try:
        scope = ExecutableScope.objects.get(
            identifier=declared["identifier"], project=contract.project
        )
    except (ExecutableScope.DoesNotExist, KeyError) as exc:
        raise ValueError("APPROVAL_SCOPE_MISMATCH") from exc
    authorized = approved_scope(scope)
    if (
        approval.scope_id != scope.pk
        or approval.reference != authorized["approval_reference"]
        or declared.get("approval_reference") != approval.reference
    ):
        raise ValueError("APPROVAL_SCOPE_MISMATCH")
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
            # Earlier conversation confirmations stored their fingerprint before
            # the public reply was reduced to its governed, caller-bound form.
            # Permit that one-way normalization only when the durable flow proves
            # that this caller, project, scope and confirmation reference are the
            # same conversation.  All other key reuse remains a hard failure.
            if tool == "conversation.confirm":
                flow = ConversationOrchestration.objects.filter(
                    scope__project__project_id=arguments["project_id"],
                    scope__identifier=arguments["scope_identifier"],
                    confirmation_reference=arguments["confirmation_reference"],
                    product_owner_identity=arguments["product_owner_identity"],
                ).first()
                if flow is not None and record.result.get("orchestration_token") == str(
                    flow.token
                ):
                    record.request_fingerprint = fingerprint
                    record.save(update_fields=["request_fingerprint"])
                else:
                    raise ValueError("IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST")
            else:
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


def _orchestration_result(flow: ConversationOrchestration) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": flow.status,
        "current_step": flow.current_step,
        "orchestration_token": str(flow.token),
        "scope_identifier": flow.scope.identifier,
        "proposal_version": flow.proposal_version,
    }
    if flow.contract:
        result["handoff_identifier"] = flow.contract.handoff_identifier
        result["contract_lifecycle"] = flow.contract.lifecycle
    if flow.run:
        result["execution_token"] = str(flow.run.token)
        result["execution_lifecycle"] = flow.run.lifecycle
    if flow.failure_detail:
        result["failure_detail"] = flow.failure_detail
    return result


def _transition(
    flow: ConversationOrchestration, caller: str, step: str, outcome: str
) -> None:
    """Persist a separately-auditable lifecycle transition for one flow."""
    flow.current_step = step
    flow.status = outcome
    flow.failure_detail = {}
    flow.save(update_fields=["current_step", "status", "failure_detail", "updated_at"])
    _audit(
        caller,
        "scope.confirm_and_execute",
        flow.scope.project,
        outcome,
        {"orchestration_token": str(flow.token), "step": step},
    )


def _advance_orchestration(flow: ConversationOrchestration, caller: str) -> None:
    """Resume only missing canonical transitions; never duplicate authority."""
    scope = ExecutableScope.objects.get(pk=flow.scope_id)
    root = Path(settings.BASE_DIR)
    try:
        if scope.status == ExecutableScope.Status.PROPOSED:
            bind_approval(scope, flow.confirmation_reference)
            _transition(flow, caller, "PUBLICATION", "APPROVED")
            scope.refresh_from_db()
        if scope.status != ExecutableScope.Status.APPROVED:
            raise ValueError("INVALID_SCOPE_STATE")
        if not scope.published_path:
            publish_scope(scope, root)
        _transition(flow, caller, "PREPARATION", "PUBLISHED")
        if flow.preparation_id is None:
            authorized = approved_scope(scope)
            flow.preparation = ExecutionPreparation.objects.create(
                project=scope.project,
                sprint_path=authorized["path"],
                preparation_data={
                    "scope_identifier": scope.identifier,
                    "approved_scope": authorized,
                    "intent": scope.record["intent"],
                    "resolved_policy": scope.record["policy"],
                    "missing_product_owner_inputs": [],
                },
            )
            flow.save(update_fields=["preparation", "updated_at"])
        _transition(flow, caller, "CONTRACT", "EXECUTION_PREPARED")
        if flow.contract_id is None:
            flow.contract = generate_scope_execution_contract(scope, root)
            flow.save(update_fields=["contract", "updated_at"])
            _transition(flow, caller, "CONTRACT_VALIDATION", "CONTRACT_GENERATED")
        contract = flow.contract
        if contract is None:
            raise ValueError("CONTRACT_GENERATION_REQUIRED")
        if contract.lifecycle == ExecutionContract.Lifecycle.DRAFT:
            validate_execution_contract(contract, root)
            _transition(flow, caller, "CONTRACT_ISSUANCE", "CONTRACT_VALIDATED")
        if contract.lifecycle == ExecutionContract.Lifecycle.VALIDATED:
            issue_execution_contract(contract, root)
            _transition(flow, caller, "CONTRACT_CONSUMPTION", "CONTRACT_ISSUED")
        if contract.lifecycle == ExecutionContract.Lifecycle.ISSUED:
            contract = consume_execution_contract(
                contract,
                root,
                expected_hash=contract.contract_hash,
                provider_identity=contract.payload["provider_policy"][
                    "selected_provider_identity"
                ],
                observed_baseline=contract.payload["execution"]["baseline_commit"],
                schema_version="2.0",
                idempotency_key=f"conversation:{flow.token}",
            )
            _transition(flow, caller, "EXECUTION", "CONTRACT_CONSUMED")
        if contract.lifecycle not in {
            ExecutionContract.Lifecycle.CONSUMED,
            ExecutionContract.Lifecycle.RUNNING,
            ExecutionContract.Lifecycle.COMPLETED,
        }:
            raise ValueError("CONTRACT_LIFECYCLE_NOT_EXECUTABLE")
        _transition(flow, caller, "EXECUTION", "CONTRACT_CONSUMED")
        persisted_run = flow.run if flow.run_id is not None else None
        if (
            persisted_run is not None
            and persisted_run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
        ):
            flow.run = None
            flow.save(update_fields=["run", "updated_at"])
        if flow.run_id is None:
            request, _ = ExecutionStartRequest.objects.get_or_create(
                contract=contract,
                defaults={
                    "approval": GovernanceApproval.objects.get(
                        reference=flow.confirmation_reference, project=scope.project
                    )
                },
            )
            audit = McpAuditEvent.objects.create(
                caller=caller,
                tool_name="scope.confirm_and_execute",
                project=scope.project,
                outcome="DISPATCHING",
                details={
                    "orchestration_token": str(flow.token),
                    "contract": contract.handoff_identifier,
                },
            )
            try:
                flow.run = start_run(
                    contract,
                    request,
                    project_repository_root(scope.project, root),
                    audit_event_id=audit.pk,
                )
            except (OSError, ValueError):
                flow.run = ExecutionRun.objects.filter(contract=contract).first()
                if flow.run is not None:
                    flow.save(update_fields=["run", "updated_at"])
                raise
            request.status = "EXECUTION_STARTED"
            request.next_action = "Provider result must be verified before completion."
            request.save(update_fields=["status", "next_action"])
            flow.save(update_fields=["run", "updated_at"])
        _transition(flow, caller, "EXECUTION", "EXECUTION_STARTED")
    except (OSError, ValueError) as exc:
        flow.status = "BLOCKED"
        flow.failure_detail = {"code": str(exc), "resume_available": True}
        flow.save(update_fields=["status", "failure_detail", "updated_at"])
        _audit(
            caller,
            "scope.confirm_and_execute",
            scope.project,
            "BLOCKED",
            {"orchestration_token": str(flow.token), "code": str(exc)[:200]},
        )


def _confirm_and_execute(
    arguments: dict[str, Any], project: Project, caller: str
) -> dict[str, Any]:
    """One durable orchestration, composed exclusively from canonical services."""
    scope = ExecutableScope.objects.get(
        project=project, identifier=arguments["scope_identifier"]
    )
    review = review_scope(scope)
    existing = ConversationOrchestration.objects.filter(
        scope=scope, confirmation_reference=arguments["confirmation_reference"]
    ).first()
    if existing:
        if (
            existing.proposal_hash != arguments["proposal_hash"]
            or existing.proposal_version != arguments["proposal_version"]
            or existing.product_owner_identity != arguments["product_owner_identity"]
        ):
            raise ValueError("CONFIRMATION_REFERENCE_REUSE_MISMATCH")
        _advance_orchestration(existing, caller)
        return _orchestration_result(existing)
    if not review["confirmation_eligible"]:
        raise ValueError("CLARIFICATION_REQUIRED")
    if (
        review["proposal_hash"] != arguments["proposal_hash"]
        or review["proposal_version"] != arguments["proposal_version"]
    ):
        raise ValueError("STALE_PROPOSAL_VERSION")
    approval, created = GovernanceApproval.objects.get_or_create(
        reference=arguments["confirmation_reference"],
        defaults={
            "project": project,
            "scope": scope,
            "approved_action": "AUTHORIZE_EXECUTION",
            "approved_by": arguments["product_owner_identity"],
        },
    )
    if not created and (
        approval.project_id != project.pk
        or approval.approved_by != arguments["product_owner_identity"]
        or approval.approved_action not in {"AUTHORIZE_EXECUTION", "ALL"}
    ):
        raise ValueError("CONFIRMATION_REFERENCE_REUSE_MISMATCH")
    flow = ConversationOrchestration.objects.create(
        scope=scope,
        product_owner_identity=arguments["product_owner_identity"],
        confirmation_reference=arguments["confirmation_reference"],
        proposal_version=arguments["proposal_version"],
        proposal_hash=arguments["proposal_hash"],
    )
    _advance_orchestration(flow, caller)
    return _orchestration_result(flow)


def _normalise_confirmation(value: str) -> str:
    """Compare conversational confirmation without weakening its vocabulary."""
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents.casefold()).strip()


def _confirm_conversation(
    arguments: dict[str, Any], project: Project, caller: str
) -> dict[str, Any]:
    """Map an accepted Product Owner phrase to the exact displayed proposal."""
    if _normalise_confirmation(arguments["confirmation_text"]) not in (
        _PRODUCT_OWNER_CONFIRMATIONS
    ):
        raise ValueError("PRODUCT_OWNER_CONFIRMATION_REQUIRED")
    scope = ExecutableScope.objects.get(
        project=project, identifier=arguments["scope_identifier"]
    )
    review = review_scope(scope)
    if not review["confirmation_eligible"]:
        raise ValueError("CLARIFICATION_REQUIRED")
    return _confirm_and_execute(
        {
            **arguments,
            "proposal_version": review["proposal_version"],
            "proposal_hash": review["proposal_hash"],
        },
        project,
        caller,
    )


def _complete_orchestration(
    arguments: dict[str, Any], project: Project, caller: str
) -> dict[str, Any]:
    """Accept completion after the real provider stops and evidence exists."""
    scope = ExecutableScope.objects.get(
        project=project, identifier=arguments["scope_identifier"]
    )
    flow = ConversationOrchestration.objects.get(
        scope=scope, token=arguments["orchestration_token"]
    )
    if flow.status == "COMPLETED":
        return _orchestration_result(flow)
    if flow.run_id is None or flow.contract_id is None:
        raise ValueError("EXECUTION_NOT_STARTED")
    run = flow.run
    contract = flow.contract
    if run is None or contract is None:
        raise ValueError("EXECUTION_NOT_STARTED")
    if provider(run.provider_name).status(run.provider_execution_id) != "FINISHED":
        raise ValueError("EXECUTION_STILL_RUNNING")
    completion_data = arguments["completion_data"]
    required = {
        "execution_result",
        "gate_results",
        "evidence_manifest",
        "changed_files",
        "failure_classification",
    }
    if required - set(completion_data):
        raise ValueError("RUN_COMPLETION_EVIDENCE_REQUIRED")
    gates = completion_data["gate_results"]
    if not isinstance(gates, dict) or not gates or set(gates.values()) != {"PASS"}:
        raise ValueError("RELEASE_GATES_NOT_PASSED")
    if not completion_data["changed_files"]:
        raise ValueError("EXECUTION_CHANGED_FILES_REQUIRED")
    root = project_repository_root(project, Path(settings.BASE_DIR))
    manifest = completion_data["evidence_manifest"]
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("RUN_COMPLETION_EVIDENCE_INVALID")
    if not all(
        isinstance(path, str) and (root / path).is_file() for path in manifest.values()
    ):
        raise ValueError("EVIDENCE_MANIFEST_MISSING")
    complete_run(run, arguments["final_commit_sha"], completion_data)
    complete_execution_contract(
        contract,
        arguments["final_commit_sha"],
        "PASS — READY FOR PRODUCT OWNER REVIEW",
        completion_data,
    )
    flow.status = "COMPLETED"
    flow.current_step = "COMPLETED"
    flow.failure_detail = {}
    flow.save(update_fields=["status", "current_step", "failure_detail", "updated_at"])
    _audit(
        caller,
        "scope.complete_execution",
        project,
        "COMPLETED",
        {
            "orchestration_token": str(flow.token),
            "final_commit": arguments["final_commit_sha"],
        },
    )
    result = _orchestration_result(flow)
    result.update(
        {
            "completion_message": "Főnök, kész!",
            "evidence": manifest,
            "test_instructions": (
                "Review the changed files and rerun the recorded Release Gates."
            ),
        }
    )
    return result


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
    _validate_arguments(schema, arguments)
    if name == "conversation.confirm":
        arguments = _derived_conversation_confirmation(arguments, caller)
    replay = _idempotent(caller, name, arguments)
    if replay is not None:
        if name == "conversation.confirm":
            replay_project = _project(arguments)
            flow = ConversationOrchestration.objects.filter(
                scope__project=replay_project,
                confirmation_reference=arguments["confirmation_reference"],
            ).first()
            if flow is not None and flow.status == "BLOCKED":
                _advance_orchestration(flow, caller)
                resumed = _orchestration_result(flow)
                McpIdempotencyRecord.objects.filter(
                    caller=caller,
                    tool_name=name,
                    key=arguments["idempotency_key"],
                ).update(result=resumed)
                return {**resumed, "idempotent_replay": True, "resumed": True}
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
        elif name == "provider.list":
            result = {
                "providers": [
                    public_provider(item)
                    for item in ExecutionProvider.objects.order_by(
                        "priority", "provider_id"
                    )
                ]
            }
        elif name == "provider.get":
            result = public_provider(
                ExecutionProvider.objects.get(provider_id=arguments["provider_id"])
            )
        elif name == "provider.capabilities":
            item = ExecutionProvider.objects.get(provider_id=arguments["provider_id"])
            result = {
                "provider_id": item.provider_id,
                "capabilities": item.capabilities,
            }
        elif name == "provider.health":
            item = ExecutionProvider.objects.get(provider_id=arguments["provider_id"])
            result = {
                "provider_id": item.provider_id,
                "health": public_provider(item)["health"],
                "last_health_at": public_provider(item)["last_health_at"],
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
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            authorized = approved_scope(scope)
            result = invoke_operation(
                "scope.get",
                {
                    "scope_identifier": scope.identifier,
                },
                Path(settings.BASE_DIR),
            )
            result["approved_scope"] = authorized
        elif name == "scope.review":
            assert project is not None
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            review = review_scope(scope)
            result = {
                "status": "PROPOSAL_REVIEW",
                "project_id": project.project_id,
                "scope_identifier": scope.identifier,
                "proposal_review": review,
                "next_tool": (
                    "conversation.confirm" if review["confirmation_eligible"] else None
                ),
                "required_user_input": (
                    ["confirmation_text"] if review["confirmation_eligible"] else []
                ),
            }
        elif name == "scope.answer_clarifications":
            assert project is not None
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            updated = answer_clarifications(scope, arguments["answers"])
            result = {
                "status": "SCOPE_REVISED",
                "proposal_review": review_scope(updated),
            }
        elif name == "scope.confirm_and_execute":
            assert project is not None
            result = _confirm_and_execute(arguments, project, caller)
        elif name == "conversation.confirm":
            assert project is not None
            result = _confirm_conversation(arguments, project, caller)
        elif name == "scope.orchestration_status":
            assert project is not None
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            flow = (
                ConversationOrchestration.objects.filter(scope=scope)
                .order_by("-created_at")
                .first()
            )
            result = (
                _orchestration_result(flow)
                if flow
                else {
                    "status": "NO_CONFIRMATION_RECORDED",
                    "scope_identifier": scope.identifier,
                }
            )
        elif name == "scope.complete_execution":
            assert project is not None
            result = _complete_orchestration(arguments, project, caller)
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
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            authorized = approved_scope(scope)
            preparation_data = {
                "scope_identifier": scope.identifier,
                "approved_scope": authorized,
                "intent": scope.record["intent"],
                "resolved_policy": scope.record["policy"],
                "missing_product_owner_inputs": [],
            }
            prep = ExecutionPreparation.objects.create(
                project=project,
                sprint_path=authorized["path"],
                preparation_data=preparation_data,
            )
            result = {
                "status": "EXECUTION_PREPARED",
                "preparation_token": str(prep.token),
                "approved_scope": authorized,
                "resolved_policy": scope.record["policy"],
                "missing_product_owner_inputs": [],
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
            approval = _approval_for_contract(
                arguments, contract, "execution.request_start"
            )
            req = ExecutionStartRequest.objects.create(
                contract=contract, approval=approval
            )
            dispatch_audit = McpAuditEvent.objects.create(
                caller=caller,
                tool_name=name,
                project=contract.project,
                outcome="DISPATCHING",
                details={"handoff_identifier": contract.handoff_identifier},
            )
            run = start_run(
                contract,
                req,
                project_repository_root(contract.project, Path(settings.BASE_DIR)),
                audit_event_id=dispatch_audit.pk,
            )
            req.status = "EXECUTION_STARTED"
            req.next_action = (
                "Monitor the execution run through execution.get_run_status."
            )
            req.save(update_fields=["status", "next_action"])
            result = {
                "status": req.status,
                "request_id": req.pk,
                "next_action": req.next_action,
                "execution_token": str(run.token),
                "provider": run.provider_name,
            }
        elif name in {
            "execution.get_run_status",
            "execution.list_events",
            "execution.evidence_summary",
            "execution.cancel",
        }:
            run = ExecutionRun.objects.get(token=arguments["execution_token"])
            if name == "execution.cancel":
                approval = _approval_for_contract(
                    arguments, run.contract, "execution.cancel"
                )
                if run.lifecycle not in {
                    ExecutionRun.Lifecycle.RUNNING,
                    ExecutionRun.Lifecycle.STARTING,
                }:
                    raise ValueError("EXECUTION_NOT_CANCELLABLE")
                provider(run.provider_name).cancel(run.provider_execution_id)
                run.lifecycle = ExecutionRun.Lifecycle.CANCELLED
                run.current_phase = "CANCELLED"
                run.save(update_fields=["lifecycle", "current_phase", "updated_at"])
                add_event(run, "EXECUTION_CANCELLED", approval=approval.reference)
                result = {"status": "CANCELLED", "execution_token": str(run.token)}
            elif name == "execution.list_events":
                result = {
                    "execution_token": str(run.token),
                    "events": [
                        {
                            "sequence": event.sequence,
                            "type": event.event_type,
                            "details": event.details,
                            "created_at": event.created_at.isoformat(),
                        }
                        for event in ExecutionProgressEvent.objects.filter(run=run)[
                            :100
                        ]
                    ],
                }
            elif name == "execution.evidence_summary":
                result = {
                    "execution_token": str(run.token),
                    "evidence_root": run.evidence_root,
                    "final_commit_sha": run.final_commit_sha,
                    "terminal_state": run.terminal_state,
                    "contract_hash": run.contract_hash,
                }
            else:
                result = {
                    "execution_token": str(run.token),
                    "status": run.lifecycle,
                    "phase": run.current_phase,
                    "provider": run.provider_name,
                    "provider_execution_id": run.provider_execution_id,
                    "attempt_count": run.attempt_count,
                    "current_blocker": run.current_blocker,
                }
        elif name.startswith("scope.") or name in {
            "sprint.propose",
            "work_item.propose",
        }:
            operation = {
                "scope.classify": "scope.classify",
                "sprint.propose": "sprint.propose",
                "work_item.propose": "work_item.propose",
                "scope.validate": "scope.validate",
                "scope.approve": "scope.approve",
                "scope.publish": "scope.publish",
                "scope.get": "scope.get",
                "scope.review": "scope.review",
                "scope.answer_clarifications": "scope.answer_clarifications",
                "scope.confirm_and_execute": "scope.confirm_and_execute",
                "scope.orchestration_status": "scope.orchestration_status",
                "scope.contract.generate": "scope.contract.generate",
                "scope.complete": "scope.complete",
                "scope.cancel": "scope.cancel",
                "scope.supersede": "scope.supersede",
            }[name]
            if "scope_identifier" in arguments:
                scope = ExecutableScope.objects.get(
                    identifier=arguments["scope_identifier"]
                )
                project = scope.project
                if name in {"scope.complete", "scope.cancel", "scope.supersede"}:
                    approval = _approval(
                        arguments, project, f"scope.{name.split('.')[-1]}"
                    )
                    if approval.scope_id != scope.pk:
                        raise ValueError("APPROVAL_SCOPE_MISMATCH")
                    approved_scope(scope)
            result = invoke_operation(
                operation, dict(arguments), Path(settings.BASE_DIR)
            )
        elif name.startswith("contract."):
            action = name.split(".")[1]
            op = {
                "generate": "scope.contract.generate",
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
                if (
                    prep.preparation_data.get("scope_identifier")
                    != arguments["scope_identifier"]
                ):
                    raise ValueError("PREPARATION_SCOPE_MISMATCH")
                payload = {
                    "scope_identifier": arguments["scope_identifier"],
                }
            elif action == "complete":
                payload.update(
                    {
                        "final_commit_sha": arguments["final_commit_sha"],
                        "closure_state": arguments["closure_state"],
                        "completion_data": {
                            key: arguments[key]
                            for key in (
                                "execution_result",
                                "gate_results",
                                "evidence_manifest",
                                "changed_files",
                                "failure_classification",
                            )
                        },
                    }
                )
            elif action == "consume":
                payload.update(
                    {
                        key: arguments[key]
                        for key in (
                            "expected_contract_hash",
                            "provider_identity",
                            "observed_baseline",
                            "schema_version",
                            "idempotency_key",
                        )
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
                _approval_for_contract(arguments, contract, f"contract.{action}")
            if action == "complete":
                run = ExecutionRun.objects.get(
                    contract=contract, lifecycle=ExecutionRun.Lifecycle.RUNNING
                )
                complete_run(
                    run, payload["final_commit_sha"], payload["completion_data"]
                )
            result = invoke_operation(op, payload, Path(settings.BASE_DIR))
        else:
            raise ValueError("TOOL_NOT_IMPLEMENTED")
        _store_idempotent(caller, name, arguments, result)
        _audit(caller, name, project, "SUCCESS", {"status": result.get("status", "OK")})
        return result
    except Exception as exc:
        _audit(caller, name, project, "REJECTED", {"code": str(exc)[:200]})
        raise

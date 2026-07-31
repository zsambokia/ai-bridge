"""Governed public MCP tool registry; HTTP only adapts this canonical surface."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import uuid
from pathlib import Path
from typing import Any, cast

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .contract_policy import EXECUTION_LEVELS, RISK_MODIFIERS, TASK_TYPES
from .contracts import (
    _baseline_exists,
    complete_execution_contract,
    consume_execution_contract,
    generate_scope_execution_contract,
    issue_execution_contract,
    supersede_execution_contract,
    validate_execution_contract,
)
from .engineering_memory import (
    activate_candidate as activate_engineering_candidate,
)
from .engineering_memory import (
    impact as engineering_impact,
)
from .engineering_memory import (
    ingest_lifecycle_event,
    planning_assessment,
    revision_diff,
    revision_history,
)
from .engineering_memory import (
    link as link_engineering_entities,
)
from .engineering_memory import (
    search as engineering_search,
)
from .engineering_memory import (
    upsert_candidate as upsert_engineering_candidate,
)
from .execution import (
    ACTIVE_STATES,
    add_event,
    complete_run,
    confirm_execution_cancellation,
    enqueue_run,
    lifecycle_status_projection,
    prepare_execution_cancellation,
    provider,
    request_execution_cancellation,
    start_run,
)
from .execution_activity import activity_summary, events_for_view
from .knowledge import (
    build_and_record_context_package as akb_context_package,
)
from .knowledge import (
    create_or_upsert_candidate,
    entry_for_project,
    review_candidate,
)
from .knowledge import (
    search as akb_search,
)
from .mcp import invoke_operation
from .models import (
    ConversationOrchestration,
    EngineeringEntity,
    ExecutableScope,
    ExecutionContract,
    ExecutionPreparation,
    ExecutionProgressEvent,
    ExecutionProvider,
    ExecutionRun,
    ExecutionStartRequest,
    GovernanceApproval,
    KnowledgeContextPackage,
    KnowledgeEntry,
    McpAuditEvent,
    McpIdempotencyRecord,
    Project,
    RoadmapItem,
    RoadmapUpdateCandidate,
    RuntimeDeployment,
)
from .orchestration_gate import (
    assert_contract_authorized,
    bind_runtime,
    open_gate,
    trace_for_contract,
)
from .providers import public_provider
from .roadmap import create_item as create_roadmap_item
from .roadmap import propose_update as propose_roadmap_update
from .roadmap import review_update as review_roadmap_update
from .runtime_deployment import deployment_projection
from .scopes import (
    answer_clarifications,
    approved_scope,
    bind_approval,
    close_scope,
    publish_scope,
    review_scope,
)
from .services import _head_sha, project_repository_root

TOOL_SURFACE_VERSION = "2026-07-31.4"
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
_PRODUCT_OWNER_CONFIRMATION_PREFIXES = (
    "i approve",
    "i confirm",
    "i accept",
    "approve",
    "confirm",
    "accept",
    "jovahagyom",
    "megerositem",
    "elfogadom",
)
_PRODUCT_OWNER_CONFIRMATION_DISQUALIFIERS = {
    "cannot",
    "dont",
    "ha",
    "if",
    "kiveve",
    "nem",
    "never",
    "no",
    "not",
    "unless",
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
_AKB_ENTRY = {
    "entry_key": {"type": "string", "minLength": 1, "maxLength": 160},
    "scope": {"type": "string", "enum": ["PLATFORM", "PROJECT"]},
    "knowledge_type": {
        "type": "string",
        "enum": [
            "CONSTITUTION",
            "ROADMAP",
            "UI_PLAN",
            "SYSTEM_DESIGN",
            "INCIDENT_LESSON",
            "RUNBOOK",
            "POLICY",
            "ARCHITECTURE_DECISION",
            "GENERAL",
        ],
    },
    "title": {"type": "string", "minLength": 1, "maxLength": 255},
    "content": {"type": "string", "minLength": 1, "maxLength": 12000},
    "source_type": {"type": "string", "maxLength": 64},
    "source_reference": {"type": "string", "minLength": 1, "maxLength": 255},
    "evidence_references": {
        "type": "array",
        "maxItems": 20,
        "items": {"type": "string", "maxLength": 255},
    },
    "work_context_id": {"type": "string", "maxLength": 255},
    "role_context": {
        "type": "array",
        "maxItems": 10,
        "items": {"type": "string", "maxLength": 64},
    },
    "verification_status": {"type": "string", "maxLength": 32},
    "freshness_status": {"type": "string", "maxLength": 32},
    "knowledge_owner_role": {"type": "string", "maxLength": 64},
    "is_must_know": {"type": "boolean"},
    "source_version": {"type": "string", "maxLength": 128},
    "conflict_key": {"type": "string", "maxLength": 160},
    "precedence": {"type": "integer", "minimum": 0, "maximum": 65535},
}
_ENGINEERING_ENTITY = {
    "entity_key": {"type": "string", "minLength": 1, "maxLength": 160},
    "kind": {"type": "string", "enum": list(EngineeringEntity.Kind.values)},
    "name": {"type": "string", "minLength": 1, "maxLength": 255},
    "description": {"type": "string", "maxLength": 12000},
    "source_reference": {"type": "string", "minLength": 1, "maxLength": 255},
    "evidence_references": {
        "type": "array",
        "maxItems": 20,
        "items": {"type": "string", "maxLength": 255},
    },
    "attributes": {"type": "object"},
    "expected_version": {"type": "integer", "minimum": 1},
}


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
        "deployment.get_status",
        "Read the canonical SHA-bound runtime deployment receipt for a delivery.",
        READ_ONLY,
        {"delivery_id": {"type": "integer", "minimum": 1}},
        ["delivery_id"],
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
        "Search governed Platform and Project AKB entries with bounded "
        "metadata filters.",
        READ_ONLY,
        {
            **_PROJECT,
            "query": {"type": "string", "minLength": 1, "maxLength": 200},
            "limit": {"type": "integer", "minimum": 1, "maximum": 10},
            "scope": {"type": "string", "enum": ["PLATFORM", "PROJECT"]},
            "knowledge_type": {"type": "string", "maxLength": 64},
            "status": {"type": "string", "maxLength": 32},
            "verification_status": {"type": "string", "maxLength": 32},
            "freshness_status": {"type": "string", "maxLength": 32},
            "role_context": {"type": "string", "maxLength": 64},
            "work_context_id": {"type": "string", "maxLength": 255},
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
        "akb.get_entry",
        "Read one governed AKB entry in the caller's project context.",
        READ_ONLY,
        {**_PROJECT, "entry_id": {"type": "integer", "minimum": 1}},
        ["project_id", "entry_id"],
    ),
    _tool(
        "akb.get_context_package",
        "Build and persist the deterministic, auditable Orki AKB Context Package.",
        READ_ONLY,
        {
            **_PROJECT,
            "work_context_id": {"type": "string", "minLength": 1, "maxLength": 255},
            "role_context_id": {"type": "string", "maxLength": 64},
            "retrieval_intent": {"type": "string", "maxLength": 128},
            "retrieval_query": {"type": "string", "maxLength": 1000},
        },
        ["project_id", "work_context_id"],
    ),
    _tool(
        "akb.get_context_usage",
        "Read the persisted Context Package and its canonical consumption bindings.",
        READ_ONLY,
        {
            **_PROJECT,
            "package_hash": {"type": "string", "minLength": 64, "maxLength": 64},
        },
        ["project_id", "package_hash"],
    ),
    _tool(
        "roadmap.create_item",
        "Register a proposed project roadmap item; progression remains governed.",
        PREPARATORY_STATE,
        {
            **_PROJECT,
            "item_key": {"type": "string", "minLength": 1, "maxLength": 160},
            "title": {"type": "string", "minLength": 1, "maxLength": 255},
            "epic_reference": {"type": "string", "maxLength": 255},
            "sprint_reference": {"type": "string", "maxLength": 255},
            "dependencies": {
                "type": "array",
                "items": {"type": "string", "maxLength": 160},
            },
            **_IDEMPOTENCY,
        },
        ["project_id", "item_key", "title", "idempotency_key"],
    ),
    _tool(
        "roadmap.propose_update",
        "Record delivery evidence as a reviewable roadmap progress candidate.",
        PREPARATORY_STATE,
        {
            **_PROJECT,
            "item_key": {"type": "string", "minLength": 1, "maxLength": 160},
            "proposed_state": {
                "type": "string",
                "enum": list(RoadmapItem.State.values),
            },
            "engineering_status": {"type": "string", "maxLength": 16},
            "operational_status": {"type": "string", "maxLength": 16},
            "evidence_references": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "maxLength": 255},
            },
            "final_commit_sha": {"type": "string", "maxLength": 40},
            "source_reference": {"type": "string", "minLength": 1, "maxLength": 255},
            **_IDEMPOTENCY,
        },
        [
            "project_id",
            "item_key",
            "proposed_state",
            "evidence_references",
            "source_reference",
            "idempotency_key",
        ],
    ),
    _tool(
        "roadmap.review_update",
        "Approve or reject a roadmap progress candidate using a durable approval.",
        APPROVAL_REQUIRED,
        {
            **_PROJECT,
            "candidate_id": {"type": "integer", "minimum": 1},
            "decision": {"type": "string", "enum": ["APPROVE", "REJECT"]},
            **_APPROVAL,
            **_IDEMPOTENCY,
        },
        ["project_id", "candidate_id", "decision", "idempotency_key"],
    ),
    _tool(
        "roadmap.list",
        "Read canonical project-scoped roadmap items and governed update candidates.",
        READ_ONLY,
        _PROJECT,
        ["project_id"],
    ),
    _tool(
        "akb.create_candidate",
        "Create a governed AKB candidate; publication remains approval-controlled.",
        PREPARATORY_STATE,
        {**_PROJECT, **_AKB_ENTRY, **_IDEMPOTENCY},
        [
            "project_id",
            "entry_key",
            "scope",
            "knowledge_type",
            "title",
            "content",
            "source_reference",
            "idempotency_key",
        ],
    ),
    _tool(
        "akb.upsert_candidate",
        "Idempotently revise an existing AKB candidate without overwriting "
        "active knowledge.",
        PREPARATORY_STATE,
        {**_PROJECT, **_AKB_ENTRY, **_IDEMPOTENCY},
        [
            "project_id",
            "entry_key",
            "scope",
            "knowledge_type",
            "title",
            "content",
            "source_reference",
            "idempotency_key",
        ],
    ),
    _tool(
        "akb.review_candidate",
        "Submit review or approve a candidate with a durable approval reference.",
        APPROVAL_REQUIRED,
        {
            **_PROJECT,
            "entry_id": {"type": "integer", "minimum": 1},
            "decision": {
                "type": "string",
                "enum": ["REQUEST_REVIEW", "REJECT", "APPROVE"],
            },
            "approval_reference": {"type": "string", "minLength": 1, "maxLength": 128},
            **_IDEMPOTENCY,
        },
        ["project_id", "entry_id", "decision", "idempotency_key"],
    ),
    _tool(
        "akb.list_review_queue",
        "List candidate and review entries visible in one project context.",
        READ_ONLY,
        {**_PROJECT, "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
        ["project_id"],
    ),
    _tool(
        "engineering.search",
        (
            "Search active, project-isolated engineering-memory entities; role only "
            "affects ordering."
        ),
        READ_ONLY,
        {
            **_PROJECT,
            "query": {"type": "string", "maxLength": 200},
            "kinds": {
                "type": "array",
                "maxItems": 20,
                "items": {
                    "type": "string",
                    "enum": list(EngineeringEntity.Kind.values),
                },
            },
            "role_profile": {
                "type": "string",
                "enum": [
                    "PRODUCT",
                    "DEVELOPMENT",
                    "APPLICATION",
                    "SUPPORT",
                    "OPERATIONS",
                ],
            },
        },
        ["project_id"],
    ),
    _tool(
        "engineering.get_entity",
        "Get a project-isolated engineering-memory entity and its provenance.",
        READ_ONLY,
        {**_PROJECT, "entity_key": _ENGINEERING_ENTITY["entity_key"]},
        ["project_id", "entity_key"],
    ),
    _tool(
        "engineering.upsert_candidate",
        (
            "Create or version a reviewable engineering-memory candidate; it never "
            "activates knowledge."
        ),
        PREPARATORY_STATE,
        {**_PROJECT, **_ENGINEERING_ENTITY, **_IDEMPOTENCY},
        [
            "project_id",
            "entity_key",
            "kind",
            "name",
            "source_reference",
            "idempotency_key",
        ],
    ),
    _tool(
        "engineering.review_candidate",
        "Activate a candidate only with durable Product Owner approval.",
        APPROVAL_REQUIRED,
        {
            **_PROJECT,
            "entity_key": _ENGINEERING_ENTITY["entity_key"],
            **_APPROVAL,
            **_IDEMPOTENCY,
        },
        ["project_id", "entity_key", "approval_reference", "idempotency_key"],
    ),
    _tool(
        "engineering.link",
        "Create or update an evidenced typed relation within one project.",
        PREPARATORY_STATE,
        {
            **_PROJECT,
            "source_key": _ENGINEERING_ENTITY["entity_key"],
            "target_key": _ENGINEERING_ENTITY["entity_key"],
            "relationship_type": {"type": "string", "minLength": 1, "maxLength": 64},
            "work_reference": {"type": "string", "maxLength": 255},
            "evidence_references": _ENGINEERING_ENTITY["evidence_references"],
            **_IDEMPOTENCY,
        },
        [
            "project_id",
            "source_key",
            "target_key",
            "relationship_type",
            "idempotency_key",
        ],
    ),
    _tool(
        "engineering.impact",
        "Return one-hop, project-isolated impact relations for an engineering entity.",
        READ_ONLY,
        {**_PROJECT, "entity_key": _ENGINEERING_ENTITY["entity_key"]},
        ["project_id", "entity_key"],
    ),
    _tool(
        "engineering.history",
        (
            "Return append-only revision metadata for a project-isolated engineering "
            "entity."
        ),
        READ_ONLY,
        {**_PROJECT, "entity_key": _ENGINEERING_ENTITY["entity_key"]},
        ["project_id", "entity_key"],
    ),
    _tool(
        "engineering.plan",
        "Assess governed roadmap prerequisites, capability gaps, and GitHub conflicts.",
        READ_ONLY,
        _PROJECT,
        ["project_id"],
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
        (
            "List ordered, redacted events in Activity, Provider Output, or Raw "
            "Events view."
        ),
        READ_ONLY,
        {
            "execution_token": {"type": "string"},
            "view": {
                "type": "string",
                "enum": ["ACTIVITY", "PROVIDER_OUTPUT", "RAW_EVENTS"],
            },
            "after_sequence": {"type": "integer", "minimum": 0},
            "limit": {"type": "integer", "minimum": 1, "maximum": 500},
        },
        ["execution_token"],
    ),
    _tool(
        "execution.get_activity_summary",
        "Read the canonical live execution activity and derived checklist.",
        READ_ONLY,
        {"execution_token": {"type": "string"}},
        ["execution_token"],
    ),
    _tool(
        "governance.prepare_codex_handoff",
        (
            "Return a copyable, fully bound Codex handoff only when durable "
            "execution authority exists."
        ),
        READ_ONLY,
        {
            **_PROJECT,
            "scope_identifier": {"type": "string", "minLength": 1},
        },
        ["project_id", "scope_identifier"],
    ),
    _tool(
        "execution.prepare_cancel",
        "Prepare a durable Product Owner cancellation request.",
        PREPARATORY_STATE,
        {
            "execution_token": {"type": "string"},
            "reason": {"type": "string", "minLength": 1, "maxLength": 1000},
            **_IDEMPOTENCY,
        },
        ["execution_token", "reason", "idempotency_key"],
    ),
    _tool(
        "execution.confirm_cancel",
        "Confirm the exact durable execution cancellation request.",
        LIFECYCLE_MUTATION,
        {
            "execution_token": {"type": "string"},
            "confirmation_text": {"type": "string", "minLength": 1},
            **_IDEMPOTENCY,
        },
        ["execution_token", "confirmation_text", "idempotency_key"],
    ),
    _tool(
        "execution.cancel",
        "Execute a previously confirmed, durable cancellation request.",
        EXECUTION_BOUNDARY,
        {
            "execution_token": {"type": "string"},
            "reason": {"type": "string", "minLength": 1, "maxLength": 1000},
            "requested_by": {"type": "string", "minLength": 1, "maxLength": 255},
            "confirmation_reference": {
                "type": "string",
                "minLength": 1,
                "maxLength": 255,
            },
            **_IDEMPOTENCY,
        },
        [
            "execution_token",
            "reason",
            "requested_by",
            "confirmation_reference",
            "idempotency_key",
        ],
    ),
    _tool(
        "execution.evidence_summary",
        "Read final execution evidence binding metadata.",
        READ_ONLY,
        {"execution_token": {"type": "string"}},
        ["execution_token"],
    ),
]

# First-class MCP adapters keep the important planning/design objects discoverable
# while reusing the one governed engineering-memory authoring path.
_ENGINEERING_ADAPTERS = {
    "roadmap": "ROADMAP_ITEM",
    "constitution": "CONSTITUTION_SECTION",
    "ui_plan": "UI_PLAN",
    "system_design": "SYSTEM_DESIGN",
}
for _adapter, _kind in _ENGINEERING_ADAPTERS.items():
    _TOOLS.extend(
        [
            _tool(
                f"{_adapter}.search",
                (
                    f"Search active project-isolated {_adapter} engineering-memory "
                    "objects."
                ),
                READ_ONLY,
                {**_PROJECT, "query": {"type": "string", "maxLength": 200}},
                ["project_id"],
            ),
            _tool(
                f"{_adapter}.upsert_candidate",
                (
                    f"Create or revise a governed {_adapter} candidate; activation "
                    "remains approval-controlled."
                ),
                PREPARATORY_STATE,
                {**_PROJECT, **_ENGINEERING_ENTITY, **_IDEMPOTENCY},
                [
                    "project_id",
                    "entity_key",
                    "name",
                    "source_reference",
                    "idempotency_key",
                ],
            ),
        ]
    )

_TOOLS.append(
    _tool(
        "constitution.diff",
        "Compare two append-only Constitution section revisions.",
        READ_ONLY,
        {
            **_PROJECT,
            "entity_key": _ENGINEERING_ENTITY["entity_key"],
            "from_version": {"type": "integer", "minimum": 1},
            "to_version": {"type": "integer", "minimum": 1},
        },
        ["project_id", "entity_key", "from_version", "to_version"],
    )
)
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
                "retry key are derived by the governed service. Use an explicit "
                "unconditional confirmation, for example 'I approve the exact "
                "displayed proposal.'"
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
            "scope.resume",
            (
                "Read the durable recovery state for a scope after a client or "
                "MCP session interruption. This is read-only and returns the "
                "exact proposal version/hash required for a later confirmation."
            ),
            READ_ONLY,
            {**_PROJECT, "scope_identifier": {"type": "string", "minLength": 1}},
            ["project_id", "scope_identifier"],
        ),
        _tool(
            "scope.resume_confirm_and_execute",
            (
                "From a new authenticated session, confirm and resume exactly the "
                "version/hash returned by scope.resume. The caller supplies an "
                "affirmative Product Owner reply; Bridge derives the durable "
                "identity, approval reference, and idempotency key."
            ),
            EXECUTION_BOUNDARY,
            {
                **_PROJECT,
                "scope_identifier": {"type": "string", "minLength": 1},
                "proposal_version": {"type": "integer", "minimum": 1},
                "proposal_hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "confirmation_text": {"type": "string", "minLength": 1},
            },
            [
                "project_id",
                "scope_identifier",
                "proposal_version",
                "proposal_hash",
                "confirmation_text",
            ],
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
    if not _is_explicit_product_owner_confirmation(arguments["confirmation_text"]):
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


def _derived_recovery_confirmation(
    arguments: dict[str, Any], caller: str
) -> dict[str, Any]:
    """Bind an explicit recovery confirmation without relying on session state.

    Unlike ``conversation.confirm``, this path deliberately does not require a
    fresh proposal review: another authenticated Product Owner session may be
    resuming an already-approved scope.  The caller must instead echo the
    exact version and hash obtained from ``scope.resume``.
    """
    if not _is_explicit_product_owner_confirmation(arguments["confirmation_text"]):
        raise ValueError("PRODUCT_OWNER_CONFIRMATION_REQUIRED")
    caller_fingerprint = hashlib.sha256(caller.encode("utf-8")).hexdigest()
    product_owner_identity = f"authenticated-mcp-caller:{caller_fingerprint}"
    binding = {
        "caller": caller_fingerprint,
        "project_id": arguments["project_id"],
        "scope_identifier": arguments["scope_identifier"],
        "proposal_version": arguments["proposal_version"],
        "proposal_hash": arguments["proposal_hash"],
    }
    digest = hashlib.sha256(
        json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "product_owner_identity": product_owner_identity,
        "confirmation_reference": f"scope-resume-confirmation:v1:{digest}",
        "idempotency_key": f"scope-resume-confirm:v1:{digest}",
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


def _akb_audit_details(
    name: str, arguments: dict[str, Any], result: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Record AKB operation metadata without putting knowledge content in audit logs."""
    if not name.startswith(
        (
            "akb.",
            "engineering.",
            "roadmap.",
            "constitution.",
            "ui_plan.",
            "system_design.",
        )
    ):
        return {}
    details: dict[str, Any] = {
        "operation_type": name,
        "platform_context_id": "ai-bridge.platform.v1",
        "project_context_id": arguments.get("project_id", ""),
        "work_context_id": arguments.get("work_context_id", ""),
        "role_context": arguments.get(
            "role_context_id", arguments.get("role_context", "")
        ),
        "input_reference": arguments.get(
            "entry_key", arguments.get("entry_id", arguments.get("query", ""))
        ),
        "approval_reference": arguments.get("approval_reference", ""),
    }
    if result:
        details["modified_entry_ids"] = (
            [result["entry_id"]] if "entry_id" in result else []
        )
        details["modified_entity_keys"] = (
            [result["entity_key"]] if "entity_key" in result else []
        )
        details["context_package_hash"] = result.get("hash", "")
    return details


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


def _execution_run(execution_token: str) -> ExecutionRun:
    """Resolve a public execution token without leaking ORM failures to MCP."""
    try:
        token = uuid.UUID(execution_token)
    except (AttributeError, ValueError) as exc:
        raise ValueError("INVALID_EXECUTION_TOKEN") from exc
    try:
        return ExecutionRun.objects.get(token=token)
    except ExecutionRun.DoesNotExist as exc:
        raise ValueError("EXECUTION_NOT_FOUND") from exc


def _conflicting_execution_details(contract: ExecutionContract) -> dict[str, str]:
    """Expose the actionable token for a run that blocks this contract.

    The flow must not bind ``run`` to a run owned by another contract: doing so
    would make later completion operate on the wrong contract.  Instead, keep
    that ownership intact and return only the public token needed by the
    separately authorized ``execution.cancel`` operation.
    """
    branch = contract.payload.get("execution", {}).get("target_branch")
    if not isinstance(branch, str) or not branch:
        return {}
    conflicting_run = (
        ExecutionRun.objects.filter(
            contract__project=contract.project,
            branch=branch,
            lifecycle__in=ACTIVE_STATES,
        )
        .order_by("created_at", "pk")
        .first()
    )
    if conflicting_run is None:
        return {}
    return {
        "execution_token": str(conflicting_run.token),
        "execution_lifecycle": conflicting_run.lifecycle,
    }


def _orchestration_result(flow: ConversationOrchestration) -> dict[str, Any]:
    failure_detail = dict(flow.failure_detail or {})
    if (
        failure_detail.get("code") == "CONFLICTING_ACTIVE_EXECUTION"
        and not failure_detail.get("execution_token")
        and flow.contract is not None
    ):
        failure_detail.update(_conflicting_execution_details(flow.contract))

    result: dict[str, Any] = {
        "status": flow.status,
        "current_step": flow.current_step,
        "orchestration_token": str(flow.token),
        "scope_identifier": flow.scope.identifier,
        "scope_status": flow.scope.status,
        "proposal_version": flow.proposal_version,
        "proposal_hash": flow.proposal_hash,
    }
    if flow.contract:
        result["handoff_identifier"] = flow.contract.handoff_identifier
        result["contract_lifecycle"] = flow.contract.lifecycle
        if flow.contract.orchestration_session_id:
            result["orki"] = trace_for_contract(flow.contract)
    elif flow.orchestration_session is not None:
        result["orchestration_session_token"] = str(flow.orchestration_session.token)
    if flow.run:
        result["execution_token"] = str(flow.run.token)
        result["execution_lifecycle"] = flow.run.lifecycle
    if failure_detail:
        result["failure_detail"] = failure_detail
        # A conflict is owned by another contract, so it intentionally is not
        # ``flow.run``.  Promote its public token to the response shape used by
        # execution.cancel while retaining the ownership boundary above.
        if "execution_token" not in result and failure_detail.get("execution_token"):
            result["execution_token"] = failure_detail["execution_token"]
            result["execution_lifecycle"] = failure_detail.get(
                "execution_lifecycle", ""
            )
    return result


def _resume_result(scope: ExecutableScope) -> dict[str, Any]:
    """Render the session-independent recovery projection for one scope."""
    record = scope.record
    flow = (
        ConversationOrchestration.objects.filter(scope=scope)
        .order_by("-created_at")
        .first()
    )
    result: dict[str, Any] = {
        "scope": {
            "id": scope.identifier,
            "version": record["proposal_version"],
            "hash": record["proposal_hash"],
            "status": scope.status,
        },
        # Approval records are durable and deliberately have no implicit expiry.
        # A later revision, revocation, or final scope state is the authoritative
        # invalidation mechanism; clients must always submit this exact binding.
        "expires_at": None,
        "can_resume": scope.status
        in {
            ExecutableScope.Status.PROPOSED,
            ExecutableScope.Status.APPROVED,
        },
        "can_confirm": scope.status == ExecutableScope.Status.PROPOSED,
        "required_next_action": "scope.resume_confirm_and_execute",
    }
    if flow is None:
        result["status"] = "PENDING_APPROVAL"
        return result
    orchestration = _orchestration_result(flow)
    result["orchestration"] = orchestration
    if flow.status == "COMPLETED":
        result.update(
            {
                "status": "ALREADY_COMPLETED",
                "can_resume": False,
                "can_confirm": False,
                "required_next_action": "review_completion_evidence",
            }
        )
    elif flow.run_id is not None and flow.run and flow.run.lifecycle in ACTIVE_STATES:
        result.update(
            {
                "status": "ALREADY_EXECUTING",
                "can_confirm": False,
                "required_next_action": "poll_execution_status",
            }
        )
    else:
        result.update({"status": "RECOVERABLE", "can_confirm": True})
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


def _recover_incomplete_contract_binding(
    flow: ConversationOrchestration, root: Path
) -> None:
    """Replace only an exited, pre-fix contract that lacked scope authority.

    Older contracts named the Bridge-side projection but did not carry its
    contents.  A provider running in a separately registered workspace cannot
    verify that projection.  Once that provider has exited without a commit,
    superseding it is safe and retains the same conversation confirmation.
    """
    contract = flow.contract
    run = flow.run
    if (
        contract is None
        or run is None
        or contract.lifecycle != ExecutionContract.Lifecycle.RUNNING
        or "content" in contract.payload.get("approved_scope", {})
        or provider(run.provider_name).status(run.provider_execution_id) != "FINISHED"
    ):
        return
    workspace_root = project_repository_root(contract.project, root)
    if _head_sha(workspace_root) != contract.payload["execution"]["baseline_commit"]:
        raise ValueError("LEGACY_CONTRACT_RECOVERY_MUTATION_DETECTED")

    run.lifecycle = ExecutionRun.Lifecycle.FAILED_GOVERNANCE
    run.current_phase = "CONTRACT_BINDING_REPAIRED"
    run.current_blocker = {
        "category": "contract binding defect",
        "evidence": "Issued contract omitted approved scope content.",
    }
    run.ended_at = timezone.now()
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "current_blocker",
            "ended_at",
            "updated_at",
        ]
    )
    add_event(run, "CONTRACT_SUPERSEDED", reason="missing approved scope content")
    replacement = generate_scope_execution_contract(
        flow.scope, root, orchestration_session=flow.orchestration_session
    )
    supersede_execution_contract(
        contract,
        replacement,
        allow_running_binding_repair=True,
    )
    flow.contract = replacement
    flow.run = None
    flow.failure_detail = {}
    flow.save(update_fields=["contract", "run", "failure_detail", "updated_at"])


def _recover_pre_execution_baseline_binding(
    flow: ConversationOrchestration, root: Path
) -> None:
    """Replace a consumed contract whose baseline is absent from its target repo.

    A contract is immutable once issued.  The narrow exception here retains
    that property by superseding it with a new contract, and is safe only when
    workspace provisioning stopped before any provider was started.
    """
    contract = flow.contract
    run = flow.run
    if (
        contract is None
        or run is None
        or contract.lifecycle != ExecutionContract.Lifecycle.CONSUMED
        or run.lifecycle != ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT
        or run.current_phase != "WORKSPACE_FAILED"
        or run.provider_execution_id
    ):
        return
    workspace_root = project_repository_root(contract.project, root)
    baseline = contract.payload["execution"]["baseline_commit"]
    if _baseline_exists(workspace_root, baseline):
        return

    run.lifecycle = ExecutionRun.Lifecycle.FAILED_GOVERNANCE
    run.current_phase = "CONTRACT_BASELINE_REPAIRED"
    run.current_blocker = {
        "category": "contract binding defect",
        "evidence": (
            "Contract baseline is absent from the registered target repository."
        ),
    }
    run.ended_at = timezone.now()
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "current_blocker",
            "ended_at",
            "updated_at",
        ]
    )
    add_event(run, "CONTRACT_SUPERSEDED", reason="target baseline absent")
    replacement = generate_scope_execution_contract(
        flow.scope, root, orchestration_session=flow.orchestration_session
    )
    supersede_execution_contract(
        contract,
        replacement,
        allow_consumed_pre_execution_binding_repair=True,
    )
    flow.contract = replacement
    flow.run = None
    flow.failure_detail = {}
    flow.save(update_fields=["contract", "run", "failure_detail", "updated_at"])


def _provider_has_completed(run: ExecutionRun) -> bool:
    """Recognize a durable provider terminal event when PID probing is stale.

    A provider process identifier is only an observation. On Windows it can
    outlive the child process or be reused, while the activity projector has
    already persisted the provider's terminal ``turn.completed`` event. That
    event is generated by the provider stream itself and is the authoritative
    fallback for releasing the governed completion transition.
    """
    if provider(run.provider_name).status(run.provider_execution_id) == "FINISHED":
        return True
    return (
        ExecutionProgressEvent.objects.filter(
            run=run, event_type="PROVIDER_COMPLETED"
        ).exists()
        or ExecutionProgressEvent.objects.filter(
            run=run,
            event_type="PROVIDER_OUTPUT",
            details__activity_type="turn.completed",
        ).exists()
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
        if flow.orchestration_session_id is None:
            flow.orchestration_session = open_gate(flow, caller)
            flow.save(update_fields=["orchestration_session", "updated_at"])
        session = flow.orchestration_session
        if session is None:
            raise ValueError("ORCHESTRATION_GATE_REQUIRED")
        if session.decision.policy_decision != "ALLOW":
            raise ValueError("ORCHESTRATION_AUTHORITY_DENIED")
        _recover_incomplete_contract_binding(flow, root)
        _recover_pre_execution_baseline_binding(flow, root)
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
            flow.contract = generate_scope_execution_contract(
                scope, root, orchestration_session=session
            )
            bind_runtime(session, flow.contract)
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
        if persisted_run is not None and persisted_run.lifecycle in {
            ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
            ExecutionRun.Lifecycle.CANCELLED,
        }:
            # A cancelled provider no longer owns an active execution slot.  Keep
            # the same approved contract and conversation binding, but let a
            # durable recovery confirmation dispatch a replacement run.
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
                job = enqueue_run(contract, request, root, audit_event_id=audit.pk)
                flow.run = job.run
            except (OSError, ValueError):
                flow.run = ExecutionRun.objects.filter(contract=contract).first()
                if flow.run is not None:
                    flow.save(update_fields=["run", "updated_at"])
                raise
            request.status = "EXECUTION_QUEUED"
            request.next_action = "Independent worker must claim the durable job."
            request.save(update_fields=["status", "next_action"])
            flow.save(update_fields=["run", "updated_at"])
        _transition(flow, caller, "EXECUTION", "EXECUTION_QUEUED")
    except (OSError, ValueError) as exc:
        flow.status = "BLOCKED"
        failure_detail: dict[str, Any] = {
            "code": str(exc),
            "resume_available": True,
        }
        conflicting_contract = flow.contract
        if str(exc) == "CONFLICTING_ACTIVE_EXECUTION" and conflicting_contract:
            failure_detail.update(_conflicting_execution_details(conflicting_contract))
        flow.failure_detail = failure_detail
        flow.save(update_fields=["status", "failure_detail", "updated_at"])
        _audit(
            caller,
            "scope.confirm_and_execute",
            scope.project,
            "BLOCKED",
            {"orchestration_token": str(flow.token), "code": str(exc)[:200]},
        )


@transaction.atomic
def _confirm_and_execute(
    arguments: dict[str, Any], project: Project, caller: str
) -> dict[str, Any]:
    """One durable orchestration, composed exclusively from canonical services."""
    scope = ExecutableScope.objects.select_for_update().get(
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


@transaction.atomic
def _resume_confirm_and_execute(
    arguments: dict[str, Any], project: Project, caller: str
) -> dict[str, Any]:
    """Continue a reviewed scope after a lost client session.

    The explicit proposal binding makes the recovery request safe to replay in a
    fresh session.  We reuse the existing durable approval/orchestration record
    whenever one already exists; a retry never creates another contract or run.
    """
    if not _is_explicit_product_owner_confirmation(arguments["confirmation_text"]):
        raise ValueError("PRODUCT_OWNER_CONFIRMATION_REQUIRED")
    scope = ExecutableScope.objects.select_for_update().get(
        project=project, identifier=arguments["scope_identifier"]
    )
    record = scope.record
    if arguments["proposal_version"] != record["proposal_version"]:
        raise ValueError(
            "SCOPE_VERSION_MISMATCH: review the current proposal version "
            f"{record['proposal_version']}"
        )
    if arguments["proposal_hash"] != record["proposal_hash"]:
        raise ValueError("SCOPE_HASH_MISMATCH: review the current proposal hash")
    existing = (
        ConversationOrchestration.objects.filter(scope=scope)
        .order_by("created_at")
        .first()
    )
    if existing is not None:
        if (
            existing.proposal_version != arguments["proposal_version"]
            or existing.proposal_hash != arguments["proposal_hash"]
        ):
            raise ValueError("SCOPE_CONFIRMATION_SUPERSEDED")
        _audit(
            caller,
            "scope.resume_confirm_and_execute",
            project,
            "APPROVAL_REPLAYED",
            {
                "scope_identifier": scope.identifier,
                "orchestration_token": str(existing.token),
            },
        )
        _advance_orchestration(existing, caller)
        result = _orchestration_result(existing)
        return {**result, "resumed": True, "approval_replayed": True}
    result = _confirm_and_execute(
        {
            **arguments,
            "proposal_version": arguments["proposal_version"],
            "proposal_hash": arguments["proposal_hash"],
        },
        project,
        caller,
    )
    _audit(
        caller,
        "scope.resume_confirm_and_execute",
        project,
        "APPROVED",
        {
            "scope_identifier": scope.identifier,
            "orchestration_token": result["orchestration_token"],
        },
    )
    return {**result, "resumed": True, "approval_replayed": False}


def _normalise_confirmation(value: str) -> str:
    """Normalize a confirmation without retaining caller-controlled formatting."""
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents.casefold()).strip()


def _is_explicit_product_owner_confirmation(value: str) -> bool:
    """Accept an explicit, unconditional approval without guessing user intent.

    ChatGPT may faithfully forward a Product Owner's natural-language approval
    with its displayed scope, version, and hash.  The former exact-phrase
    allowlist rejected those confirmations before their caller-bound approval
    reference could be persisted.  The governed fields, not prose copied by a
    model, remain the authoritative scope binding; this predicate only decides
    whether the reply expresses an unambiguous affirmative intent.
    """
    # Check common English contractions before punctuation normalisation splits
    # them into separate harmless-looking words (for example, ``don't`` into
    # ``don t``).  A qualified or negative reply must never authorize work.
    folded = value.casefold()
    if re.search(r"\b(?:don't|dont|can't|cannot|won't|will not|do not)\b", folded):
        return False
    normalized = _normalise_confirmation(value)
    if normalized in _PRODUCT_OWNER_CONFIRMATIONS:
        return True
    words = set(normalized.split())
    if words.intersection(_PRODUCT_OWNER_CONFIRMATION_DISQUALIFIERS):
        return False
    return any(
        normalized == prefix or normalized.startswith(f"{prefix} ")
        for prefix in _PRODUCT_OWNER_CONFIRMATION_PREFIXES
    )


def _cancellation_requester(caller: str) -> str:
    """Bind cancellation attribution to the authenticated MCP caller."""
    digest = hashlib.sha256(caller.encode("utf-8")).hexdigest()
    return f"authenticated-mcp-caller:{digest}"


def _cancellation_confirmation_reference(run: ExecutionRun, caller: str) -> str:
    binding = {
        "execution_token": str(run.token),
        "requester": _cancellation_requester(caller),
        "reason": run.cancellation.reason,
    }
    digest = hashlib.sha256(
        json.dumps(binding, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"execution-cancellation-confirmation:v1:{digest}"


def _confirm_conversation(
    arguments: dict[str, Any], project: Project, caller: str
) -> dict[str, Any]:
    """Map an accepted Product Owner phrase to the exact displayed proposal."""
    if not _is_explicit_product_owner_confirmation(arguments["confirmation_text"]):
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
    if not _provider_has_completed(run):
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
    pass_closure_state = next(
        (
            state
            for state in contract.payload["allowed_terminal_states"]
            if state.startswith("PASS ")
        ),
        None,
    )
    if pass_closure_state is None:
        raise ValueError("PASS_CLOSURE_STATE_NOT_ALLOWED")
    # The original Product Owner approval authorizes this completed scope.  A
    # second approval for ``scope.complete`` would be both redundant and an
    # incorrect lifecycle boundary: all evidence has already been verified
    # above and no scope mutation is being proposed.  Keep every durable
    # terminal transition together so a failed contract/scope update cannot
    # leave a successful execution looking actionable.
    with transaction.atomic():
        if run.lifecycle == ExecutionRun.Lifecycle.RUNNING:
            complete_run(run, arguments["final_commit_sha"], completion_data)
        elif (
            run.lifecycle != ExecutionRun.Lifecycle.COMPLETED
            or run.final_commit_sha != arguments["final_commit_sha"]
            or run.completion_data != completion_data
        ):
            raise ValueError("RUN_COMPLETION_NOT_RECOVERABLE")
        complete_execution_contract(
            contract,
            arguments["final_commit_sha"],
            pass_closure_state,
            completion_data,
        )
        close_scope(scope, "COMPLETED")
        flow.status = "COMPLETED"
        flow.current_step = "COMPLETED"
        flow.failure_detail = {}
        flow.save(
            update_fields=["status", "current_step", "failure_detail", "updated_at"]
        )
    ingest_lifecycle_event(
        project,
        event_type="SPRINT_COMPLETED",
        event_key=scope.identifier,
        source_reference=contract.handoff_identifier,
        evidence_references=list(manifest.values()),
        attributes={"final_commit_sha": arguments["final_commit_sha"]},
        actor=caller,
    )
    for gate, outcome in gates.items():
        ingest_lifecycle_event(
            project,
            event_type="GATE_RESULT",
            event_key=f"{scope.identifier}:{gate}",
            source_reference=contract.handoff_identifier,
            evidence_references=list(manifest.values()),
            attributes={"outcome": outcome, "scope_identifier": scope.identifier},
            actor=caller,
        )
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
    # ``flow.scope`` may have been relation-cached before ``close_scope``.
    # Return the terminal status that was actually persisted above.
    flow.scope = scope
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


def _prepared_codex_handoff(scope: ExecutableScope) -> dict[str, Any]:
    """Render a handoff from durable authority only, never client-supplied hints."""
    contract = next(
        (
            candidate
            for candidate in ExecutionContract.objects.filter(project=scope.project)
            if candidate.payload.get("approved_scope", {}).get("identifier")
            == scope.identifier
        ),
        None,
    )
    if contract is None:
        return {
            "status": "HANDOFF_INCOMPLETE",
            "scope_identifier": scope.identifier,
            "missing_fields": ["execution_contract"],
        }
    run = ExecutionRun.objects.filter(contract=contract).order_by("-created_at").first()
    if run is None:
        return {
            "status": "HANDOFF_INCOMPLETE",
            "scope_identifier": scope.identifier,
            "contract_identifier": contract.handoff_identifier,
            "missing_fields": ["execution_run"],
        }
    payload = contract.payload
    execution = payload.get("execution", {})
    evidence = payload.get("evidence", {})
    required = {
        "project_id": payload.get("project", {}).get("id"),
        "repository": payload.get("project", {}).get("repository"),
        "sprint_document_path": payload.get("approved_scope", {}).get("path"),
        "proposal_version": scope.record.get("proposal_version"),
        "proposal_hash": scope.record.get("proposal_hash"),
        "product_owner_approval_reference": payload.get("approval_reference"),
        "contract_identifier": contract.handoff_identifier,
        "contract_hash": contract.contract_hash,
        "execution_token": str(run.token),
        "baseline_commit_sha": execution.get("baseline_commit"),
        "target_branch": execution.get("target_branch"),
        "evidence_root": evidence.get("root"),
    }
    missing = sorted(key for key, value in required.items() if not value)
    if missing:
        return {
            "status": "HANDOFF_INCOMPLETE",
            "scope_identifier": scope.identifier,
            "missing_fields": missing,
        }
    release_gates = payload.get("policy", {}).get("required_release_gates", [])
    evidence_artifacts = payload.get("policy", {}).get(
        "required_evidence_artifacts", []
    )
    handoff = {
        "status": "HANDOFF_READY",
        "scope_identifier": scope.identifier,
        **required,
        "release_gates": release_gates,
        "required_evidence_artifacts": evidence_artifacts,
        "execution_status": run.lifecycle,
    }
    handoff["codex_prompt"] = "\n".join(
        (
            "Execute only the following already-consumed AI Bridge contract.",
            f"Scope identifier: {scope.identifier}",
            "Proposal version/hash: "
            f"{scope.record.get('proposal_version')} / "
            f"{scope.record.get('proposal_hash')}",
            f"Product Owner approval: {payload['approval_reference']}",
            "Contract identifier/hash: "
            f"{contract.handoff_identifier} / {contract.contract_hash}",
            f"Execution token: {run.token}",
            "Repository/branch/baseline: "
            f"{required['repository']} / {execution['target_branch']} / "
            f"{execution['baseline_commit']}",
            f"Release gates: {', '.join(release_gates)}",
            f"Evidence root: {evidence['root']}",
            f"Required evidence: {', '.join(evidence_artifacts)}",
            (
                "Preserve unrelated worktree changes. Record final evidence "
                "before requesting closure."
            ),
        )
    )
    return handoff


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
    elif name == "scope.resume_confirm_and_execute":
        arguments = {
            **arguments,
            **_derived_recovery_confirmation(arguments, caller),
        }
    replay = _idempotent(caller, name, arguments)
    if replay is not None:
        if name in {"conversation.confirm", "scope.resume_confirm_and_execute"}:
            replay_project = _project(arguments)
            flow = ConversationOrchestration.objects.filter(
                scope__project=replay_project,
                confirmation_reference=arguments["confirmation_reference"],
            ).first()
            if flow is not None and flow.status in {"BLOCKED", "EXECUTION_STARTED"}:
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
        elif name == "deployment.get_status":
            result = deployment_projection(
                RuntimeDeployment.objects.select_related("delivery").get(
                    delivery_id=arguments["delivery_id"]
                )
            )
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
        elif name == "governance.prepare_codex_handoff":
            assert project is not None
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            result = _prepared_codex_handoff(scope)
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
        elif name == "scope.resume":
            assert project is not None
            scope = ExecutableScope.objects.get(
                identifier=arguments["scope_identifier"], project=project
            )
            result = _resume_result(scope)
            _audit(
                caller,
                "scope.resume",
                project,
                "RECOVERY_STATE_RETRIEVED",
                {"scope_identifier": scope.identifier},
            )
        elif name == "scope.resume_confirm_and_execute":
            assert project is not None
            result = _resume_confirm_and_execute(arguments, project, caller)
        elif name == "scope.complete_execution":
            assert project is not None
            result = _complete_orchestration(arguments, project, caller)
        elif name == "akb.get_document":
            assert project is not None
            ident, content = _akb(project, arguments["document_id"])
            result = {"document_id": ident, "content": content}
        elif name == "akb.search":
            assert project is not None
            limit = arguments.get("limit", 10)
            hits = akb_search(
                project, arguments["query"], {**arguments, "limit": limit}
            )
            result = {
                "results": [
                    {**hit, "rank": index + 1} for index, hit in enumerate(hits)
                ],
                "result_limit": limit,
                "search_capability": "bounded metadata-filtered AKB text search",
            }
        elif name == "akb.get_entry":
            assert project is not None
            entry = entry_for_project(project, arguments["entry_id"])
            result = {
                "entry_id": entry.pk,
                "entry_key": entry.entry_key,
                "title": entry.title,
                "content": entry.content,
                "scope": entry.scope,
                "knowledge_type": entry.knowledge_type,
                "status": entry.status,
                "version": entry.version,
                "source_reference": entry.source_reference,
                "evidence_references": entry.evidence_references,
            }
        elif name == "akb.get_context_package":
            assert project is not None
            result = akb_context_package(
                project,
                arguments["work_context_id"],
                arguments.get("role_context_id", ""),
                retrieval_intent=arguments.get(
                    "retrieval_intent", "mcp-context-request"
                ),
                retrieval_query=arguments.get("retrieval_query", ""),
            )
        elif name == "akb.get_context_usage":
            assert project is not None
            package = KnowledgeContextPackage.objects.get(
                project=project, package_hash=arguments["package_hash"]
            )
            result = {
                "package_id": package.pk,
                "package_hash": package.package_hash,
                "entry_ids": package.entry_ids,
                "source_versions": package.source_versions,
                "stale_warnings": package.stale_warnings,
                "conflict_warnings": package.conflict_warnings,
                "uses": [
                    {
                        "session_token": str(use.session.token)
                        if use.session
                        else None,
                        "decision_id": use.decision_id,
                        "contract_id": use.execution_contract_id,
                        "run_id": use.execution_run_id,
                    }
                    for use in package.uses.select_related("session").all()
                ],
            }
        elif name == "roadmap.create_item":
            assert project is not None
            roadmap_item = create_roadmap_item(project, arguments)
            result = {
                "item_id": roadmap_item.pk,
                "item_key": roadmap_item.item_key,
                "state": roadmap_item.state,
            }
        elif name == "roadmap.propose_update":
            assert project is not None
            candidate = propose_roadmap_update(
                project, arguments["item_key"], arguments
            )
            result = {
                "candidate_id": candidate.pk,
                "status": candidate.status,
                "item_key": candidate.item.item_key,
            }
        elif name == "roadmap.review_update":
            assert project is not None
            candidate = review_roadmap_update(
                project,
                arguments["candidate_id"],
                arguments["decision"],
                caller,
                arguments.get("approval_reference", ""),
            )
            result = {
                "candidate_id": candidate.pk,
                "status": candidate.status,
                "item_key": candidate.item.item_key,
            }
        elif name == "roadmap.list":
            assert project is not None
            result = {
                "items": [
                    {
                        "item_key": item.item_key,
                        "title": item.title,
                        "state": item.state,
                        "engineering_status": item.engineering_status,
                        "operational_status": item.operational_status,
                        "final_commit_sha": item.final_commit_sha,
                        "evidence_references": item.evidence_references,
                    }
                    for item in RoadmapItem.objects.filter(project=project).order_by(
                        "item_key"
                    )
                ],
                "update_candidates": [
                    {
                        "candidate_id": item.pk,
                        "item_key": item.item.item_key,
                        "status": item.status,
                    }
                    for item in RoadmapUpdateCandidate.objects.filter(
                        item__project=project
                    )
                    .select_related("item")
                    .order_by("pk")
                ],
            }
        elif name in {"akb.create_candidate", "akb.upsert_candidate"}:
            assert project is not None
            entry = create_or_upsert_candidate(
                project, arguments, caller, upsert=name == "akb.upsert_candidate"
            )
            result = {
                "status": entry.status,
                "entry_id": entry.pk,
                "entry_key": entry.entry_key,
                "version": entry.version,
                "next_allowed_action": "akb.review_candidate",
            }
        elif name == "akb.review_candidate":
            assert project is not None
            entry = review_candidate(
                project,
                arguments["entry_id"],
                arguments["decision"],
                caller,
                arguments.get("approval_reference", ""),
            )
            result = {
                "status": entry.status,
                "entry_id": entry.pk,
                "version": entry.version,
                "approval_reference": entry.approval_reference,
            }
        elif name == "akb.list_review_queue":
            assert project is not None
            queue = KnowledgeEntry.objects.filter(
                project__in=[None, project],
                status__in=[
                    KnowledgeEntry.Status.CANDIDATE,
                    KnowledgeEntry.Status.IN_REVIEW,
                    KnowledgeEntry.Status.REJECTED,
                ],
            ).order_by("created_at")[: arguments.get("limit", 20)]
            result = {
                "entries": [
                    {
                        "entry_id": item.pk,
                        "entry_key": item.entry_key,
                        "title": item.title,
                        "status": item.status,
                        "knowledge_type": item.knowledge_type,
                        "scope": item.scope,
                    }
                    for item in queue
                ]
            }
        elif name == "engineering.search":
            assert project is not None
            entities = engineering_search(
                project,
                query=arguments.get("query", ""),
                kinds=arguments.get("kinds"),
                role_profile=arguments.get("role_profile"),
            )
            result = {
                "results": [
                    {
                        "entity_key": item.entity_key,
                        "kind": item.kind,
                        "name": item.name,
                        "state": item.state,
                        "version": item.version,
                    }
                    for item in entities
                ],
                "role_profile": arguments.get("role_profile", ""),
            }
        elif name == "engineering.get_entity":
            assert project is not None
            entity_item = EngineeringEntity.objects.get(
                project=project, entity_key=arguments["entity_key"]
            )
            result = {
                "entity_key": entity_item.entity_key,
                "kind": entity_item.kind,
                "name": entity_item.name,
                "state": entity_item.state,
                "description": entity_item.description,
                "attributes": entity_item.attributes,
                "evidence_references": entity_item.evidence_references,
                "source_reference": entity_item.source_reference,
                "version": entity_item.version,
                "approval_reference": entity_item.approval_reference,
            }
        elif name == "engineering.upsert_candidate":
            assert project is not None
            entity_item = upsert_engineering_candidate(
                project, arguments, actor=caller, upsert=True
            )
            result = {
                "entity_key": entity_item.entity_key,
                "state": entity_item.state,
                "version": entity_item.version,
                "next_allowed_action": "engineering.review_candidate",
            }
        elif name == "engineering.review_candidate":
            assert project is not None
            approval = _approval(arguments, project, "engineering.review_candidate")
            entity_item = activate_engineering_candidate(
                project,
                arguments["entity_key"],
                approval_reference=approval.reference,
                actor=caller,
            )
            result = {
                "entity_key": entity_item.entity_key,
                "state": entity_item.state,
                "version": entity_item.version,
                "approval_reference": entity_item.approval_reference,
            }
        elif name == "engineering.link":
            assert project is not None
            relation = link_engineering_entities(
                project,
                source_key=arguments["source_key"],
                target_key=arguments["target_key"],
                relationship_type=arguments["relationship_type"],
                evidence_references=arguments.get("evidence_references", []),
                work_reference=arguments.get("work_reference", ""),
            )
            result = {
                "relationship_id": relation.pk,
                "source_key": relation.source.entity_key,
                "target_key": relation.target.entity_key,
                "relationship_type": relation.relationship_type,
            }
        elif name == "engineering.impact":
            assert project is not None
            graph = engineering_impact(project, arguments["entity_key"])
            result = {
                "entity_key": graph["entity"].entity_key,
                "affected_keys": graph["affected_keys"],
                "relations": [
                    {
                        "source_key": item.source.entity_key,
                        "target_key": item.target.entity_key,
                        "relationship_type": item.relationship_type,
                    }
                    for item in graph["relations"]
                ],
            }
        elif name == "engineering.history":
            assert project is not None
            result = {
                "entity_key": arguments["entity_key"],
                "revisions": [
                    {
                        "version": revision.new_version,
                        "previous_version": revision.previous_version,
                        "source_reference": revision.source_reference,
                        "approval_reference": revision.approval_reference,
                        "reason": revision.reason,
                        "created_at": revision.created_at.isoformat(),
                    }
                    for revision in revision_history(project, arguments["entity_key"])
                ],
            }
        elif name == "engineering.plan":
            assert project is not None
            result = cast(dict[str, object], planning_assessment(project))
        elif name == "constitution.diff":
            assert project is not None
            entity_item = EngineeringEntity.objects.get(
                project=project, entity_key=arguments["entity_key"]
            )
            if entity_item.kind != "CONSTITUTION_SECTION":
                raise ValueError("CONSTITUTION_SECTION_REQUIRED")
            result = revision_diff(
                project,
                arguments["entity_key"],
                from_version=arguments["from_version"],
                to_version=arguments["to_version"],
            )
        elif name in {f"{adapter}.search" for adapter in _ENGINEERING_ADAPTERS}:
            assert project is not None
            adapter = name.split(".", 1)[0]
            entities = engineering_search(
                project,
                query=arguments.get("query", ""),
                kinds=[_ENGINEERING_ADAPTERS[adapter]],
            )
            result = {
                "results": [
                    {
                        "entity_key": item.entity_key,
                        "name": item.name,
                        "state": item.state,
                        "version": item.version,
                    }
                    for item in entities
                ]
            }
        elif name in {
            f"{adapter}.upsert_candidate" for adapter in _ENGINEERING_ADAPTERS
        }:
            assert project is not None
            adapter = name.split(".", 1)[0]
            entity_item = upsert_engineering_candidate(
                project,
                {**arguments, "kind": _ENGINEERING_ADAPTERS[adapter]},
                actor=caller,
                upsert=True,
            )
            result = {
                "entity_key": entity_item.entity_key,
                "state": entity_item.state,
                "version": entity_item.version,
                "next_allowed_action": "engineering.review_candidate",
            }
        elif name in {"scope.contract.generate", "contract.generate"}:
            # A bare contract has no actor/request/ownership chain.  The normal
            # public route is conversation.confirm -> Orki -> contract.
            raise ValueError("ORCHESTRATION_GATE_REQUIRED")
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
            assert_contract_authorized(contract)
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
                Path(settings.BASE_DIR),
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
            "execution.get_activity_summary",
            "execution.evidence_summary",
            "execution.prepare_cancel",
            "execution.confirm_cancel",
            "execution.cancel",
        }:
            run = _execution_run(arguments["execution_token"])
            if name == "execution.prepare_cancel":
                cancellation = prepare_execution_cancellation(
                    run,
                    requested_by=_cancellation_requester(caller),
                    reason=arguments["reason"],
                )
                result = {
                    "status": cancellation.status,
                    "execution_token": str(run.token),
                    "cancellation_token": str(cancellation.token),
                    "confirmation_required": True,
                    "next_tool": "execution.confirm_cancel",
                }
            elif name == "execution.confirm_cancel":
                if not _is_explicit_product_owner_confirmation(
                    arguments["confirmation_text"]
                ):
                    raise ValueError("PRODUCT_OWNER_CONFIRMATION_REQUIRED")
                requester = _cancellation_requester(caller)
                confirmation_reference = _cancellation_confirmation_reference(
                    run, caller
                )
                cancellation = confirm_execution_cancellation(
                    run,
                    requested_by=requester,
                    confirmation_reference=confirmation_reference,
                )
                result = {
                    "status": cancellation.status,
                    "execution_token": str(run.token),
                    "reason": cancellation.reason,
                    "requested_by": requester,
                    "confirmation_reference": confirmation_reference,
                    "next_tool": "execution.cancel",
                }
            elif name == "execution.cancel":
                if arguments["requested_by"] != _cancellation_requester(caller):
                    raise ValueError("CANCELLATION_REQUESTER_MISMATCH")
                cancelled, status = request_execution_cancellation(
                    run,
                    requested_by=arguments["requested_by"],
                    reason=arguments["reason"],
                    confirmation_reference=arguments["confirmation_reference"],
                )
                result = {
                    "status": status,
                    "execution_token": str(cancelled.token),
                    "lifecycle": cancelled.lifecycle,
                }
            elif name == "execution.list_events":
                view = str(arguments.get("view", "ACTIVITY"))
                if view not in {"ACTIVITY", "PROVIDER_OUTPUT", "RAW_EVENTS"}:
                    raise ValueError("EXECUTION_EVENT_VIEW_INVALID")
                result = {
                    "execution_token": str(run.token),
                    "view": view,
                    "events": events_for_view(
                        run,
                        view,
                        after_sequence=int(arguments.get("after_sequence", 0)),
                        limit=min(int(arguments.get("limit", 100)), 500),
                    ),
                }
            elif name == "execution.get_activity_summary":
                result = activity_summary(run)
            elif name == "execution.evidence_summary":
                result = {
                    "execution_token": str(run.token),
                    "evidence_root": run.evidence_root,
                    "final_commit_sha": run.final_commit_sha,
                    "terminal_state": run.terminal_state,
                    "contract_hash": run.contract_hash,
                }
            else:
                result = lifecycle_status_projection(run)
                if run.contract.orchestration_session_id:
                    result["orchestration"] = trace_for_contract(run.contract)
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
        _audit(
            caller,
            name,
            project,
            "SUCCESS",
            {
                "status": result.get("status", "OK"),
                **_akb_audit_details(name, arguments, result),
            },
        )
        return result
    except Exception as exc:
        _audit(
            caller,
            name,
            project,
            "REJECTED",
            {"code": str(exc)[:200], **_akb_audit_details(name, arguments)},
        )
        raise

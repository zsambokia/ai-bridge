"""Canonical executable-scope authority and deterministic publication."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from django.db import transaction
from django.utils import timezone

from .contract_policy import resolve_policy
from .models import ExecutableScope, GovernanceApproval, Project

SCOPE_SCHEMA = "ai-bridge-scope/v1"
SPRINT_SCHEMA = "ai-bridge-sprint/v1"
WORK_ITEM_SCHEMA = "ai-bridge-work-item/v1"
FINAL_STATUSES = {"COMPLETED", "CANCELLED", "SUPERSEDED"}


def canonical_hash(record: dict[str, Any]) -> str:
    value = {key: value for key, value in record.items() if key != "content_hash"}
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _proposal_hash(record: dict[str, Any]) -> str:
    """Hash the reviewable proposal, excluding lifecycle-derived fields."""
    excluded = {
        "content_hash",
        "proposal_hash",
        "status",
        "execution_authorization",
        "approval_reference",
        "updated_at",
        "clarification_answers",
    }
    value = {key: value for key, value in record.items() if key not in excluded}
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def clarification_questions(request: str) -> list[str]:
    """Return bounded questions only when the requested outcome is materially vague."""
    normalized = request.strip().lower().rstrip(".")
    if normalized == "add the new customer feature to the application":
        return [
            "What customer outcome must the feature deliver?",
            "Which application area and acceptance checks define the requested change?",
        ]
    return []


def classify_request(
    request: str,
    *,
    requested_kind: str | None = None,
    proposed_task_type: str | None = None,
) -> dict[str, str]:
    """Validate a structured semantic proposal without inferring from keywords.

    An LLM (or another client) may supply the natural-language intent and its
    proposed classification.  Bridge validates that proposal and resolves the
    policy later; it never represents a local keyword heuristic as semantics.
    """
    text = request.strip()
    if not text:
        raise ValueError("REQUEST_REQUIRED")
    kind = (requested_kind or "WORK_ITEM").upper()
    if kind not in {"SPRINT", "WORK_ITEM"}:
        raise ValueError("SCOPE_KIND_INVALID")
    task_type = (proposed_task_type or "FEATURE").upper()
    if task_type not in {
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
    }:
        raise ValueError("TASK_TYPE_INVALID")
    return {"kind": kind, "task_type": task_type, "intent": text}


def _identifier(project: Project, kind: str) -> str:
    prefix = "sprint" if kind == "SPRINT" else "work-item"
    return f"bridge:{project.project_id}:{prefix}:{uuid4()}"


def propose_scope(
    project: Project,
    request: str,
    *,
    kind: str | None = None,
    title: str | None = None,
    task_type: str | None = None,
    execution_level: str = "TASK",
    risk_modifiers: list[str] | None = None,
) -> ExecutableScope:
    classified = classify_request(
        request, requested_kind=kind, proposed_task_type=task_type
    )
    scope_kind = classified["kind"]
    level = "SPRINT" if scope_kind == "SPRINT" else execution_level.upper()
    policy = resolve_policy(
        level, (task_type or classified["task_type"]).upper(), risk_modifiers or []
    )
    identifier = _identifier(project, scope_kind)
    now = timezone.now().isoformat()
    record: dict[str, Any] = {
        "schema": SPRINT_SCHEMA if scope_kind == "SPRINT" else WORK_ITEM_SCHEMA,
        "schema_version": "1",
        "scope_kind": scope_kind,
        "identifier": identifier,
        "project_id": project.project_id,
        "title": title or request.strip().splitlines()[0][:160],
        "status": "PROPOSED",
        "execution_authorization": "NONE",
        "execution_level": level,
        "task_type": (task_type or classified["task_type"]).upper(),
        "intent": classified["intent"],
        "risk_modifiers": sorted({item.upper() for item in risk_modifiers or []}),
        "policy": policy,
        "approval_reference": "",
        "created_by": "AI_BRIDGE",
        "created_at": now,
        "updated_at": now,
        "proposal_version": 1,
        "clarification_questions": clarification_questions(classified["intent"]),
        "clarification_state": "CLARIFICATION_REQUIRED"
        if clarification_questions(classified["intent"])
        else "READY_FOR_CONFIRMATION",
    }
    record["proposal_hash"] = _proposal_hash(record)
    record["content_hash"] = canonical_hash(record)
    return ExecutableScope.objects.create(
        identifier=identifier,
        project=project,
        kind=scope_kind,
        record=record,
        content_hash=record["content_hash"],
    )


def review_scope(scope: ExecutableScope) -> dict[str, Any]:
    """Render the exact, non-authorizing Product Owner review surface."""
    record = validate_scope_record(scope.record, scope.project)
    questions = record.get("clarification_questions", [])
    ready = not questions and scope.status == ExecutableScope.Status.PROPOSED
    return {
        "scope_identifier": scope.identifier,
        "proposal_version": record.get("proposal_version", scope.version),
        "proposal_hash": record.get("proposal_hash"),
        "title": record["title"],
        "status": scope.status,
        "execution_authorization": record["execution_authorization"],
        "requested_outcome": record["intent"],
        "in_scope": [record["intent"]],
        "out_of_scope": ["Any change not expressed in the approved scope."],
        "acceptance_checks": record["policy"]["required_release_gates"],
        "release_gates": record["policy"]["required_release_gates"],
        "risks": record["risk_modifiers"],
        "policy_result": record["policy"],
        "clarification_state": record.get("clarification_state"),
        "clarification_questions": questions,
        "confirmation_eligible": ready,
        "confirmation_prompt": "Jó lesz így?" if ready else "",
    }


def answer_clarifications(
    scope: ExecutableScope, answers: dict[str, str]
) -> ExecutableScope:
    """Create a revised pending proposal; earlier versions can never be confirmed."""
    if scope.status != ExecutableScope.Status.PROPOSED:
        raise ValueError("SCOPE_NOT_REVISIONABLE")
    questions = scope.record.get("clarification_questions", [])
    if not questions:
        raise ValueError("CLARIFICATION_NOT_REQUIRED")
    if set(answers) != {str(index + 1) for index in range(len(questions))}:
        raise ValueError("CLARIFICATION_ANSWERS_INCOMPLETE")
    if any(not value.strip() for value in answers.values()):
        raise ValueError("CLARIFICATION_ANSWERS_INCOMPLETE")
    record = dict(scope.record)
    record["clarification_questions"] = []
    record["clarification_state"] = "READY_FOR_CONFIRMATION"
    record["clarification_answers"] = answers
    record["proposal_version"] = int(record.get("proposal_version", scope.version)) + 1
    record["updated_at"] = timezone.now().isoformat()
    record["proposal_hash"] = _proposal_hash(record)
    record["content_hash"] = canonical_hash(record)
    scope.version += 1
    scope.record = record
    scope.content_hash = record["content_hash"]
    scope.save(update_fields=["version", "record", "content_hash", "updated_at"])
    return scope


def validate_scope_record(
    record: dict[str, Any], project: Project | None = None
) -> dict[str, Any]:
    # The JSON Schema files are the source of truth.  This small runtime
    # evaluator deliberately consumes their declarations instead of duplicating
    # their required/const/enum rules in Python.
    schema_name = (
        "ai-bridge-sprint-v1.schema.json"
        if record.get("scope_kind") == "SPRINT"
        else "ai-bridge-work-item-v1.schema.json"
    )
    schema_path = Path(__file__).resolve().parents[1] / "docs" / "schemas" / schema_name
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("SCOPE_SCHEMA_UNAVAILABLE") from exc
    required = set(schema["required"])
    missing = sorted(required - set(record))
    if missing:
        raise ValueError("SCOPE_SCHEMA_INVALID:MISSING_" + ",".join(missing))
    if record["schema"] not in {SPRINT_SCHEMA, WORK_ITEM_SCHEMA}:
        raise ValueError("SCOPE_SCHEMA_INVALID:SCHEMA")
    kind = record["scope_kind"]
    if kind not in {"SPRINT", "WORK_ITEM"} or (kind == "SPRINT") != (
        record["schema"] == SPRINT_SCHEMA
    ):
        raise ValueError("SCOPE_SCHEMA_INVALID:KIND")
    for key, rule in schema.get("properties", {}).items():
        if key in record and "const" in rule and record[key] != rule["const"]:
            raise ValueError(f"SCOPE_SCHEMA_INVALID:{key.upper()}")
        if key in record and "enum" in rule and record[key] not in rule["enum"]:
            raise ValueError(f"SCOPE_SCHEMA_INVALID:{key.upper()}")
        if key not in record:
            continue
        value = record[key]
        expected_type = rule.get("type")
        type_matches = {
            "string": isinstance(value, str),
            "array": isinstance(value, list),
            "object": isinstance(value, dict),
        }
        if expected_type and not type_matches.get(expected_type, True):
            raise ValueError(f"SCOPE_SCHEMA_INVALID:{key.upper()}")
        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                raise ValueError(f"SCOPE_SCHEMA_INVALID:{key.upper()}")
            if len(value) > rule.get("maxLength", float("inf")):
                raise ValueError(f"SCOPE_SCHEMA_INVALID:{key.upper()}")
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None:
                raise ValueError(f"SCOPE_SCHEMA_INVALID:{key.upper()}")
    if record["status"] not in {choice for choice, _ in ExecutableScope.Status.choices}:
        raise ValueError("SCOPE_SCHEMA_INVALID:STATUS")
    if record["execution_authorization"] not in {"NONE", "APPROVED_PROVIDER_EXECUTION"}:
        raise ValueError("SCOPE_SCHEMA_INVALID:AUTHORIZATION")
    if record["created_by"] != "AI_BRIDGE":
        raise ValueError("SCOPE_SCHEMA_INVALID:AUTHORITY")
    if project and record["project_id"] != project.project_id:
        raise ValueError("PROJECT_SCOPE_MISMATCH")
    declared = record.get("content_hash")
    if declared and declared != canonical_hash(record):
        raise ValueError("SCOPE_CONTENT_HASH_MISMATCH")
    return record


def bind_approval(scope: ExecutableScope, reference: str) -> ExecutableScope:
    caller_scope = scope
    with transaction.atomic():
        scope = ExecutableScope.objects.select_for_update().get(pk=scope.pk)
        if scope.status in FINAL_STATUSES:
            raise ValueError("CLOSED_SCOPE_IMMUTABLE")
        if scope.status != ExecutableScope.Status.PROPOSED:
            raise ValueError("SCOPE_NOT_PENDING_CONFIRMATION")
        if scope.record.get("clarification_questions"):
            raise ValueError("CLARIFICATION_REQUIRED")
        try:
            approval = GovernanceApproval.objects.select_for_update().get(
                reference=reference, project=scope.project, revoked_at__isnull=True
            )
        except GovernanceApproval.DoesNotExist as exc:
            raise ValueError("APPROVAL_REQUIRED") from exc
        if approval.approved_action not in {"AUTHORIZE_EXECUTION", "ALL"}:
            raise ValueError("APPROVAL_ACTION_INVALID")
        if approval.scope_id not in {None, scope.pk}:
            raise ValueError("APPROVAL_SCOPE_MISMATCH")
        record = dict(scope.record)
        record.update(
            {
                "status": "APPROVED",
                "execution_authorization": "APPROVED_PROVIDER_EXECUTION",
                "approval_reference": reference,
                "updated_at": timezone.now().isoformat(),
            }
        )
        record["content_hash"] = canonical_hash(record)
        approval.scope = scope
        approval.save(update_fields=["scope"])
        scope.status = "APPROVED"
        scope.approval_reference = reference
        scope.record = record
        scope.content_hash = record["content_hash"]
        scope.save(
            update_fields=[
                "status",
                "approval_reference",
                "record",
                "content_hash",
                "updated_at",
            ]
        )
    # Preserve the useful service convention that callers may continue using
    # the instance they supplied, while the transaction itself used a locked
    # fresh row for authority checks.
    caller_scope.refresh_from_db()
    return caller_scope


def render_scope(scope: ExecutableScope) -> str:
    record = validate_scope_record(scope.record, scope.project)
    frontmatter = yaml.safe_dump(record, sort_keys=True, allow_unicode=True).strip()
    return (
        f"---\n{frontmatter}\n---\n\n# {record['title']}\n\n"
        f"## Intent\n\n{record['intent']}\n"
    )


def parse_scope_document(text: str, project: Project | None = None) -> dict[str, Any]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError("SCOPE_DOCUMENT_NOT_CANONICAL")
    try:
        record = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValueError("SCOPE_SCHEMA_INVALID:YAML") from exc
    if not isinstance(record, dict):
        raise ValueError("SCOPE_SCHEMA_INVALID:ROOT")
    return validate_scope_record(record, project)


def publish_scope(scope: ExecutableScope, root: Path) -> ExecutableScope:
    if scope.status in FINAL_STATUSES:
        raise ValueError("CLOSED_SCOPE_IMMUTABLE")
    validate_scope_record(scope.record, scope.project)
    if scope.status != ExecutableScope.Status.APPROVED:
        raise ValueError("SCOPE_NOT_APPROVED")
    folder = "sprints" if scope.kind == "SPRINT" else "work-items"
    safe = (
        re.sub(r"[^a-z0-9]+", "-", scope.record["title"].lower()).strip("-") or "scope"
    )
    path = (
        Path("docs") / folder / f"{scope.identifier.rsplit(':', 1)[-1]}-{safe[:48]}.md"
    )
    target = root / path
    if target.exists() and target.read_text(encoding="utf-8") != render_scope(scope):
        raise ValueError("SCOPE_PUBLICATION_COLLISION")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_scope(scope), encoding="utf-8")
    scope.published_path = path.as_posix()
    scope.save(update_fields=["published_path", "updated_at"])
    return scope


def approved_scope(scope: ExecutableScope) -> dict[str, Any]:
    validate_scope_record(scope.record, scope.project)
    if scope.status in FINAL_STATUSES:
        raise ValueError("CLOSED_SCOPE_IMMUTABLE")
    if (
        scope.status != "APPROVED"
        or not scope.approval_reference
        or not scope.published_path
    ):
        raise ValueError("SCOPE_NOT_APPROVED")
    try:
        approval = GovernanceApproval.objects.get(
            reference=scope.approval_reference,
            project=scope.project,
            scope=scope,
            revoked_at__isnull=True,
        )
    except GovernanceApproval.DoesNotExist as exc:
        raise ValueError("APPROVAL_BINDING_INVALID") from exc
    if approval.approved_action not in {"AUTHORIZE_EXECUTION", "ALL"}:
        raise ValueError("APPROVAL_ACTION_INVALID")
    return {
        "identifier": scope.identifier,
        "path": scope.published_path,
        "version": scope.version,
        "status": scope.status,
        "approval_reference": scope.approval_reference,
        "content_hash": scope.content_hash,
    }


def close_scope(scope: ExecutableScope, status: str) -> ExecutableScope:
    """Terminal scope transitions are explicit and prohibit future execution."""
    if status not in FINAL_STATUSES:
        raise ValueError("SCOPE_TERMINAL_STATUS_INVALID")
    if scope.status in FINAL_STATUSES:
        raise ValueError("CLOSED_SCOPE_IMMUTABLE")
    record = dict(scope.record)
    record.update(
        {
            "status": status,
            "execution_authorization": "NONE",
            "updated_at": timezone.now().isoformat(),
        }
    )
    record["content_hash"] = canonical_hash(record)
    scope.status, scope.record, scope.content_hash = (
        status,
        record,
        record["content_hash"],
    )
    scope.save(update_fields=["status", "record", "content_hash", "updated_at"])
    return scope

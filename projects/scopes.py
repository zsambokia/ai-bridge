"""Canonical executable-scope authority and deterministic publication."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
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


def classify_request(
    request: str, *, requested_kind: str | None = None
) -> dict[str, str]:
    """Deterministic classification; an LLM may supply text but not authority."""
    text = request.strip()
    if not text:
        raise ValueError("REQUEST_REQUIRED")
    kind = (
        requested_kind
        or ("SPRINT" if re.search(r"\bsprint\b", text, re.I) else "WORK_ITEM")
    ).upper()
    if kind not in {"SPRINT", "WORK_ITEM"}:
        raise ValueError("SCOPE_KIND_INVALID")
    task_type = (
        "BUGFIX" if re.search(r"\b(fix|bug|repair)\b", text, re.I) else "FEATURE"
    )
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
    classified = classify_request(request, requested_kind=kind)
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
    }
    record["content_hash"] = canonical_hash(record)
    return ExecutableScope.objects.create(
        identifier=identifier,
        project=project,
        kind=scope_kind,
        record=record,
        content_hash=record["content_hash"],
    )


def validate_scope_record(
    record: dict[str, Any], project: Project | None = None
) -> dict[str, Any]:
    required = {
        "schema",
        "scope_kind",
        "identifier",
        "project_id",
        "title",
        "status",
        "execution_authorization",
        "execution_level",
        "task_type",
        "intent",
        "policy",
        "created_by",
    }
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
    if scope.status in FINAL_STATUSES:
        raise ValueError("CLOSED_SCOPE_IMMUTABLE")
    try:
        approval = GovernanceApproval.objects.get(
            reference=reference, project=scope.project, revoked_at__isnull=True
        )
    except GovernanceApproval.DoesNotExist as exc:
        raise ValueError("APPROVAL_REFERENCE_INVALID") from exc
    if approval.approved_action not in {"AUTHORIZE_EXECUTION", "ALL"}:
        raise ValueError("APPROVAL_ACTION_INVALID")
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
    return scope


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
    if scope.status != "APPROVED" or not scope.approval_reference:
        raise ValueError("SCOPE_NOT_APPROVED")
    return {
        "identifier": scope.identifier,
        "path": scope.published_path,
        "version": scope.version,
        "status": scope.status,
        "approval_reference": scope.approval_reference,
        "content_hash": scope.content_hash,
    }

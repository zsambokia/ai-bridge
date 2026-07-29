"""Bounded, auditable technical remediation for an existing execution run."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import yaml
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import (
    ExecutableScope,
    ExecutionRun,
    McpAuditEvent,
    TechnicalRemediationLoop,
)
from .scopes import canonical_hash, propose_scope, render_scope


def classify_blocker(classification: str) -> str:
    """Validate an explicit classifier result; never infer business semantics."""
    if classification not in TechnicalRemediationLoop.Classification.values:
        raise ValueError("BLOCKER_CLASSIFICATION_INVALID")
    return classification


def _parent_scope(run: ExecutionRun) -> ExecutableScope:
    declared = run.contract.payload.get("approved_scope", {})
    identifier = declared.get("identifier")
    if run.contract.payload.get("schema_version") != "2.0" or not identifier:
        raise ValueError("PARENT_SCOPE_BINDING_REQUIRED")
    try:
        return ExecutableScope.objects.get(
            identifier=identifier, project=run.contract.project
        )
    except ExecutableScope.DoesNotExist as exc:
        raise ValueError("PARENT_SCOPE_BINDING_REQUIRED") from exc


def _event(loop: TechnicalRemediationLoop, event: str, **details: object) -> None:
    loop.timeline = [
        *loop.timeline,
        {"at": timezone.now().isoformat(), "event": event, "details": details},
    ][-30:]


@transaction.atomic
def open_technical_remediation(
    *,
    parent_run: ExecutionRun,
    classification: str,
    gate_name: str,
    summary: str,
    policy_basis: str,
    evidence_references: list[str],
    idempotency_key: str,
) -> TechnicalRemediationLoop:
    """Create one child work item only for an in-scope technical blocker."""
    classification = classify_blocker(classification)
    if classification != TechnicalRemediationLoop.Classification.TECHNICAL_REMEDIATION:
        raise ValueError("BLOCKER_REQUIRES_ESCALATION")
    if (
        not all(
            isinstance(value, str) and value.strip()
            for value in (gate_name, summary, policy_basis, idempotency_key)
        )
        or not evidence_references
    ):
        raise ValueError("TECHNICAL_REMEDIATION_INPUT_REQUIRED")
    parent_run = ExecutionRun.objects.select_for_update().get(pk=parent_run.pk)
    parent_scope = _parent_scope(parent_run)
    existing = TechnicalRemediationLoop.objects.filter(
        idempotency_key=idempotency_key
    ).first()
    if existing is not None:
        if (
            existing.parent_run_id != parent_run.pk
            or existing.classification != classification
            or existing.gate_name != gate_name
            or existing.policy_basis != policy_basis
            or existing.evidence_references != evidence_references
        ):
            raise ValueError("TECHNICAL_REMEDIATION_IDEMPOTENCY_MISMATCH")
        return existing
    child = propose_scope(
        parent_scope.project,
        summary,
        kind="WORK_ITEM",
        title=f"Technical remediation: {gate_name}",
        task_type="BUGFIX",
        work_type="BUGFIX",
        execution_level="TASK",
    )
    child_record = dict(child.record)
    child_record["parent_execution"] = {
        "run_token": str(parent_run.token),
        "parent_scope": parent_scope.identifier,
        "policy_basis": policy_basis[:1000],
        "gate_name": gate_name[:128],
    }
    child_record["content_hash"] = canonical_hash(child_record)
    child.record = child_record
    child.content_hash = child_record["content_hash"]
    child.save(update_fields=["record", "content_hash", "updated_at"])
    try:
        loop = TechnicalRemediationLoop.objects.create(
            parent_run=parent_run,
            parent_scope=parent_scope,
            remediation_scope=child,
            idempotency_key=idempotency_key,
            classification=classification,
            gate_name=gate_name[:128],
            policy_basis=policy_basis[:1000],
            evidence_references=evidence_references,
            status=TechnicalRemediationLoop.Status.REMEDIATING,
        )
    except IntegrityError as exc:
        raise ValueError("TECHNICAL_REMEDIATION_IDEMPOTENCY_MISMATCH") from exc
    _event(loop, "CHILD_WORK_ITEM_CREATED", child_scope=child.identifier)
    loop.save(update_fields=["timeline", "updated_at"])
    parent_run.lifecycle = ExecutionRun.Lifecycle.REPAIRING
    parent_run.current_phase = "TECHNICAL_REMEDIATION"
    parent_run.current_blocker = {
        "classification": classification,
        "gate_name": gate_name[:128],
        "remediation_scope": child.identifier,
    }
    parent_run.save(
        update_fields=["lifecycle", "current_phase", "current_blocker", "updated_at"]
    )
    McpAuditEvent.objects.create(
        caller="orchestrator-remediation-loop",
        tool_name="execution.open_technical_remediation",
        project=parent_scope.project,
        outcome="REMEDIATING",
        details={
            "parent_scope": parent_scope.identifier,
            "child_scope": child.identifier,
            "run_token": str(parent_run.token),
            "gate_name": gate_name[:128],
        },
    )
    return loop


def repair_published_scope_hash(scope: ExecutableScope, repository_root: Path) -> None:
    """Restore the deterministic projection of an unchanged canonical record."""
    if not scope.published_path:
        raise ValueError("PUBLISHED_SCOPE_REQUIRED")
    root = repository_root.resolve()
    target = (root / scope.published_path).resolve()
    if root not in target.parents:
        raise ValueError("SCOPE_PUBLICATION_PATH_INVALID")
    # Read the front matter without content-hash validation: that validation
    # is the very failed gate this bounded repair is allowed to correct.
    match = re.match(
        r"\A---\s*\n(.*?)\n---\s*\n", target.read_text(encoding="utf-8"), re.DOTALL
    )
    if match is None:
        raise ValueError("SCOPE_DOCUMENT_NOT_CANONICAL")
    parsed = yaml.safe_load(match.group(1))
    if not isinstance(parsed, dict):
        raise ValueError("SCOPE_SCHEMA_INVALID:ROOT")
    if parsed.get("identifier") != scope.identifier:
        raise ValueError("PUBLISHED_SCOPE_IDENTITY_MISMATCH")
    target.write_text(render_scope(scope), encoding="utf-8")


@transaction.atomic
def complete_technical_remediation(
    loop: TechnicalRemediationLoop,
    *,
    repair: Callable[[], None],
    rerun_gate: Callable[[], bool],
    evidence_references: list[str],
) -> TechnicalRemediationLoop:
    """Run a bounded repair and resume the same parent only after its gate passes."""
    loop = (
        TechnicalRemediationLoop.objects.select_for_update()
        .select_related("parent_run")
        .get(pk=loop.pk)
    )
    if loop.status == TechnicalRemediationLoop.Status.RESUMED:
        return loop
    if loop.status != TechnicalRemediationLoop.Status.REMEDIATING:
        raise ValueError("TECHNICAL_REMEDIATION_NOT_ACTIVE")
    if not evidence_references or not all(
        isinstance(value, str) and value.strip() for value in evidence_references
    ):
        raise ValueError("TECHNICAL_REMEDIATION_EVIDENCE_REQUIRED")
    try:
        repair()
        gate_passed = rerun_gate()
    except Exception as exc:
        loop.status = TechnicalRemediationLoop.Status.FAILED
        _event(loop, "REPAIR_FAILED", reason=str(exc)[:255])
        loop.save(update_fields=["status", "timeline", "updated_at"])
        raise
    if not gate_passed:
        loop.status = TechnicalRemediationLoop.Status.FAILED
        _event(loop, "GATE_RERUN_FAILED")
        loop.save(update_fields=["status", "timeline", "updated_at"])
        return loop
    loop.evidence_references = [*loop.evidence_references, *evidence_references]
    loop.status = TechnicalRemediationLoop.Status.RESUMED
    _event(loop, "GATE_RERUN_PASSED", evidence_references=evidence_references)
    loop.save(update_fields=["evidence_references", "status", "timeline", "updated_at"])
    run = loop.parent_run
    run.lifecycle = ExecutionRun.Lifecycle.RUNNING
    run.current_phase = "RESUMED_AFTER_TECHNICAL_REMEDIATION"
    run.current_blocker = {}
    run.gate_rerun_count += 1
    run.save(
        update_fields=[
            "lifecycle",
            "current_phase",
            "current_blocker",
            "gate_rerun_count",
            "updated_at",
        ]
    )
    McpAuditEvent.objects.create(
        caller="orchestrator-remediation-loop",
        tool_name="execution.complete_technical_remediation",
        project=loop.parent_scope.project,
        outcome="RESUMED",
        details={
            "parent_scope": loop.parent_scope.identifier,
            "child_scope": loop.remediation_scope.identifier,
            "run_token": str(run.token),
            "gate_name": loop.gate_name,
            "provider_execution_started": False,
        },
    )
    return loop

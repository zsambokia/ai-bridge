"""Bounded, auditable technical remediation for an existing execution run."""

from __future__ import annotations

import re
from collections.abc import Callable
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from django.db import IntegrityError, transaction
from django.utils import timezone

from .incidents import add_evidence, assess_ownership, close_incident, record_incident
from .models import (
    ExecutableScope,
    ExecutionJob,
    ExecutionRun,
    McpAuditEvent,
    TechnicalRemediationEscalation,
    TechnicalRemediationLoop,
    TechnicalRemediationValidation,
)
from .orchestrator import PolicyDecision
from .scopes import canonical_hash, propose_scope, render_scope

if TYPE_CHECKING:
    from .models import FailureIncident, OwnershipAssessment


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


MAX_REMEDIATIONS_PER_RUN_GATE = 3


def hold_unhandled_job_for_remediation(
    job: ExecutionJob,
    *,
    worker_id: str,
    exception_type: str,
) -> TechnicalRemediationLoop:
    """Release an unknown worker failure into durable technical remediation.

    Unknown exceptions must never be silently re-claimed forever.  The
    original run remains in ``REPAIRING`` until independent validation permits
    its exact checkpoint to resume.
    """
    if not exception_type or not worker_id:
        raise ValueError("WORKER_TECHNICAL_REMEDIATION_INPUT_REQUIRED")
    expected_fencing_token = job.lease_fencing_token
    idempotency_key = f"worker-remediation:{job.token}:{expected_fencing_token}"
    try:
        loop = open_technical_remediation(
            parent_run=job.run,
            classification=TechnicalRemediationLoop.Classification.TECHNICAL_REMEDIATION,
            gate_name="worker-execution",
            summary=(
                "Execution worker encountered an unclassified technical exception "
                f"({exception_type}) while processing its durable job."
            ),
            policy_basis=(
                "Sprint 7 autonomous technical remediation requires durable repair "
                "and independent validation before the original run can resume."
            ),
            evidence_references=[
                f"execution:{job.run.token}:job:{job.token}:fence:{expected_fencing_token}"
            ],
            idempotency_key=idempotency_key,
        )
    except ValueError as exc:
        if str(exc) != "TECHNICAL_REMEDIATION_LIMIT_EXCEEDED":
            raise
        # A bounded remediation policy must still release the leased job.  The
        # reconciler/Orki can now see a deterministic, auditable state instead
        # of a dead worker silently retaining the lease.
        with transaction.atomic():
            locked = (
                ExecutionJob.objects.select_for_update()
                .select_related("run")
                .get(pk=job.pk)
            )
            if locked.lease_fencing_token != expected_fencing_token:
                raise ValueError("WORKER_FENCING_TOKEN_STALE")
            if (
                locked.status != ExecutionJob.Status.LEASED
                or locked.lease_owner != worker_id
            ):
                raise ValueError("WORKER_LEASE_NOT_OWNED")
            locked.status = ExecutionJob.Status.FAILED
            locked.lease_owner = ""
            locked.lease_expires_at = None
            locked.next_recovery_at = None
            locked.provider_attempt_metadata = {
                **locked.provider_attempt_metadata,
                "recovery_action": "AUTONOMOUS_REMEDIATION_LIMIT_REACHED",
                "exception_type": exception_type[:128],
            }
            locked.save(
                update_fields=[
                    "status",
                    "lease_owner",
                    "lease_expires_at",
                    "next_recovery_at",
                    "provider_attempt_metadata",
                    "updated_at",
                ]
            )
            locked.run.lifecycle = ExecutionRun.Lifecycle.REPAIRING
            locked.run.current_phase = "TECHNICAL_REMEDIATION_LIMIT_REACHED"
            locked.run.current_blocker = {
                "classification": "TECHNICAL_REMEDIATION",
                "gate_name": "worker-execution",
                "reason": "AUTONOMOUS_REMEDIATION_LIMIT_EXCEEDED",
                "max_attempts": MAX_REMEDIATIONS_PER_RUN_GATE,
            }
            locked.run.save(
                update_fields=[
                    "lifecycle",
                    "current_phase",
                    "current_blocker",
                    "updated_at",
                ]
            )
        from .execution import add_event

        add_event(
            job.run,
            "TECHNICAL_REMEDIATION_LIMIT_REACHED",
            gate_name="worker-execution",
            exception_type=exception_type[:128],
            max_attempts=MAX_REMEDIATIONS_PER_RUN_GATE,
        )
        return TechnicalRemediationLoop.objects.filter(
            parent_run=job.run, gate_name="worker-execution"
        ).latest("created_at")
    with transaction.atomic():
        locked = (
            ExecutionJob.objects.select_for_update()
            .select_related("run")
            .get(pk=job.pk)
        )
        if locked.lease_fencing_token != expected_fencing_token:
            raise ValueError("WORKER_FENCING_TOKEN_STALE")
        if (
            locked.status != ExecutionJob.Status.LEASED
            or locked.lease_owner != worker_id
        ):
            raise ValueError("WORKER_LEASE_NOT_OWNED")
        locked.status = ExecutionJob.Status.FAILED
        locked.lease_owner = ""
        locked.lease_expires_at = None
        locked.next_recovery_at = None
        locked.provider_attempt_metadata = {
            **locked.provider_attempt_metadata,
            "recovery_action": "AUTONOMOUS_TECHNICAL_REMEDIATION",
            "technical_remediation_loop": str(loop.pk),
            "exception_type": exception_type[:128],
        }
        locked.save(
            update_fields=[
                "status",
                "lease_owner",
                "lease_expires_at",
                "next_recovery_at",
                "provider_attempt_metadata",
                "updated_at",
            ]
        )
    from .execution import add_event

    add_event(
        job.run,
        "TECHNICAL_REMEDIATION_OPENED",
        remediation_scope=loop.remediation_scope.identifier,
        gate_name=loop.gate_name,
        exception_type=exception_type[:128],
    )
    return loop


def _incident_key(kind: str, parent_run: ExecutionRun, idempotency_key: str) -> str:
    digest = sha256(
        f"{kind}:{parent_run.token}:{idempotency_key}".encode("utf-8")
    ).hexdigest()
    return f"{kind}:{digest[:96]}"


def _record_and_assess(
    *,
    parent_run: ExecutionRun,
    classification: str,
    gate_name: str,
    summary: str,
    evidence_references: list[str],
    idempotency_key: str,
    kind: str,
) -> tuple["FailureIncident", "OwnershipAssessment"]:
    incident = record_incident(
        parent_run.contract.project,
        summary,
        _incident_key(kind, parent_run, idempotency_key),
        session=parent_run.orchestration_session,
        causal_classification=classification,
    )
    for reference in evidence_references:
        add_evidence(
            incident,
            reference,
            "EXECUTION_GATE",
            f"{gate_name} evidence for {classification}",
            "execution-remediation",
        )
    assessment = assess_ownership(
        incident,
        [
            {
                "repository": parent_run.contract.project.repository_full_name,
                "component": gate_name[:255],
                "confidence": 1.0,
                "evidence_references": evidence_references,
            }
        ],
    )
    if assessment.policy_decision != PolicyDecision.ALLOW:
        raise ValueError("TECHNICAL_REMEDIATION_OWNERSHIP_DENIED")
    return incident, assessment


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
    with transaction.atomic():
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
        attempts = TechnicalRemediationLoop.objects.filter(
            parent_run=parent_run, gate_name=gate_name
        ).count()
        if attempts >= MAX_REMEDIATIONS_PER_RUN_GATE:
            McpAuditEvent.objects.create(
                caller="orchestrator-remediation-loop",
                tool_name="execution.open_technical_remediation",
                project=parent_scope.project,
                outcome="AUTONOMOUS_REMEDIATION_LIMIT_EXCEEDED",
                details={
                    "run_token": str(parent_run.token),
                    "gate_name": gate_name[:128],
                    "max_attempts": MAX_REMEDIATIONS_PER_RUN_GATE,
                },
            )
        else:
            incident, assessment = _record_and_assess(
                parent_run=parent_run,
                classification=classification,
                gate_name=gate_name,
                summary=summary,
                evidence_references=evidence_references,
                idempotency_key=idempotency_key,
                kind="technical-remediation",
            )
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
                    incident=incident,
                    idempotency_key=idempotency_key,
                    classification=classification,
                    gate_name=gate_name[:128],
                    policy_basis=policy_basis[:1000],
                    evidence_references=evidence_references,
                    status=TechnicalRemediationLoop.Status.REMEDIATING,
                    resume_checkpoint={
                        "lifecycle": parent_run.lifecycle,
                        "current_phase": parent_run.current_phase,
                        "current_blocker": parent_run.current_blocker,
                    },
                )
            except IntegrityError as exc:
                raise ValueError("TECHNICAL_REMEDIATION_IDEMPOTENCY_MISMATCH") from exc
            _event(
                loop,
                "CHILD_WORK_ITEM_CREATED",
                child_scope=child.identifier,
                incident=str(incident.token),
                ownership_policy=assessment.policy_decision,
            )
            loop.save(update_fields=["timeline", "updated_at"])
            parent_run.lifecycle = ExecutionRun.Lifecycle.REPAIRING
            parent_run.current_phase = "TECHNICAL_REMEDIATION"
            parent_run.current_blocker = {
                "classification": classification,
                "gate_name": gate_name[:128],
                "remediation_scope": child.identifier,
            }
            parent_run.save(
                update_fields=[
                    "lifecycle",
                    "current_phase",
                    "current_blocker",
                    "updated_at",
                ]
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
                    "incident": str(incident.token),
                },
            )
            return loop
    raise ValueError("TECHNICAL_REMEDIATION_LIMIT_EXCEEDED")


@transaction.atomic
def escalate_business_decision(
    *,
    parent_run: ExecutionRun,
    gate_name: str,
    summary: str,
    evidence_references: list[str],
    idempotency_key: str,
) -> TechnicalRemediationEscalation:
    """Persist an explicit business question instead of guessing an outcome."""
    required_values = (gate_name, summary, idempotency_key)
    if (
        not all(isinstance(value, str) and value.strip() for value in required_values)
        or not evidence_references
    ):
        raise ValueError("BUSINESS_ESCALATION_INPUT_REQUIRED")
    parent_run = ExecutionRun.objects.select_for_update().get(pk=parent_run.pk)
    parent_scope = _parent_scope(parent_run)
    existing = TechnicalRemediationEscalation.objects.filter(
        idempotency_key=idempotency_key
    ).first()
    if existing is not None:
        if (
            existing.parent_run_id != parent_run.pk
            or existing.gate_name != gate_name
            or existing.summary != summary
            or existing.evidence_references != evidence_references
        ):
            raise ValueError("BUSINESS_ESCALATION_IDEMPOTENCY_MISMATCH")
        return existing
    incident, assessment = _record_and_assess(
        parent_run=parent_run,
        classification=(
            TechnicalRemediationLoop.Classification.BUSINESS_DECISION_REQUIRED
        ),
        gate_name=gate_name,
        summary=summary,
        evidence_references=evidence_references,
        idempotency_key=idempotency_key,
        kind="business-escalation",
    )
    escalation = TechnicalRemediationEscalation.objects.create(
        parent_run=parent_run,
        parent_scope=parent_scope,
        incident=incident,
        idempotency_key=idempotency_key,
        classification=(
            TechnicalRemediationLoop.Classification.BUSINESS_DECISION_REQUIRED
        ),
        gate_name=gate_name[:128],
        summary=summary[:1000],
        evidence_references=evidence_references,
        status=TechnicalRemediationEscalation.Status.PENDING_PRODUCT_OWNER,
        timeline=[
            {
                "at": timezone.now().isoformat(),
                "event": "PRODUCT_OWNER_DECISION_REQUIRED",
                "details": {
                    "incident": str(incident.token),
                    "ownership_policy": assessment.policy_decision,
                },
            }
        ],
    )
    parent_run.lifecycle = ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION
    parent_run.current_phase = "BUSINESS_DECISION_ESCALATION"
    parent_run.current_blocker = {
        "classification": (
            TechnicalRemediationLoop.Classification.BUSINESS_DECISION_REQUIRED
        ),
        "gate_name": gate_name[:128],
        "escalation": str(escalation.pk),
        "summary": summary[:1000],
    }
    parent_run.save(
        update_fields=["lifecycle", "current_phase", "current_blocker", "updated_at"]
    )
    McpAuditEvent.objects.create(
        caller="orchestrator-remediation-loop",
        tool_name="execution.escalate_business_decision",
        project=parent_scope.project,
        outcome="PRODUCT_OWNER_DECISION_REQUIRED",
        details={
            "run_token": str(parent_run.token),
            "gate_name": gate_name[:128],
            "incident": str(incident.token),
        },
    )
    return escalation


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
    validator_identity: str = "independent-gate-runner",
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
    if not validator_identity.strip():
        raise ValueError("TECHNICAL_REMEDIATION_VALIDATOR_REQUIRED")
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
        TechnicalRemediationValidation.objects.create(
            remediation=loop,
            validator_identity=validator_identity[:255],
            outcome=TechnicalRemediationValidation.Outcome.FAILED,
            evidence_references=evidence_references,
            rationale="Independent invalidated-gate rerun did not pass.",
        )
        return loop
    loop.evidence_references = [*loop.evidence_references, *evidence_references]
    loop.status = TechnicalRemediationLoop.Status.RESUMED
    _event(loop, "GATE_RERUN_PASSED", evidence_references=evidence_references)
    loop.save(update_fields=["evidence_references", "status", "timeline", "updated_at"])
    TechnicalRemediationValidation.objects.create(
        remediation=loop,
        validator_identity=validator_identity[:255],
        outcome=TechnicalRemediationValidation.Outcome.PASSED,
        evidence_references=evidence_references,
        rationale="Independent invalidated-gate rerun passed.",
    )
    if loop.incident_id:
        incident = loop.incident
        assert incident is not None
        close_incident(incident, actor="orchestrator-remediation-loop")
    run = loop.parent_run
    checkpoint = loop.resume_checkpoint
    run.lifecycle = checkpoint.get("lifecycle", ExecutionRun.Lifecycle.RUNNING)
    run.current_phase = checkpoint.get("current_phase", "PREFLIGHT")
    run.current_blocker = checkpoint.get("current_blocker", {})
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
    job = (
        ExecutionJob.objects.select_for_update()
        .filter(run=run, status=ExecutionJob.Status.FAILED)
        .first()
    )
    if job is not None and job.provider_attempt_metadata.get(
        "technical_remediation_loop"
    ) == str(loop.pk):
        job.status = ExecutionJob.Status.QUEUED
        job.next_recovery_at = None
        job.provider_attempt_metadata = {
            **job.provider_attempt_metadata,
            "recovery_action": "RESUME_AFTER_TECHNICAL_REMEDIATION",
        }
        job.save(
            update_fields=[
                "status",
                "next_recovery_at",
                "provider_attempt_metadata",
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
            "resume_checkpoint": checkpoint,
        },
    )
    return loop

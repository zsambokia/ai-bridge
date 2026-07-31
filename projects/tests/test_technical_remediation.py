"""Tests for Sprint C's contract-preserving technical remediation loop."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from projects.models import (
    ExecutionContract,
    ExecutionRun,
    ExecutionStartRequest,
    McpAuditEvent,
    TechnicalRemediationEscalation,
    TechnicalRemediationValidation,
)
from projects.scopes import parse_scope_document
from projects.technical_remediation import (
    complete_technical_remediation,
    escalate_business_decision,
    open_technical_remediation,
    repair_published_scope_hash,
)
from projects.tests import test_execution


@pytest.fixture
def parent_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Path, ExecutionContract, ExecutionStartRequest, ExecutionRun]]:
    consumed = test_execution.consumed_contract.__wrapped__(tmp_path, monkeypatch)  # type: ignore[attr-defined]
    root, contract, request = next(consumed)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository="example/generic-project",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(root),
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    yield root, contract, request, run
    with pytest.raises(StopIteration):
        next(consumed)


@pytest.mark.django_db
def test_invalid_published_scope_is_repaired_then_parent_resumes(
    parent_execution: tuple[
        Path, ExecutionContract, ExecutionStartRequest, ExecutionRun
    ],
) -> None:
    root, contract, _request, run = parent_execution
    scope = contract.project.scopes.get(
        identifier=contract.payload["approved_scope"]["identifier"]
    )
    published = root / scope.published_path
    published.write_text(
        published.read_text(encoding="utf-8").replace(scope.content_hash, "0" * 64),
        encoding="utf-8",
    )
    loop = open_technical_remediation(
        parent_run=run,
        classification="TECHNICAL_REMEDIATION",
        gate_name="validate_scopes",
        summary="Restore the deterministic published-scope projection.",
        policy_basis="The parent scope authorizes in-scope technical gate repair.",
        evidence_references=["gate:validate_scopes:failed"],
        idempotency_key="repair-published-scope",
    )
    assert loop.remediation_scope.kind == "WORK_ITEM"
    assert (
        loop.remediation_scope.record["parent_execution"]["parent_scope"]
        == scope.identifier
    )
    run.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.REPAIRING
    completed = complete_technical_remediation(
        loop,
        repair=lambda: repair_published_scope_hash(scope, root),
        rerun_gate=lambda: (
            parse_scope_document(published.read_text(encoding="utf-8"), scope.project)[
                "content_hash"
            ]
            == scope.content_hash
        ),
        evidence_references=["gate:validate_scopes:passed"],
    )
    run.refresh_from_db()
    assert completed.status == "RESUMED"
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert run.current_phase == "PREFLIGHT"
    assert run.gate_rerun_count == 1
    assert completed.independent_validations.get().outcome == (
        TechnicalRemediationValidation.Outcome.PASSED
    )
    assert completed.incident is not None
    completed.incident.refresh_from_db()
    assert completed.incident.status == "CLOSED"
    assert McpAuditEvent.objects.filter(
        tool_name="execution.complete_technical_remediation", outcome="RESUMED"
    ).exists()
    assert (
        complete_technical_remediation(
            completed,
            repair=lambda: pytest.fail("replay must not repair again"),
            rerun_gate=lambda: False,
            evidence_references=["ignored-on-replay"],
        ).pk
        == completed.pk
    )


@pytest.mark.django_db
def test_non_technical_and_incomplete_evidence_are_not_auto_remediated(
    parent_execution: tuple[
        Path, ExecutionContract, ExecutionStartRequest, ExecutionRun
    ],
) -> None:
    _root, _contract, _request, run = parent_execution
    with pytest.raises(ValueError, match="BLOCKER_REQUIRES_ESCALATION"):
        open_technical_remediation(
            parent_run=run,
            classification="BUSINESS_DECISION_REQUIRED",
            gate_name="validate_scopes",
            summary="Needs a product choice.",
            policy_basis="No autonomous authority.",
            evidence_references=["gate:failed"],
            idempotency_key="business-decision",
        )
    loop = open_technical_remediation(
        parent_run=run,
        classification="TECHNICAL_REMEDIATION",
        gate_name="validate_scopes",
        summary="Repair a deterministic projection.",
        policy_basis="Parent authority is bounded to this repair.",
        evidence_references=["gate:failed"],
        idempotency_key="evidence-required",
    )
    with pytest.raises(ValueError, match="TECHNICAL_REMEDIATION_EVIDENCE_REQUIRED"):
        complete_technical_remediation(
            loop, repair=lambda: None, rerun_gate=lambda: True, evidence_references=[]
        )


@pytest.mark.django_db
def test_remediation_request_is_idempotent_and_rejects_changed_binding(
    parent_execution: tuple[
        Path, ExecutionContract, ExecutionStartRequest, ExecutionRun
    ],
) -> None:
    _root, _contract, _request, run = parent_execution
    first = open_technical_remediation(
        parent_run=run,
        classification="TECHNICAL_REMEDIATION",
        gate_name="validate_scopes",
        summary="Repair deterministic projection.",
        policy_basis="Parent authority is bounded to this repair.",
        evidence_references=["gate:failed"],
        idempotency_key="idempotent-remediation",
    )
    assert (
        open_technical_remediation(
            parent_run=run,
            classification="TECHNICAL_REMEDIATION",
            gate_name="validate_scopes",
            summary="Repair deterministic projection.",
            policy_basis="Parent authority is bounded to this repair.",
            evidence_references=["gate:failed"],
            idempotency_key="idempotent-remediation",
        ).pk
        == first.pk
    )
    with pytest.raises(ValueError, match="TECHNICAL_REMEDIATION_IDEMPOTENCY_MISMATCH"):
        open_technical_remediation(
            parent_run=run,
            classification="TECHNICAL_REMEDIATION",
            gate_name="pytest",
            summary="Repair deterministic projection.",
            policy_basis="Parent authority is bounded to this repair.",
            evidence_references=["gate:failed"],
            idempotency_key="idempotent-remediation",
        )


@pytest.mark.django_db
def test_remediation_persists_incident_ownership_and_bounds_repeat_attempts(
    parent_execution: tuple[
        Path, ExecutionContract, ExecutionStartRequest, ExecutionRun
    ],
) -> None:
    _root, _contract, _request, run = parent_execution
    first = open_technical_remediation(
        parent_run=run,
        classification="TECHNICAL_REMEDIATION",
        gate_name="pytest",
        summary="Repair a deterministic failing test.",
        policy_basis="In-scope repair.",
        evidence_references=["gate:pytest:failed"],
        idempotency_key="bounded-0",
    )
    assert first.incident is not None
    assert first.incident.status == "ASSESSED"
    assert first.incident.ownership_assessment.policy_decision == "ALLOW"
    for attempt in range(1, 3):
        open_technical_remediation(
            parent_run=run,
            classification="TECHNICAL_REMEDIATION",
            gate_name="pytest",
            summary=f"Repair attempt {attempt}.",
            policy_basis="In-scope repair.",
            evidence_references=[f"gate:pytest:failed:{attempt}"],
            idempotency_key=f"bounded-{attempt}",
        )
    with pytest.raises(ValueError, match="TECHNICAL_REMEDIATION_LIMIT_EXCEEDED"):
        open_technical_remediation(
            parent_run=run,
            classification="TECHNICAL_REMEDIATION",
            gate_name="pytest",
            summary="Fourth attempt.",
            policy_basis="In-scope repair.",
            evidence_references=["gate:pytest:failed:3"],
            idempotency_key="bounded-3",
        )
    assert run.technical_remediations.filter(gate_name="pytest").count() == 3
    assert McpAuditEvent.objects.filter(
        tool_name="execution.open_technical_remediation",
        outcome="AUTONOMOUS_REMEDIATION_LIMIT_EXCEEDED",
    ).exists()


@pytest.mark.django_db
def test_genuine_business_decision_is_escalated_without_automatic_remediation(
    parent_execution: tuple[
        Path, ExecutionContract, ExecutionStartRequest, ExecutionRun
    ],
) -> None:
    _root, _contract, _request, run = parent_execution
    escalation = escalate_business_decision(
        parent_run=run,
        gate_name="deployment_target",
        summary="Choose whether production deployment is in scope.",
        evidence_references=["decision:deployment-target-required"],
        idempotency_key="business-choice",
    )
    assert (
        escalation.status == TechnicalRemediationEscalation.Status.PENDING_PRODUCT_OWNER
    )
    assert escalation.incident.ownership_assessment.policy_decision == "ALLOW"
    run.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION
    assert run.current_phase == "BUSINESS_DECISION_ESCALATION"

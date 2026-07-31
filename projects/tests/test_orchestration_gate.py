"""Sprint 2 acceptance coverage for the mandatory normal-execution Orki gate."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest

from projects.models import (
    ConversationOrchestration,
    ExecutionContract,
    OrchestrationSession,
    Project,
)
from projects.orchestration_gate import (
    assert_contract_authorized,
    bind_runtime,
    open_gate,
    trace_for_contract,
)
from projects.scopes import propose_scope


def _project(project_id: str, repository: str) -> Project:
    return Project.objects.create(
        project_id=project_id,
        display_name=f"{project_id} project",
        repository_full_name=repository,
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _flow(project: Project, intent: str) -> ConversationOrchestration:
    scope = propose_scope(project, intent, kind="WORK_ITEM")
    return ConversationOrchestration.objects.create(
        scope=scope,
        product_owner_identity="authenticated-mcp-caller:acceptance",
        confirmation_reference="conversation-confirmation:v1:acceptance",
        proposal_version=scope.record["proposal_version"],
        proposal_hash=scope.record["proposal_hash"],
    )


def _bound_contract(
    session: OrchestrationSession, project: Project
) -> ExecutionContract:
    return cast(
        ExecutionContract,
        SimpleNamespace(
            orchestration_session=session,
            orchestration_decision_hash=session.decision_hash,
            project_id=project.pk,
            payload={
                "orchestration": {
                    "session_token": str(session.token),
                    "context_package_hash": session.context_package_hash,
                    "decision_hash": session.decision_hash,
                },
                "project": {"repository": project.repository_full_name},
                "provider_policy": {"selected_provider_identity": "codex-cli"},
                "execution": {"target_branch": "main"},
            },
        ),
    )


@pytest.mark.django_db
def test_normal_technical_request_creates_one_durable_allow_decision() -> None:
    project = _project("ai-bridge", "zsambokia/ai-bridge")
    flow = _flow(project, "Repair the deterministic worker lifecycle.")

    first = open_gate(flow, "chatgpt-mcp")
    second = open_gate(flow, "chatgpt-mcp-retry")

    assert first.pk == second.pk
    assert first.actor_identity == "authenticated-mcp-caller:acceptance"
    assert first.status == "COMPLETED"
    assert first.decision.policy_decision == "ALLOW"
    assert first.ownership_assessment.selected_project == project
    assert first.ownership_assessment.confidence == 1.0
    assert len(first.context_package_hash) == 64
    assert len(first.decision_hash) == 64


@pytest.mark.django_db
def test_ownership_of_another_registered_repository_fails_closed() -> None:
    bridge = _project("ai-bridge", "zsambokia/ai-bridge")
    demo = _project("bridge-demo", "zsambokia/bridge-demo")
    flow = _flow(bridge, "Repair zsambokia/bridge-demo's provider runtime.")

    session = open_gate(flow, "chatgpt-mcp")

    assert session.ownership_assessment.selected_project == demo
    assert session.decision.policy_decision == "DENY"
    assert "CROSS_PROJECT" in session.decision.risk_flags


@pytest.mark.django_db
def test_contract_dispatch_rejects_decision_context_or_repository_mismatch() -> None:
    project = _project("ai-bridge", "zsambokia/ai-bridge")
    session = open_gate(_flow(project, "Fix a technical worker defect."), "mcp")
    contract = _bound_contract(session, project)

    assert assert_contract_authorized(contract) == session
    contract.payload["orchestration"]["decision_hash"] = "0" * 64
    with pytest.raises(ValueError, match="ORCHESTRATION_BINDING_MISMATCH"):
        assert_contract_authorized(contract)
    contract.payload["orchestration"]["decision_hash"] = session.decision_hash
    contract.payload["project"]["repository"] = "zsambokia/bridge-demo"
    with pytest.raises(ValueError, match="ORCHESTRATION_BINDING_MISMATCH"):
        assert_contract_authorized(contract)


@pytest.mark.django_db
def test_business_authority_is_not_misclassified_as_a_technical_request() -> None:
    project = _project("ai-bridge", "zsambokia/ai-bridge")
    session = open_gate(
        _flow(project, "Make a commercial pricing business decision."), "mcp"
    )

    assert session.decision.policy_decision == "REQUIRE_PRODUCT_OWNER"
    assert session.decision.product_owner_question


@pytest.mark.django_db
def test_ambiguous_registered_projects_require_product_owner_resolution() -> None:
    bridge = _project("ai-bridge", "zsambokia/ai-bridge")
    _project("bridge-demo", "zsambokia/bridge-demo")
    session = open_gate(
        _flow(
            bridge,
            "Coordinate zsambokia/ai-bridge and zsambokia/bridge-demo providers.",
        ),
        "mcp",
    )

    assert session.ownership_assessment.selected_project is None
    assert session.decision.risk_flags == ["AMBIGUOUS_OWNERSHIP"]
    assert session.decision.authority_classification == "MIXED"
    assert session.decision.policy_decision == "REQUIRE_PRODUCT_OWNER"


@pytest.mark.django_db
def test_bridge_demo_own_work_stays_in_its_own_context() -> None:
    _project("ai-bridge", "zsambokia/ai-bridge")
    demo = _project("bridge-demo", "zsambokia/bridge-demo")
    session = open_gate(
        _flow(demo, "Repair the bridge-demo worker lease reconciliation."), "mcp"
    )

    assert session.ownership_assessment.selected_project == demo
    assert session.decision.policy_decision == "ALLOW"


@pytest.mark.django_db
def test_provider_binding_is_exposed_by_canonical_trace() -> None:
    project = _project("ai-bridge", "zsambokia/ai-bridge")
    session = open_gate(_flow(project, "Repair a technical worker defect."), "mcp")
    contract = _bound_contract(session, project)

    bind_runtime(session, contract)
    trace = trace_for_contract(contract)

    assert trace["session_token"] == str(session.token)
    assert trace["project_id"] == "ai-bridge"
    assert trace["repository"] == "zsambokia/ai-bridge"
    assert trace["provider"] == "codex-cli"
    assert trace["runtime_profile_hash"]

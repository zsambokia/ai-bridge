from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from projects.contract_policy import EXECUTION_LEVELS, RISK_MODIFIERS, TASK_TYPES
from projects.governed_mcp import (
    TOOL_SURFACE_VERSION,
    TOOLS,
    invoke_public_tool,
    public_tools,
)
from projects.models import (
    ConversationOrchestration,
    ExecutableScope,
    ExecutionContract,
    ExecutionRun,
    GovernanceApproval,
    McpAuditEvent,
    McpIdempotencyRecord,
    Project,
    ProjectContext,
    ProjectResolutionContinuation,
)
from projects.scopes import bind_approval, propose_scope


@pytest.mark.django_db
def test_public_registry_is_versioned_unique_and_schema_bounded() -> None:
    tools = public_tools()
    assert len({tool["name"] for tool in tools}) == len(tools)
    assert {
        "factory.get_status",
        "factory.begin_self_development",
        "factory.reconcile_provider_runs",
        "project.resolve",
        "akb.search",
        "execution.prepare",
        "contract.issue",
        "conversation.confirm",
        "scope.confirm_and_execute",
    }.issubset({tool["name"] for tool in tools})
    assert all(tool["inputSchema"]["additionalProperties"] is False for tool in tools)
    assert (
        invoke_public_tool("factory.list_capabilities", {})["tool_surface_version"]
        == TOOL_SURFACE_VERSION
    )


@pytest.mark.django_db
def test_cancel_mcp_requires_confirmation_and_replays_without_duplicate_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = ExecutionRun.objects.create(
        repository="zsambokia/ai-bridge",
        branch="main",
        baseline_commit="a" * 40,
        contract_hash="",
        workspace_identifier="test-workspace",
        provider_name="codex-cli",
        provider_execution_id="77",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        current_phase="EXECUTING",
        evidence_root="docs/evidence/test-cancel",
    )

    class ProviderStub:
        def status(self, execution_id: str) -> str:
            return "RUNNING"

        def cancel(self, execution_id: str) -> str:
            return "CANCELLATION_REQUESTED"

    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: ProviderStub()
    )
    caller = "product-owner"
    prepared = invoke_public_tool(
        "execution.prepare_cancel",
        {
            "execution_token": str(run.token),
            "reason": "Stop the stuck execution.",
            "idempotency_key": "prepare-cancel-1",
        },
        caller=caller,
    )
    assert prepared["confirmation_required"] is True
    confirmed = invoke_public_tool(
        "execution.confirm_cancel",
        {
            "execution_token": str(run.token),
            "confirmation_text": "igen",
            "idempotency_key": "confirm-cancel-1",
        },
        caller=caller,
    )
    arguments = {
        "execution_token": str(run.token),
        "reason": confirmed["reason"],
        "requested_by": confirmed["requested_by"],
        "confirmation_reference": confirmed["confirmation_reference"],
        "idempotency_key": "execute-cancel-1",
    }
    first = invoke_public_tool("execution.cancel", arguments, caller=caller)
    replay = invoke_public_tool("execution.cancel", arguments, caller=caller)

    assert first["status"] == "CANCELLING"
    assert replay["idempotent_replay"] is True
    run.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.CANCELLING
    assert run.events.filter(event_type="CANCELLATION_REQUESTED").count() == 1


@pytest.mark.django_db
def test_preparation_is_idempotent_and_audited() -> None:
    project = Project.objects.create(
        project_id="ai-bridge",
        display_name="Bridge",
        repository_full_name="zsambokia/ai-bridge",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Prepare the governed tool surface.", kind="SPRINT")
    approval = GovernanceApproval.objects.create(
        reference="PO-prepare",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    scope = bind_approval(scope, approval.reference)
    scope.published_path = "docs/sprints/po-prepare.md"
    scope.save(update_fields=["published_path"])
    args = {
        "project_id": project.project_id,
        "scope_identifier": scope.identifier,
        "idempotency_key": "prepare-" + str(uuid.uuid4()),
    }
    first = invoke_public_tool("execution.prepare", args)
    second = invoke_public_tool("execution.prepare", args)
    assert first["status"] == "EXECUTION_PREPARED"
    assert second["idempotent_replay"] is True
    assert McpIdempotencyRecord.objects.count() == 1
    assert McpAuditEvent.objects.filter(
        tool_name="execution.prepare", outcome="SUCCESS"
    ).exists()


@pytest.mark.django_db
def test_codex_handoff_refuses_to_invent_missing_execution_authority() -> None:
    project = Project.objects.create(
        project_id="handoff-project",
        display_name="Handoff Project",
        repository_full_name="example/handoff-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Prepare a bound Codex handoff.", kind="SPRINT")

    result = invoke_public_tool(
        "governance.prepare_codex_handoff",
        {"project_id": project.project_id, "scope_identifier": scope.identifier},
    )

    assert "governance.prepare_codex_handoff" in TOOLS
    assert result == {
        "status": "HANDOFF_INCOMPLETE",
        "scope_identifier": scope.identifier,
        "missing_fields": ["execution_contract"],
    }


@pytest.mark.django_db
def test_unknown_properties_and_unknown_tools_are_rejected() -> None:
    with pytest.raises(ValueError, match="UNKNOWN_TOOL"):
        invoke_public_tool("system.shell", {})
    with pytest.raises(
        ValueError, match="INVALID_ARGUMENTS: unknown property: untrusted"
    ):
        invoke_public_tool("factory.get_status", {"untrusted": True})


@pytest.mark.django_db
def test_execution_prepare_schema_and_runtime_validator_share_one_registry() -> None:
    published = next(
        tool for tool in public_tools() if tool["name"] == "execution.prepare"
    )
    assert published["inputSchema"] == TOOLS["execution.prepare"]["inputSchema"]

    with pytest.raises(ValueError, match="missing required property: scope_identifier"):
        invoke_public_tool(
            "execution.prepare",
            {"project_id": "ai-bridge", "idempotency_key": "prepare-123"},
        )
    with pytest.raises(ValueError, match="unknown property: sprint_path"):
        invoke_public_tool(
            "execution.prepare",
            {
                "project_id": "ai-bridge",
                "scope_identifier": "scope-123",
                "idempotency_key": "prepare-123",
                "sprint_path": "docs/sprints/legacy.md",
            },
        )
    with pytest.raises(ValueError, match="project_id: expected string"):
        invoke_public_tool(
            "execution.prepare",
            {
                "project_id": 123,
                "scope_identifier": "scope-123",
                "idempotency_key": "prepare-123",
            },
        )


@pytest.mark.django_db
def test_scope_proposal_schema_matches_policy_vocabulary() -> None:
    project = Project.objects.create(
        project_id="policy-project",
        display_name="Policy Project",
        repository_full_name="example/policy-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    for execution_level in EXECUTION_LEVELS:
        result = invoke_public_tool(
            "work_item.propose",
            {
                "project_id": project.project_id,
                "request": "Create a new Django application named storybook.",
                "execution_level": execution_level,
                "risk_modifiers": [],
                "idempotency_key": f"level-{execution_level.lower()}-123",
            },
        )
        assert result["status"] == "SCOPE_PROPOSED"
    for task_type in TASK_TYPES:
        result = invoke_public_tool(
            "work_item.propose",
            {
                "project_id": project.project_id,
                "request": "Create a new Django application named storybook.",
                "task_type": task_type,
                "risk_modifiers": sorted(RISK_MODIFIERS),
                "idempotency_key": f"task-{task_type.lower()}-123",
            },
        )
        assert result["status"] == "SCOPE_PROPOSED"

    with pytest.raises(ValueError, match="task_type: unsupported value"):
        invoke_public_tool(
            "work_item.propose",
            {
                "project_id": project.project_id,
                "request": "Create a new Django application named storybook.",
                "task_type": "UNKNOWN",
                "idempotency_key": "invalid-task-123",
            },
        )
    with pytest.raises(ValueError, match="risk_modifiers: expected array"):
        invoke_public_tool(
            "work_item.propose",
            {
                "project_id": project.project_id,
                "request": "Create a new Django application named storybook.",
                "risk_modifiers": "SECURITY_RELEVANT",
                "idempotency_key": "invalid-risk-123",
            },
        )
    with pytest.raises(ValueError, match="risk_modifiers\\[0\\]: unsupported value"):
        invoke_public_tool(
            "work_item.propose",
            {
                "project_id": project.project_id,
                "request": "Create a new Django application named storybook.",
                "risk_modifiers": ["UNKNOWN"],
                "idempotency_key": "invalid-risk-value-123",
            },
        )


@pytest.mark.django_db
def test_conversational_confirmation_binds_the_current_exact_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="conversation-project",
        display_name="Conversation Project",
        repository_full_name="example/conversation-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(
        project, "Create a new Django application named storybook.", kind="WORK_ITEM"
    )
    review = invoke_public_tool(
        "scope.review",
        {"project_id": project.project_id, "scope_identifier": scope.identifier},
    )["proposal_review"]
    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", lambda *_: None)

    result = invoke_public_tool(
        "conversation.confirm",
        {
            "project_id": project.project_id,
            "scope_identifier": scope.identifier,
            "confirmation_text": "igen",
        },
        caller="chatgpt-connector-principal",
    )

    flow = ConversationOrchestration.objects.get(scope=scope)
    assert result["orchestration_token"] == str(flow.token)
    assert flow.proposal_hash == review["proposal_hash"]
    assert flow.proposal_version == review["proposal_version"]
    assert flow.product_owner_identity.startswith("authenticated-mcp-caller:")
    assert flow.confirmation_reference.startswith("conversation-confirmation:v1:")
    assert (
        GovernanceApproval.objects.filter(
            scope=scope,
            reference=flow.confirmation_reference,
            approved_action="AUTHORIZE_EXECUTION",
        ).count()
        == 1
    )
    # A retry arrives after the proposal has left PROPOSED; it must replay the
    # existing durable flow instead of asking for another approval.
    scope.status = ExecutableScope.Status.APPROVED
    scope.save(update_fields=["status"])
    assert (
        invoke_public_tool(
            "conversation.confirm",
            {
                "project_id": project.project_id,
                "scope_identifier": scope.identifier,
                "confirmation_text": "Igen, jo lesz.",
            },
            caller="chatgpt-connector-principal",
        )["idempotent_replay"]
        is True
    )
    with pytest.raises(ValueError, match="PRODUCT_OWNER_CONFIRMATION_REQUIRED"):
        invoke_public_tool(
            "conversation.confirm",
            {
                "project_id": project.project_id,
                "scope_identifier": scope.identifier,
                "confirmation_text": "Maybe later",
            },
        )


@pytest.mark.django_db
def test_conversation_confirmation_retries_a_persisted_blocked_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="conversation-resume-project",
        display_name="Conversation Resume Project",
        repository_full_name="example/conversation-resume-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Resume the provider.", kind="WORK_ITEM")
    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", lambda *_: None)
    arguments = {
        "project_id": project.project_id,
        "scope_identifier": scope.identifier,
        "confirmation_text": "Igen, jĂł lesz.",
    }
    arguments["confirmation_text"] = "igen"
    invoke_public_tool("conversation.confirm", arguments, caller="resume-caller")
    flow = ConversationOrchestration.objects.get(scope=scope)
    flow.status = "BLOCKED"
    flow.failure_detail = {"code": "EXECUTOR_START_FAILED"}
    flow.save(update_fields=["status", "failure_detail"])
    resumed: list[ConversationOrchestration] = []

    def advance(candidate: ConversationOrchestration, caller: str) -> None:
        resumed.append(candidate)
        candidate.status = "EXECUTION_STARTED"
        candidate.current_step = "EXECUTION"
        candidate.failure_detail = {}
        candidate.save(update_fields=["status", "current_step", "failure_detail"])

    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", advance)
    result = invoke_public_tool(
        "conversation.confirm", arguments, caller="resume-caller"
    )

    assert result["idempotent_replay"] is True
    assert result["resumed"] is True
    assert resumed == [flow]


@pytest.mark.django_db
def test_conversation_confirmation_retries_a_started_durable_flow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="conversation-started-project",
        display_name="Conversation Started Project",
        repository_full_name="example/conversation-started-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Resume an exited provider.", kind="WORK_ITEM")
    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", lambda *_: None)
    arguments = {
        "project_id": project.project_id,
        "scope_identifier": scope.identifier,
        "confirmation_text": "igen",
    }
    invoke_public_tool("conversation.confirm", arguments, caller="started-caller")
    flow = ConversationOrchestration.objects.get(scope=scope)
    flow.status = "EXECUTION_STARTED"
    flow.save(update_fields=["status"])
    resumed: list[ConversationOrchestration] = []

    def advance(candidate: ConversationOrchestration, caller: str) -> None:
        resumed.append(candidate)

    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", advance)
    result = invoke_public_tool(
        "conversation.confirm", arguments, caller="started-caller"
    )

    assert result["idempotent_replay"] is True
    assert result["resumed"] is True
    assert resumed == [flow]


@pytest.mark.django_db
def test_review_routes_an_eligible_product_owner_to_simple_confirmation() -> None:
    project = Project.objects.create(
        project_id="review-routing-project",
        display_name="Review Routing Project",
        repository_full_name="example/review-routing-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Create confirmationproof.", kind="WORK_ITEM")
    review = invoke_public_tool(
        "scope.review",
        {"project_id": project.project_id, "scope_identifier": scope.identifier},
    )
    assert review["next_tool"] == "conversation.confirm"
    assert review["required_user_input"] == ["confirmation_text"]
    confirm_schema = TOOLS["conversation.confirm"]["inputSchema"]
    assert confirm_schema["required"] == [
        "project_id",
        "scope_identifier",
        "confirmation_text",
    ]
    with pytest.raises(ValueError, match="unknown property: product_owner_identity"):
        invoke_public_tool(
            "conversation.confirm",
            {
                "project_id": project.project_id,
                "scope_identifier": scope.identifier,
                "confirmation_text": "Igen.",
                "product_owner_identity": "forged",
            },
        )


@pytest.mark.django_db
def test_project_resolution_context_and_akb_journey() -> None:
    project = Project.objects.create(
        project_id="ai-bridge",
        display_name="AI Bridge",
        repository_full_name="zsambokia/ai-bridge",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    ProjectContext.objects.create(
        project=project,
        repository_full_name=project.repository_full_name,
        constitution_path="docs/constitution/BRIDGE_CONSTITUTION.md",
        roadmap_path="docs/roadmap/ROADMAP.md",
        sprint_path="docs/sprints/SPRINT_007_GOVERNED_BRIDGE_MCP_TOOL_SURFACE.md",
        current_state_path="docs/akb/CURRENT_STATE.md",
        validation_status=ProjectContext.ValidationStatus.VALID,
        source_commit_sha="a" * 40,
    )
    scope = propose_scope(project, "Read context.", kind="SPRINT")
    approval = GovernanceApproval.objects.create(
        reference="PO-context-public",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="PO",
    )
    scope = bind_approval(scope, approval.reference)
    scope.published_path = "docs/sprints/po-context.md"
    scope.save(update_fields=["published_path"])
    resolved = invoke_public_tool("project.resolve", {"query": "ai-bridge"})
    assert resolved["status"] == "PROJECT_RESOLVED"
    context = invoke_public_tool(
        "project.get_context",
        {
            "project_id": project.project_id,
            "scope_identifier": scope.identifier,
        },
    )
    assert context["status"] == "SCOPE_RETRIEVED"
    search = invoke_public_tool(
        "akb.search", {"project_id": project.project_id, "query": "MCP"}
    )
    assert search["result_limit"] == 10


@pytest.mark.django_db
def test_lifecycle_mutation_needs_durable_approval() -> None:
    project = Project.objects.create(
        project_id="ai-bridge",
        display_name="AI Bridge",
        repository_full_name="zsambokia/ai-bridge",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    ExecutionContract.objects.create(
        project=project,
        handoff_identifier="known-contract",
        approved_sprint_path="docs/sprints/SPRINT_007_GOVERNED_BRIDGE_MCP_TOOL_SURFACE.md",
        contract_hash="a" * 64,
        payload={},
    )
    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        invoke_public_tool(
            "contract.issue",
            {
                "handoff_identifier": "known-contract",
                "approval_reference": "missing-approval",
                "idempotency_key": "12345678",
            },
        )


@pytest.mark.django_db
def test_expired_and_forged_continuations_are_rejected() -> None:
    Project.objects.create(
        project_id="alpha",
        display_name="Alpha",
        repository_full_name="example/alpha",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    Project.objects.create(
        project_id="alpine",
        display_name="Alpine",
        repository_full_name="example/alpine",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    resolution = invoke_public_tool("project.resolve", {"query": "alp"})
    token = resolution["continuation_token"]
    continuation = ProjectResolutionContinuation.objects.get(token=token)
    continuation.expires_at = timezone.now() - timedelta(seconds=1)
    continuation.save(update_fields=["expires_at"])
    assert (
        invoke_public_tool(
            "project.continue_resolution",
            {
                "continuation_token": token,
                "project_id": "alpha",
                "idempotency_key": "expired-continuation",
            },
        )["status"]
        == "CONTINUATION_EXPIRED"
    )
    assert (
        invoke_public_tool(
            "project.continue_resolution",
            {
                "continuation_token": str(uuid.uuid4()),
                "project_id": "alpha",
                "idempotency_key": "forged-continuation",
            },
        )["status"]
        == "INVALID_CONTINUATION"
    )

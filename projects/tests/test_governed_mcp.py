from __future__ import annotations

import uuid
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.utils import timezone

import projects.governed_mcp as governed_mcp
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
    ExecutionCancellation,
    ExecutionContract,
    ExecutionJob,
    ExecutionProgressEvent,
    ExecutionRun,
    ExecutionStartRequest,
    ExecutionWorkspace,
    GovernanceApproval,
    McpAuditEvent,
    McpIdempotencyRecord,
    Project,
    ProjectContext,
    ProjectResolutionContinuation,
)
from projects.scopes import bind_approval, propose_scope


@pytest.mark.django_db
@pytest.mark.parametrize(
    "tool, arguments",
    [
        ("execution.get_run_status", {"execution_token": str(uuid.uuid4())}),
        ("execution.get_activity_summary", {"execution_token": str(uuid.uuid4())}),
        ("execution.list_events", {"execution_token": str(uuid.uuid4())}),
        (
            "execution.cancel",
            {
                "execution_token": str(uuid.uuid4()),
                "reason": "Product Owner requested cancellation.",
                "requested_by": "authenticated-mcp-caller:test",
                "confirmation_reference": "PO-cancel",
                "idempotency_key": "cancel-missing-run-001",
            },
        ),
    ],
)
def test_execution_tools_report_missing_runs_as_controlled_errors(
    tool: str, arguments: dict[str, str]
) -> None:
    with pytest.raises(ValueError, match="EXECUTION_NOT_FOUND"):
        invoke_public_tool(tool, arguments)


@pytest.mark.django_db
def test_execution_tools_reject_invalid_tokens_as_controlled_errors() -> None:
    with pytest.raises(ValueError, match="INVALID_EXECUTION_TOKEN"):
        invoke_public_tool(
            "execution.get_run_status", {"execution_token": "not-a-uuid"}
        )


@pytest.mark.django_db
def test_orchestration_status_exposes_conflicting_execution_token_without_rebinding() -> (  # noqa: E501
    None
):
    project = Project.objects.create(
        project_id="conflicting-execution-project",
        display_name="Conflicting Execution Project",
        repository_full_name="example/conflicting-execution-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(
        project, "Return the conflicting execution token.", kind="WORK_ITEM"
    )
    blocked_contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="blocked-contract",
        approved_sprint_path="docs/sprints/blocked.md",
        contract_hash="a" * 64,
        payload={"execution": {"target_branch": "main"}},
    )
    active_contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="active-contract",
        approved_sprint_path="docs/sprints/active.md",
        contract_hash="b" * 64,
        payload={"execution": {"target_branch": "main"}},
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-conflicting-execution",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    request = ExecutionStartRequest.objects.create(
        contract=active_contract, approval=approval
    )
    active_run = ExecutionRun.objects.create(
        contract=active_contract,
        start_request=request,
        repository=project.repository_full_name,
        branch="main",
        baseline_commit="c" * 40,
        contract_hash=active_contract.contract_hash,
        workspace_identifier="test-workspace",
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    flow = ConversationOrchestration.objects.create(
        scope=scope,
        product_owner_identity="test-product-owner",
        confirmation_reference="conversation-confirmation:v1:test",
        proposal_version=1,
        proposal_hash="d" * 64,
        status="BLOCKED",
        current_step="EXECUTION",
        contract=blocked_contract,
        failure_detail={
            "code": "CONFLICTING_ACTIVE_EXECUTION",
            "resume_available": True,
        },
    )

    result = invoke_public_tool(
        "scope.orchestration_status",
        {"project_id": project.project_id, "scope_identifier": scope.identifier},
    )

    assert flow.run is None
    assert result["execution_token"] == str(active_run.token)
    assert result["execution_lifecycle"] == ExecutionRun.Lifecycle.RUNNING
    assert result["failure_detail"]["execution_token"] == str(active_run.token)


@pytest.mark.django_db
def test_public_registry_is_versioned_unique_and_schema_bounded() -> None:
    tools = public_tools()
    assert len({tool["name"] for tool in tools}) == len(tools)
    assert {
        "factory.get_status",
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
def test_provider_terminal_activity_event_overrides_a_stale_pid_probe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="terminal-event-project",
        display_name="Terminal Event Project",
        repository_full_name="example/terminal-event-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="terminal-event-contract",
        approved_sprint_path="docs/sprints/terminal-event.md",
        contract_hash="c" * 64,
        payload={"execution": {"target_branch": "main"}},
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-terminal-event",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=project.repository_full_name,
        branch="main",
        baseline_commit="d" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="terminal-event-workspace",
        provider_name="codex-cli",
        provider_execution_id="stale-pid",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    ExecutionProgressEvent.objects.create(
        run=run,
        sequence=1,
        event_type="PROVIDER_OUTPUT",
        details={"activity_type": "turn.completed"},
    )
    monkeypatch.setattr(
        governed_mcp,
        "provider",
        lambda _name: SimpleNamespace(status=lambda _identifier: "RUNNING"),
    )

    assert governed_mcp._provider_has_completed(run) is True


@pytest.mark.django_db
def test_execution_status_exposes_consistent_queue_workspace_and_evidence() -> None:
    project = Project.objects.create(
        project_id="lifecycle-status-project",
        display_name="Lifecycle Status Project",
        repository_full_name="example/lifecycle-status-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="lifecycle-status-contract",
        approved_sprint_path="docs/sprints/lifecycle-status.md",
        contract_hash="l" * 64,
        payload={"execution": {"target_branch": "main"}},
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-lifecycle-status",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=project.repository_full_name,
        branch="main",
        baseline_commit="l" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="lifecycle-status-workspace",
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/lifecycle-status",
    )
    ExecutionJob.objects.create(
        run=run,
        status=ExecutionJob.Status.RECOVERING,
        recovery_attempts=2,
        provider_attempt_metadata={"recovery_action": "RESUME_FROM_CHECKPOINT"},
    )
    ExecutionWorkspace.objects.create(
        run=run,
        status=ExecutionWorkspace.Status.IN_USE,
        provider_pid=123,
    )

    status = invoke_public_tool(
        "execution.get_run_status", {"execution_token": str(run.token)}
    )

    assert status["queue"] == {
        "status": "RECOVERING",
        "lease_owner_present": False,
        "lease_expires_at": None,
        "last_heartbeat_at": None,
        "fencing_token": 0,
        "recovery_attempts": 2,
        "next_recovery_at": None,
        "recovery_action": "RESUME_FROM_CHECKPOINT",
    }
    assert status["workspace"] == {
        "status": "IN_USE",
        "provider_pid_present": True,
        "retention_until": None,
        "retention_reason": "",
    }
    assert status["evidence"]["evidence_root"] == "docs/evidence/lifecycle-status"


@pytest.mark.django_db
def test_confirmed_cancellation_terminalizes_a_finished_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="cancellation-project",
        display_name="Cancellation Project",
        repository_full_name="example/cancellation-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="cancellation-contract",
        approved_sprint_path="docs/sprints/cancellation.md",
        contract_hash="e" * 64,
        payload={"execution": {"target_branch": "main"}},
        lifecycle=ExecutionContract.Lifecycle.RUNNING,
    )
    approval = GovernanceApproval.objects.create(
        reference="PO-cancellation",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=project.repository_full_name,
        branch="main",
        baseline_commit="f" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier="cancellation-workspace",
        provider_name="codex-cli",
        provider_execution_id="already-finished",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/test",
    )
    monkeypatch.setattr(
        "projects.execution.provider",
        lambda _name: SimpleNamespace(status=lambda _identifier: "FINISHED"),
    )
    caller = "product-owner-session"
    prepared = invoke_public_tool(
        "execution.prepare_cancel",
        {
            "execution_token": str(run.token),
            "reason": "Product Owner requested cancellation.",
            "idempotency_key": "prepare-cancellation-001",
        },
        caller=caller,
    )
    confirmed = invoke_public_tool(
        "execution.confirm_cancel",
        {
            "execution_token": str(run.token),
            "confirmation_text": "igen",
            "idempotency_key": "confirm-cancellation-001",
        },
        caller=caller,
    )
    result = invoke_public_tool(
        "execution.cancel",
        {
            "execution_token": str(run.token),
            "reason": "Product Owner requested cancellation.",
            "requested_by": confirmed["requested_by"],
            "confirmation_reference": confirmed["confirmation_reference"],
            "idempotency_key": "cancel-cancellation-001",
        },
        caller=caller,
    )

    run.refresh_from_db()
    contract.refresh_from_db()
    cancellation = ExecutionCancellation.objects.get(run=run)
    assert prepared["status"] == ExecutionCancellation.Status.CONFIRMATION_REQUIRED
    assert result["status"] == "ALREADY_FINISHED"
    assert run.lifecycle == ExecutionRun.Lifecycle.CANCELLED
    assert run.terminal_state == "CANCELLED — PRODUCT OWNER REQUESTED"
    assert cancellation.status == ExecutionCancellation.Status.CANCELLED
    assert contract.lifecycle == ExecutionContract.Lifecycle.CANCELLED
    assert run.events.filter(event_type="CANCELLATION_EVIDENCE_COMPLETED").exists()


@pytest.mark.django_db
def test_evidence_backed_completion_closes_the_approved_scope_without_new_review(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A PASS completes the run, contract, orchestration, and approved scope."""
    project = Project.objects.create(
        project_id="automatic-completion-project",
        display_name="Automatic Completion Project",
        repository_full_name="example/automatic-completion-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Close this evidence-backed sprint.", kind="SPRINT")
    approval = GovernanceApproval.objects.create(
        reference="PO-automatic-completion",
        project=project,
        approved_action="AUTHORIZE_EXECUTION",
        approved_by="Product Owner",
    )
    scope = bind_approval(scope, approval.reference)
    contract = ExecutionContract.objects.create(
        project=project,
        handoff_identifier="automatic-completion-contract",
        approved_sprint_path="docs/sprints/automatic-completion.md",
        contract_hash="a" * 64,
        lifecycle=ExecutionContract.Lifecycle.RUNNING,
        payload={
            "schema_version": "2.0",
            "allowed_terminal_states": ["PASS — READY FOR PRODUCT OWNER REVIEW"],
        },
    )
    request = ExecutionStartRequest.objects.create(contract=contract, approval=approval)
    run = ExecutionRun.objects.create(
        contract=contract,
        start_request=request,
        repository=project.repository_full_name,
        branch="main",
        baseline_commit="b" * 40,
        contract_hash=contract.contract_hash,
        workspace_identifier=str(tmp_path),
        provider_name="codex-cli",
        lifecycle=ExecutionRun.Lifecycle.RUNNING,
        evidence_root="docs/evidence/automatic-completion",
    )
    flow = ConversationOrchestration.objects.create(
        scope=scope,
        product_owner_identity="test-product-owner",
        confirmation_reference="conversation-confirmation:v1:automatic-completion",
        proposal_version=scope.record["proposal_version"],
        proposal_hash=scope.record["proposal_hash"],
        status="EXECUTION_STARTED",
        current_step="EXECUTION",
        contract=contract,
        run=run,
    )
    evidence_path = "docs/evidence/automatic-completion/CLOSURE_REPORT.md"
    (tmp_path / evidence_path).parent.mkdir(parents=True)
    (tmp_path / evidence_path).write_text("evidence", encoding="utf-8")
    completion_data = {
        "execution_result": "PASS",
        "gate_results": {"pytest": "PASS"},
        "evidence_manifest": {"closure_report": evidence_path},
        "changed_files": ["projects/governed_mcp.py"],
        "failure_classification": None,
    }

    def complete_without_subprocess(
        candidate: ExecutionRun, final_commit_sha: str, data: dict[str, object]
    ) -> ExecutionRun:
        candidate.lifecycle = ExecutionRun.Lifecycle.COMPLETED
        candidate.current_phase = "COMPLETED"
        candidate.final_commit_sha = final_commit_sha
        candidate.terminal_state = "PASS"
        candidate.completion_data = data
        candidate.save(
            update_fields=[
                "lifecycle",
                "current_phase",
                "final_commit_sha",
                "terminal_state",
                "completion_data",
                "updated_at",
            ]
        )
        return candidate

    monkeypatch.setattr(governed_mcp, "_provider_has_completed", lambda _run: True)
    monkeypatch.setattr(governed_mcp, "complete_run", complete_without_subprocess)
    monkeypatch.setattr(governed_mcp, "project_repository_root", lambda *_: tmp_path)

    result = invoke_public_tool(
        "scope.complete_execution",
        {
            "project_id": project.project_id,
            "scope_identifier": scope.identifier,
            "orchestration_token": str(flow.token),
            "final_commit_sha": "c" * 40,
            "completion_data": completion_data,
            "idempotency_key": "automatic-completion-001",
        },
        caller="test-product-owner",
    )

    scope.refresh_from_db()
    contract.refresh_from_db()
    run.refresh_from_db()
    flow.refresh_from_db()
    assert result["status"] == "COMPLETED"
    assert result["scope_status"] == "COMPLETED"
    assert scope.status == ExecutableScope.Status.COMPLETED
    assert scope.record["execution_authorization"] == "NONE"
    assert contract.lifecycle == ExecutionContract.Lifecycle.COMPLETED
    assert run.lifecycle == ExecutionRun.Lifecycle.COMPLETED
    assert flow.status == "COMPLETED"
    assert GovernanceApproval.objects.filter(project=project).count() == 1


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
            "confirmation_text": (
                "I approve the exact displayed proposal for scope "
                f"{scope.identifier}, proposal version {review['proposal_version']}, "
                f"hash {review['proposal_hash']}."
            ),
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
    for confirmation_text in (
        "Maybe later",
        "I approve if the provider is available.",
        "I do not approve the displayed proposal.",
        "I approve, but don't start execution yet.",
    ):
        with pytest.raises(ValueError, match="PRODUCT_OWNER_CONFIRMATION_REQUIRED"):
            invoke_public_tool(
                "conversation.confirm",
                {
                    "project_id": project.project_id,
                    "scope_identifier": scope.identifier,
                    "confirmation_text": confirmation_text,
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
def test_scope_resume_recovers_an_approved_scope_from_a_new_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="recovery-session-project",
        display_name="Recovery Session Project",
        repository_full_name="example/recovery-session-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Recover a disconnected approval.", kind="WORK_ITEM")
    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", lambda *_: None)

    initial = invoke_public_tool(
        "conversation.confirm",
        {
            "project_id": project.project_id,
            "scope_identifier": scope.identifier,
            "confirmation_text": "igen",
        },
        caller="lost-chatgpt-session",
    )
    flow = ConversationOrchestration.objects.get(scope=scope)
    scope.status = ExecutableScope.Status.APPROVED
    scope.save(update_fields=["status"])
    flow.status = "BLOCKED"
    flow.failure_detail = {"code": "MCP_SESSION_LOST"}
    flow.save(update_fields=["status", "failure_detail"])

    recovery = invoke_public_tool(
        "scope.resume",
        {"project_id": project.project_id, "scope_identifier": scope.identifier},
        caller="new-chatgpt-session",
    )
    assert recovery["status"] == "RECOVERABLE"
    assert recovery["scope"]["version"] == flow.proposal_version
    assert recovery["scope"]["hash"] == flow.proposal_hash

    resumed: list[ConversationOrchestration] = []

    def advance(candidate: ConversationOrchestration, caller: str) -> None:
        resumed.append(candidate)
        candidate.status = "EXECUTION_STARTED"
        candidate.current_step = "EXECUTION"
        candidate.failure_detail = {}
        candidate.save(update_fields=["status", "current_step", "failure_detail"])

    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", advance)
    arguments = {
        "project_id": project.project_id,
        "scope_identifier": scope.identifier,
        "proposal_version": recovery["scope"]["version"],
        "proposal_hash": recovery["scope"]["hash"],
        "confirmation_text": (
            "I confirm the exact displayed proposal for scope "
            f"{scope.identifier}, proposal version {recovery['scope']['version']}, "
            f"hash {recovery['scope']['hash']}."
        ),
    }
    result = invoke_public_tool(
        "scope.resume_confirm_and_execute", arguments, caller="new-chatgpt-session"
    )

    assert result["resumed"] is True
    assert result["approval_replayed"] is True
    assert result["orchestration_token"] == initial["orchestration_token"]
    assert resumed == [flow]
    assert GovernanceApproval.objects.filter(scope=scope).count() == 1
    assert McpAuditEvent.objects.filter(
        tool_name="scope.resume_confirm_and_execute", outcome="APPROVAL_REPLAYED"
    ).exists()

    replay = invoke_public_tool(
        "scope.resume_confirm_and_execute", arguments, caller="new-chatgpt-session"
    )
    assert replay["idempotent_replay"] is True
    assert GovernanceApproval.objects.filter(scope=scope).count() == 1


@pytest.mark.django_db
def test_scope_resume_rejects_a_stale_hash_before_reusing_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.objects.create(
        project_id="recovery-stale-project",
        display_name="Recovery Stale Project",
        repository_full_name="example/recovery-stale-project",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    scope = propose_scope(project, "Reject stale recovery binding.", kind="WORK_ITEM")
    monkeypatch.setattr("projects.governed_mcp._advance_orchestration", lambda *_: None)
    recovery = invoke_public_tool(
        "scope.resume",
        {"project_id": project.project_id, "scope_identifier": scope.identifier},
    )

    with pytest.raises(ValueError, match="SCOPE_HASH_MISMATCH"):
        invoke_public_tool(
            "scope.resume_confirm_and_execute",
            {
                "project_id": project.project_id,
                "scope_identifier": scope.identifier,
                "proposal_version": recovery["scope"]["version"],
                "proposal_hash": "0" * 64,
                "confirmation_text": "igen",
            },
            caller="new-chatgpt-session",
        )
    assert not GovernanceApproval.objects.filter(scope=scope).exists()


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

from __future__ import annotations

import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from projects.governed_mcp import TOOL_SURFACE_VERSION, invoke_public_tool, public_tools
from projects.models import (
    ExecutionContract,
    McpAuditEvent,
    McpIdempotencyRecord,
    Project,
    ProjectContext,
    ProjectResolutionContinuation,
)


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
    }.issubset({tool["name"] for tool in tools})
    assert all(tool["inputSchema"]["additionalProperties"] is False for tool in tools)
    assert (
        invoke_public_tool("factory.list_capabilities", {})["tool_surface_version"]
        == TOOL_SURFACE_VERSION
    )


@pytest.mark.django_db
def test_preparation_is_idempotent_and_audited() -> None:
    project = Project.objects.create(
        project_id="ai-bridge",
        display_name="Bridge",
        repository_full_name="zsambokia/ai-bridge",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    args = {
        "project_id": project.project_id,
        "intent": "Prepare the governed tool surface.",
        "execution_level": "SPRINT",
        "task_type": "FEATURE",
        "risk_modifiers": ["EXTERNAL_INTEGRATION"],
        "sprint_path": "docs/sprints/SPRINT_007_GOVERNED_BRIDGE_MCP_TOOL_SURFACE.md",
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
def test_unknown_properties_and_unknown_tools_are_rejected() -> None:
    with pytest.raises(ValueError, match="UNKNOWN_TOOL"):
        invoke_public_tool("system.shell", {})
    with pytest.raises(ValueError, match="INVALID_ARGUMENTS"):
        invoke_public_tool("factory.get_status", {"untrusted": True})


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
    resolved = invoke_public_tool("project.resolve", {"query": "ai-bridge"})
    assert resolved["status"] == "PROJECT_RESOLVED"
    context = invoke_public_tool(
        "project.get_context",
        {
            "project_id": project.project_id,
            "sprint_path": (
                "docs/sprints/SPRINT_007_GOVERNED_BRIDGE_MCP_TOOL_SURFACE.md"
            ),
        },
    )
    assert context["status"] == "EXECUTION_CONTEXT_GENERATED"
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

"""Sprint 3 acceptance: durable knowledge retrieval and governed roadmap feedback."""

from __future__ import annotations

import pytest
from django.contrib import admin

from projects.governed_mcp import invoke_public_tool
from projects.knowledge import (
    context_package,
    create_or_upsert_candidate,
    mark_stale_for_source_revision,
    review_candidate,
)
from projects.models import (
    ConversationOrchestration,
    GovernanceApproval,
    KnowledgeContextPackage,
    KnowledgeContextUse,
    KnowledgeEntry,
    Project,
    RoadmapItem,
)
from projects.orchestration_gate import open_gate
from projects.roadmap import create_item, propose_update, review_update
from projects.scopes import propose_scope


def _project(project_id: str, repository: str) -> Project:
    return Project.objects.create(
        project_id=project_id,
        display_name=project_id,
        repository_full_name=repository,
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _active_decision(project: Project, key: str = "durable-decision") -> KnowledgeEntry:
    entry = create_or_upsert_candidate(
        project,
        {
            "entry_key": key,
            "scope": "PROJECT",
            "knowledge_type": "PRODUCT_DECISION",
            "title": f"Persistent approved lifecycle decision {key}",
            "content": "Every execution uses the approved deterministic lifecycle.",
            "source_reference": "decision:product-owner:1",
            "source_version": "po-1",
            "is_must_know": True,
            "evidence_references": ["evidence:decision:1"],
        },
        "product-owner",
    )
    approval = GovernanceApproval.objects.create(
        reference=f"approval:{key}",
        project=project,
        approved_action="AKB_PUBLISH",
        approved_by="product-owner",
    )
    return review_candidate(
        project, entry.pk, "APPROVE", "product-owner", approval.reference
    )


def _flow(project: Project, intent: str) -> ConversationOrchestration:
    scope = propose_scope(project, intent, kind="WORK_ITEM")
    return ConversationOrchestration.objects.create(
        scope=scope,
        product_owner_identity="product-owner",
        confirmation_reference=f"confirmation:{scope.identifier}",
        proposal_version=scope.record["proposal_version"],
        proposal_hash=scope.record["proposal_hash"],
    )


@pytest.mark.django_db
def test_two_session_reuse_is_durable_and_cross_project_isolated() -> None:
    bridge = _project("ai-bridge", "zsambokia/ai-bridge")
    other = _project("other", "zsambokia/other")
    decision = _active_decision(bridge)

    session_a = open_gate(
        _flow(bridge, "Apply the approved lifecycle decision."), "mcp"
    )
    session_b = open_gate(
        _flow(bridge, "Apply the approved lifecycle decision again."), "mcp"
    )
    isolated = open_gate(_flow(other, "Apply the approved lifecycle decision."), "mcp")

    use_a = KnowledgeContextUse.objects.get(session=session_a)
    use_b = KnowledgeContextUse.objects.get(session=session_b)
    assert decision.pk in use_a.package.entry_ids
    assert decision.pk in use_b.package.entry_ids
    assert use_b.package.source_versions[str(decision.pk)] == "po-1"
    assert use_b.decision == session_b.decision
    assert use_b.package.retrieval_intent == "conversation-confirmation"
    assert use_b.package.package_hash == session_b.context_package_hash
    assert (
        decision.pk
        not in KnowledgeContextUse.objects.get(session=isolated).package.entry_ids
    )


@pytest.mark.django_db
def test_conflicts_and_machine_source_drift_are_visible_in_context() -> None:
    project = _project("ai-bridge", "zsambokia/ai-bridge")
    first = _active_decision(project, "conflict-first")
    second = _active_decision(project, "conflict-second")
    KnowledgeEntry.objects.filter(pk=first.pk).update(
        conflict_key="lifecycle", precedence=5
    )
    KnowledgeEntry.objects.filter(pk=second.pk).update(
        conflict_key="lifecycle", precedence=1
    )
    first.refresh_from_db()
    second.refresh_from_db()

    package = context_package(project, "acceptance:conflict", "ENGINEERING")
    assert second.pk in package["entry_ids"]
    assert first.pk not in package["entry_ids"]
    assert package["conflict_warnings"][0]["winner_entry_id"] == second.pk
    mark_stale_for_source_revision(second, "po-2", "reconciler")
    package = context_package(project, "acceptance:conflict", "ENGINEERING")
    assert second.pk in package["stale_warnings"]


@pytest.mark.django_db
def test_mcp_persists_context_and_governed_roadmap_update_creates_akb_feedback() -> (
    None
):
    project = _project("ai-bridge", "zsambokia/ai-bridge")
    _active_decision(project)
    context = invoke_public_tool(
        "akb.get_context_package",
        {
            "project_id": project.project_id,
            "work_context_id": "mcp:acceptance",
            "retrieval_intent": "acceptance",
            "retrieval_query": "approved lifecycle",
        },
    )
    package = KnowledgeContextPackage.objects.get(pk=context["package_id"])
    assert package.package_hash == context["hash"]
    assert package.retrieval_intent == "acceptance"
    assert package.retrieval_query == "approved lifecycle"
    item = create_item(
        project,
        {"item_key": "sprint-3", "title": "Sprint 3", "dependencies": ["sprint-2"]},
    )
    candidate = propose_update(
        project,
        item.item_key,
        {
            "idempotency_key": "roadmap-sprint-3-accepted",
            "proposed_state": "COMPLETED",
            "engineering_status": "PASS",
            "operational_status": "PASS",
            "evidence_references": ["docs/evidence/sprint-3"],
            "final_commit_sha": "a" * 40,
            "source_reference": "sprint-3-closure",
        },
    )
    item.refresh_from_db()
    assert item.state == RoadmapItem.State.PROPOSED
    approval = GovernanceApproval.objects.create(
        reference="approval:roadmap:3",
        project=project,
        approved_action="ROADMAP_PROGRESS",
        approved_by="product-owner",
    )
    review_update(project, candidate.pk, "APPROVE", "product-owner", approval.reference)
    item.refresh_from_db()
    assert item.state == RoadmapItem.State.COMPLETED
    assert item.final_commit_sha == "a" * 40
    assert KnowledgeEntry.objects.filter(
        project=project,
        knowledge_type="ROADMAP",
        status=KnowledgeEntry.Status.CANDIDATE,
    ).exists()


@pytest.mark.django_db
def test_admin_and_mcp_use_the_same_canonical_knowledge_models() -> None:
    from projects.models import KnowledgeContextPackage, RoadmapUpdateCandidate

    assert KnowledgeEntry in admin.site._registry
    assert KnowledgeContextPackage in admin.site._registry
    assert KnowledgeContextUse in admin.site._registry
    assert RoadmapItem in admin.site._registry
    assert RoadmapUpdateCandidate in admin.site._registry

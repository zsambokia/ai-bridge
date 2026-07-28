"""Sprint 1 AKB foundation: lifecycle, isolation, context, and incident coverage."""

from __future__ import annotations

import pytest

from projects.governed_mcp import invoke_public_tool
from projects.incidents import add_evidence, close_incident, record_incident
from projects.knowledge import (
    context_package,
    create_or_upsert_candidate,
    review_candidate,
    search,
)
from projects.models import GovernanceApproval, KnowledgeEntry, Project


def _project(identifier: str = "akb-test") -> Project:
    return Project.objects.create(
        project_id=identifier,
        display_name=identifier,
        repository_full_name=f"example/{identifier}",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _candidate(key: str = "akb:test") -> dict[str, object]:
    return {
        "entry_key": key,
        "scope": "PROJECT",
        "knowledge_type": "SYSTEM_DESIGN",
        "title": "Bounded design",
        "content": "The canonical MCP boundary is governed.",
        "source_type": "TEST",
        "source_reference": "test:akb",
        "evidence_references": ["test:akb"],
        "role_context": ["ENGINEERING"],
        "is_must_know": True,
    }


@pytest.mark.django_db
def test_candidate_requires_approval_to_become_active_and_is_searchable() -> None:
    project = _project()
    entry = create_or_upsert_candidate(project, _candidate(), "tester")
    assert entry.status == KnowledgeEntry.Status.CANDIDATE
    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        review_candidate(project, entry.pk, "APPROVE", "reviewer")
    approval = GovernanceApproval.objects.create(
        reference="akb-approval",
        project=project,
        approved_action="akb.review_candidate",
        approved_by="PO",
    )
    active = review_candidate(
        project, entry.pk, "APPROVE", "reviewer", approval.reference
    )
    assert active.status == KnowledgeEntry.Status.ACTIVE
    assert active.revisions.count() == 2
    hits = search(project, "canonical", {"limit": 10})
    assert [hit["entry_id"] for hit in hits] == [active.pk]


@pytest.mark.django_db
def test_context_package_is_deterministic_and_project_isolated() -> None:
    project = _project()
    other = _project("akb-other")
    entry = create_or_upsert_candidate(project, _candidate(), "tester")
    approval = GovernanceApproval.objects.create(
        reference="akb-package",
        project=project,
        approved_action="AKB_PUBLISH",
        approved_by="PO",
    )
    review_candidate(project, entry.pk, "APPROVE", "reviewer", approval.reference)
    first = context_package(project, "work:1", "ENGINEERING")
    second = context_package(project, "work:1", "ENGINEERING")
    foreign = context_package(other, "work:1", "ENGINEERING")
    assert first["hash"] == second["hash"]
    assert entry.pk in first["entry_ids"]
    assert foreign["entry_ids"] == []


@pytest.mark.django_db
def test_closed_incident_creates_reviewable_lesson_not_active_knowledge() -> None:
    project = _project()
    incident = record_incident(
        project, "A bounded test failure", "akb-incident", causal_classification="TEST"
    )
    add_evidence(incident, "run:akb", "TEST", "failure evidence", "test")
    lesson = close_incident(incident, "incident-worker")
    incident.refresh_from_db()
    assert incident.status == "CLOSED"
    assert lesson.status == KnowledgeEntry.Status.CANDIDATE
    assert lesson.knowledge_type == "INCIDENT_LESSON"
    assert search(project, "bounded", {"limit": 10}) == []


@pytest.mark.django_db
def test_governed_mcp_akb_candidate_review_and_context_journey() -> None:
    project = _project()
    created = invoke_public_tool(
        "akb.create_candidate",
        {
            **_candidate("akb:mcp-journey"),
            "project_id": project.project_id,
            "idempotency_key": "akb-mcp-create",
        },
    )
    approval = GovernanceApproval.objects.create(
        reference="akb-mcp-approval",
        project=project,
        approved_action="akb.review_candidate",
        approved_by="PO",
    )
    reviewed = invoke_public_tool(
        "akb.review_candidate",
        {
            "project_id": project.project_id,
            "entry_id": created["entry_id"],
            "decision": "APPROVE",
            "approval_reference": approval.reference,
            "idempotency_key": "akb-mcp-review",
        },
    )
    package = invoke_public_tool(
        "akb.get_context_package",
        {"project_id": project.project_id, "work_context_id": "akb:authoring"},
    )
    assert reviewed["status"] == KnowledgeEntry.Status.ACTIVE
    assert created["entry_id"] in package["entry_ids"]
    assert len(package["hash"]) == 64

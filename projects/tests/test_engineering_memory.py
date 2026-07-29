"""Sprint 2 evidence for normalized, governed engineering memory."""

import pytest

from projects.engineering_memory import (
    LIFECYCLE_EVENTS,
    activate_candidate,
    impact,
    ingest_lifecycle_event,
    link,
    planning_assessment,
    revision_diff,
    search,
    upsert_candidate,
)
from projects.governed_mcp import invoke_public_tool
from projects.models import (
    EngineeringEntity,
    GovernanceApproval,
    McpAuditEvent,
    Project,
)


def _project(name: str = "engineering-memory") -> Project:
    return Project.objects.create(
        project_id=name,
        display_name=name,
        repository_full_name=f"example/{name}",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _entity(key: str, kind: str = "COMPONENT") -> dict[str, object]:
    return {
        "entity_key": key,
        "kind": kind,
        "name": key.title(),
        "source_reference": f"test:{key}",
        "evidence_references": [f"evidence:{key}"],
        "attributes": {"owner": "engineering"},
    }


def _roadmap_attributes(**overrides: object) -> dict[str, object]:
    attributes: dict[str, object] = {
        "parent_key": "epic:platform",
        "group": "knowledge",
        "horizon": "Q3",
        "status": "PLANNED",
        "priority": "P1",
        "dependencies": [],
        "target_application": "ai-bridge",
        "target_feature": "akb",
        "outcome": "Governed engineering memory",
        "acceptance_criteria": ["audit pass"],
        "risk": "LOW",
        "github_references": ["#123"],
    }
    attributes.update(overrides)
    return attributes


@pytest.mark.django_db
def test_candidate_activation_has_approval_and_append_only_history() -> None:
    project = _project()
    candidate = upsert_candidate(project, _entity("api-bridge", "API"), actor="author")
    assert candidate.state == "CANDIDATE"
    assert candidate.revisions.count() == 1
    active = activate_candidate(
        project, candidate.entity_key, approval_reference="po-1", actor="reviewer"
    )
    assert active.state == "ACTIVE"
    assert active.version == 2
    assert active.revisions.count() == 2
    assert revision_diff(project, candidate.entity_key, from_version=1, to_version=2)[
        "changed_fields"
    ] == ["approval_reference", "state"]


@pytest.mark.django_db
def test_relationships_are_typed_project_isolated_and_queryable_by_role() -> None:
    project = _project()
    other = _project("engineering-memory-other")
    source = upsert_candidate(project, _entity("component-a"), actor="author")
    target = upsert_candidate(project, _entity("service-a", "SERVICE"), actor="author")
    activate_candidate(
        project, source.entity_key, approval_reference="po-1", actor="reviewer"
    )
    activate_candidate(
        project, target.entity_key, approval_reference="po-1", actor="reviewer"
    )
    link(
        project,
        source_key="component-a",
        target_key="service-a",
        relationship_type="IMPLEMENTS",
        evidence_references=["test:relation"],
    )
    graph = impact(project, "component-a")
    assert graph["affected_keys"] == ["service-a"]
    assert [
        item.entity_key for item in search(project, role_profile="DEVELOPMENT")
    ] == ["component-a", "service-a"]
    assert search(other, query="component") == []


@pytest.mark.django_db
def test_all_required_lifecycle_events_are_retry_safe_candidates() -> None:
    project = _project()
    for event in LIFECYCLE_EVENTS:
        first = ingest_lifecycle_event(
            project,
            event_type=event,
            event_key="evidence-1",
            source_reference="test:lifecycle",
            evidence_references=["test:evidence"],
            attributes={"status": "PASS"},
        )
        second = ingest_lifecycle_event(
            project,
            event_type=event,
            event_key="evidence-1",
            source_reference="test:lifecycle",
            evidence_references=["test:evidence"],
            attributes={"status": "PASS"},
        )
        assert first.pk == second.pk
        assert first.state == "CANDIDATE"
    assert (
        EngineeringEntity.objects.filter(
            project=project, entity_key__startswith="lifecycle:"
        ).count()
        == 5
    )


@pytest.mark.django_db
def test_mcp_authoring_search_review_and_audit_are_governed() -> None:
    project = _project()
    args = {
        "project_id": project.project_id,
        **_entity("roadmap-1", "ROADMAP_ITEM"),
        "attributes": _roadmap_attributes(),
        "idempotency_key": "engineering-roadmap-001",
    }
    created = invoke_public_tool(
        "engineering.upsert_candidate", args, caller="test-agent"
    )
    assert created["state"] == "CANDIDATE"
    approval = GovernanceApproval.objects.create(
        reference="engineering-po-1",
        project=project,
        approved_action="engineering.review_candidate",
        approved_by="PO",
    )
    reviewed = invoke_public_tool(
        "engineering.review_candidate",
        {
            "project_id": project.project_id,
            "entity_key": "roadmap-1",
            "approval_reference": approval.reference,
            "idempotency_key": "engineering-review-001",
        },
        caller="test-agent",
    )
    assert reviewed["state"] == "ACTIVE"
    found = invoke_public_tool(
        "engineering.search",
        {
            "project_id": project.project_id,
            "query": "roadmap",
            "role_profile": "PRODUCT",
        },
    )
    assert [item["entity_key"] for item in found["results"]] == ["roadmap-1"]


@pytest.mark.django_db
def test_first_class_adapters_validate_structured_objects_and_versions() -> None:
    project = _project()
    adapter_payloads = {
        "roadmap": _roadmap_attributes(),
        "constitution": {
            "section_identifier": "article-iii",
            "effective_from": "2026-07-29",
            "status": "EFFECTIVE",
        },
        "ui_plan": {
            "application": "ai-bridge",
            "screens": ["knowledge"],
            "workspaces": ["engineering"],
            "roles": ["DEVELOPMENT"],
            "workflow_states": ["DRAFT"],
            "components": ["akb"],
            "feature_links": ["akb"],
            "design_status": "APPROVED",
            "implementation_status": "PLANNED",
            "assets": [],
        },
        "system_design": {
            "scope": "AKB",
            "boundaries": ["project"],
            "components": ["memory"],
            "services": ["mcp"],
            "apis": ["engineering.search"],
            "contracts": ["MCP"],
            "data_model": ["EngineeringEntity"],
            "flows": ["candidate-review"],
            "integrations": [],
            "security": ["project-isolation"],
            "operations": ["audit"],
            "alternatives": [],
            "decisions": [],
            "adr_links": [],
            "implementation_status": "IMPLEMENTED",
            "review_status": "APPROVED",
        },
    }
    for adapter, attributes in adapter_payloads.items():
        result = invoke_public_tool(
            f"{adapter}.upsert_candidate",
            {
                "project_id": project.project_id,
                "entity_key": f"{adapter}:one",
                "name": adapter,
                "source_reference": f"test:{adapter}",
                "attributes": attributes,
                "idempotency_key": f"{adapter}-one",
            },
            caller="test-agent",
        )
        assert result["state"] == "CANDIDATE"

    audit = McpAuditEvent.objects.get(tool_name="roadmap.upsert_candidate")
    assert audit.details["modified_entity_keys"] == ["roadmap:one"]

    candidate = EngineeringEntity.objects.get(project=project, entity_key="roadmap:one")
    with pytest.raises(ValueError, match="ENGINEERING_CONFLICT"):
        upsert_candidate(
            project,
            {
                **_entity("roadmap:one", "ROADMAP_ITEM"),
                "attributes": _roadmap_attributes(),
            },
            actor="author",
            upsert=True,
        )
    assert candidate.revisions.count() == 1


@pytest.mark.django_db
def test_constitution_diff_and_history_are_project_isolated() -> None:
    project = _project()
    candidate = upsert_candidate(
        project,
        {
            **_entity("constitution:article-iii", "CONSTITUTION_SECTION"),
            "attributes": {
                "section_identifier": "article-iii",
                "effective_from": "2026-07-29",
                "status": "DRAFT",
            },
        },
        actor="author",
    )
    updated = upsert_candidate(
        project,
        {
            **_entity("constitution:article-iii", "CONSTITUTION_SECTION"),
            "attributes": {
                "section_identifier": "article-iii",
                "effective_from": "2026-07-30",
                "status": "EFFECTIVE",
            },
            "expected_version": candidate.version,
        },
        actor="author",
        upsert=True,
    )
    result = invoke_public_tool(
        "constitution.diff",
        {
            "project_id": project.project_id,
            "entity_key": updated.entity_key,
            "from_version": 1,
            "to_version": 2,
        },
    )
    assert result["changed_fields"] == ["attributes"]
    history = invoke_public_tool(
        "engineering.history",
        {"project_id": project.project_id, "entity_key": updated.entity_key},
    )
    assert [item["version"] for item in history["revisions"]] == [1, 2]


@pytest.mark.django_db
def test_planning_assessment_finds_gaps_prerequisites_and_conflicts() -> None:
    project = _project()
    for key, attributes in {
        "roadmap:a": _roadmap_attributes(
            target_capability="missing-capability",
            dependencies=["missing-prerequisite"],
        ),
        "roadmap:b": _roadmap_attributes(github_references=["#123"]),
    }.items():
        candidate = upsert_candidate(
            project,
            {**_entity(key, "ROADMAP_ITEM"), "attributes": attributes},
            actor="author",
        )
        activate_candidate(project, key, approval_reference="po-1", actor="reviewer")
        assert candidate.state == "CANDIDATE"
    assessment = planning_assessment(project)
    assert assessment == {
        "missing_capabilities": ["missing-capability"],
        "missing_prerequisites": ["missing-prerequisite"],
        "conflicting_github_references": ["#123"],
    }
    assert (
        invoke_public_tool("engineering.plan", {"project_id": project.project_id})
        == assessment
    )

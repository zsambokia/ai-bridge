"""Executable Sprint 01 acceptance for the Semantic Layer foundation."""

from __future__ import annotations

import pytest

from projects.knowledge import create_or_upsert_candidate, review_candidate
from projects.models import GovernanceApproval, KnowledgeContextPackage, Project
from projects.semantic import (
    SELECTION_STRATEGY,
    SemanticContext,
    build_semantic_context,
)


def _project(identifier: str) -> Project:
    return Project.objects.create(
        project_id=identifier,
        display_name=identifier,
        repository_full_name=f"example/{identifier}",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _active_entry(project: Project, key: str, **overrides: object) -> int:
    entry = create_or_upsert_candidate(
        project,
        {
            "entry_key": key,
            "scope": "PROJECT",
            "knowledge_type": "SYSTEM_DESIGN",
            "title": "Semantic foundation source",
            "content": "Governed context selection keeps provenance.",
            "source_type": "TEST",
            "source_reference": f"test:{key}",
            "evidence_references": [f"test:{key}"],
            **overrides,
        },
        "test",
    )
    approval = GovernanceApproval.objects.create(
        reference=f"approval:{key}",
        project=project,
        approved_action="AKB_PUBLISH",
        approved_by="PO",
    )
    return review_candidate(
        project, entry.pk, "APPROVE", "reviewer", approval.reference
    ).pk


@pytest.mark.django_db
def test_semantic_context_reuses_durable_akb_package_with_provenance() -> None:
    project = _project("semantic-foundation")
    entry_id = _active_entry(
        project,
        "semantic:source",
        is_must_know=True,
        work_context_id="work:semantic",
        role_context=["ENGINEERING"],
    )

    result = build_semantic_context(
        project,
        work_context_id="work:semantic",
        role_context_id="ENGINEERING",
        retrieval_intent="reasoning-context",
        retrieval_query="provenance",
    )

    assert result.selection_strategy == SELECTION_STRATEGY
    assert (
        KnowledgeContextPackage.objects.get(pk=result.package_id).package_hash
        == result.package_hash
    )
    source = next(item for item in result.sources if item.entry_id == entry_id)
    assert set(source.selection_reasons) == {
        "PROJECT_MUST_KNOW",
        "WORK_CONTEXT",
        "ROLE_CONTEXT",
        "LEXICAL_QUERY_MATCH",
    }


@pytest.mark.django_db
def test_semantic_context_is_idempotent_and_project_isolated() -> None:
    project = _project("semantic-local")
    foreign = _project("semantic-foreign")
    _active_entry(project, "semantic:local", is_must_know=True)

    first = build_semantic_context(
        project,
        work_context_id="work:local",
        role_context_id="",
        retrieval_intent="behaviour-context",
    )
    second = build_semantic_context(
        project,
        work_context_id="work:local",
        role_context_id="",
        retrieval_intent="behaviour-context",
    )
    isolated = build_semantic_context(
        foreign,
        work_context_id="work:local",
        role_context_id="",
        retrieval_intent="behaviour-context",
    )

    assert first.package_id == second.package_id
    assert first.package_hash == second.package_hash
    assert isolated.sources == ()
    assert isolated.package_hash != first.package_hash


def test_semantic_context_contract_has_no_decision_or_runtime_authority() -> None:
    assert set(SemanticContext.__dataclass_fields__) == {
        "package_id",
        "package_hash",
        "retrieval_intent",
        "retrieval_query",
        "selection_strategy",
        "sources",
        "stale_warnings",
        "conflict_warnings",
    }

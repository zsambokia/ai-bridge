"""Sprint 02 acceptance: governed AKB -> index -> ranked RAG candidates."""

from __future__ import annotations

import pytest

from projects.knowledge import create_or_upsert_candidate, review_candidate
from projects.models import GovernanceApproval, Project, SemanticEmbedding
from projects.semantic import (
    DjangoVectorStore,
    RetrievalService,
    SemanticContextBuilder,
)


def _project(name: str) -> Project:
    return Project.objects.create(
        project_id=name,
        display_name=name,
        repository_full_name=f"test/{name}",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _active(
    project: Project, key: str, title: str, content: str, kind: str = "SYSTEM_DESIGN"
) -> None:
    entry = create_or_upsert_candidate(
        project,
        {
            "entry_key": key,
            "scope": "PROJECT",
            "knowledge_type": kind,
            "title": title,
            "content": content,
            "source_type": "TEST",
            "source_reference": key,
            "evidence_references": [key],
        },
        "test",
    )
    approval = GovernanceApproval.objects.create(
        reference=f"approve:{key}",
        project=project,
        approved_action="AKB_PUBLISH",
        approved_by="PO",
    )
    review_candidate(project, entry.pk, "APPROVE", "tester", approval.reference)


@pytest.mark.django_db
def test_index_cache_ranking_evidence_and_project_isolation() -> None:
    project, foreign = (
        _project("semantic-intelligence"),
        _project("semantic-foreign-index"),
    )
    _active(
        project,
        "semantic:vector",
        "Vector retrieval",
        "Vector embeddings retrieve relevant knowledge with similarity search.",
    )
    _active(foreign, "semantic:foreign", "Foreign secret", "foreign isolated knowledge")
    store = DjangoVectorStore()
    assert store.index_project(project) == {"indexed": 1, "cached": 0, "eligible": 1}
    assert store.index_project(project)["cached"] == 1
    results = store.search(project, "how do vector embeddings retrieve knowledge?")
    assert [item.metadata["entry_key"] for item in results] == ["semantic:vector"]
    assert results[0].reason == "COSINE_SIMILARITY"
    assert (
        results[0].evidence["embedding_id"]
        == SemanticEmbedding.objects.get().embedding_id
    )


@pytest.mark.django_db
def test_rag_filter_and_context_budget_only_return_candidates() -> None:
    project = _project("semantic-context-v2")
    _active(
        project,
        "semantic:architecture",
        "Semantic architecture",
        "semantic retrieval architecture",
        "ARCHITECTURE_DECISION",
    )
    _active(project, "semantic:design", "Other design", "unrelated design")
    store = DjangoVectorStore()
    store.index_project(project)
    retrieval = RetrievalService()
    candidates = retrieval.retrieve(project, "semantic", domain="ARCHITECTURE_DECISION")
    assert [item.metadata["entry_key"] for item in candidates] == [
        "semantic:architecture"
    ]
    context = SemanticContextBuilder(retrieval).build(
        project,
        "semantic architecture",
        runtime_state={"state": "READ_ONLY"},
        token_budget=20,
    )
    assert context.runtime_state == {"state": "READ_ONLY"}
    assert "Semantic architecture" in context.text
    assert context.evidence and "embedding_id" in context.evidence[0]

"""Sprint 02 acceptance: governed AKB -> index -> ranked RAG candidates."""

from __future__ import annotations

from uuid import uuid4

import pytest

from projects.cognitive_evolution import (
    build_guidance,
    govern_behaviour,
    propose_behaviour,
    record_experience,
)
from projects.decision_contract.framework import (
    CONTRACT_VERSION,
    DecisionEvidence,
    DecisionPlanItem,
    ExecutionRequest,
)
from projects.knowledge import create_or_upsert_candidate, review_candidate
from projects.knowledge_pipeline import KnowledgePipeline
from projects.models import (
    GovernanceApproval,
    KnowledgeContextPackage,
    KnowledgeEntry,
    KnowledgeRevision,
    Project,
    RuntimeKnowledgeCandidate,
    RuntimeReflectionCandidate,
    SemanticEmbedding,
)
from projects.orki_runtime import (
    execute_structured_decision,
    start_structured_decision_execution,
)
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


def _runtime_from_context(
    project: Project, package: KnowledgeContextPackage
) -> tuple[RuntimeReflectionCandidate, RuntimeKnowledgeCandidate]:
    """Execute the frozen Runtime with the retrieval package's evidence projection."""
    request = ExecutionRequest(
        contract_version=CONTRACT_VERSION,
        decision_id=uuid4(),
        goal="Calculate the shipping containers needed for the order.",
        plan=(DecisionPlanItem("calculate", "Calculate containers", (), "Verified"),),
        required_capabilities=(),
        required_tools=(),
        required_workflows=(),
        evidence=DecisionEvidence(
            knowledge_entry_ids=tuple(package.entry_ids),
            embedding_hits=tuple(
                {
                    "entry_id": item["entry_id"],
                    "score": item["score"],
                }
                for item in package.payload["candidates"]
            ),
            behaviour="ENGINEERING",
            plan_identifiers=("calculate",),
            critic_observations=(),
        ),
    )
    execution = start_structured_decision_execution(project, request, actor="mvp-proof")
    execute_structured_decision(
        str(execution.token),
        actor="mvp-proof",
        operation=lambda: {
            "verification": {"passed": True},
            "reflection_candidate": {
                "summary": "Container calculation was verified.",
                "reflection_text": "The approved container rule was applied unchanged.",
                "confidence": 0.95,
            },
            "knowledge_candidate": {
                "title": "Container calculation runtime lesson",
                "summary": "Verified container calculation completed.",
                "body": "The Runtime emitted a candidate and did not mutate AKB.",
                "reason": "MVP reproducibility proof.",
                "confidence": 0.95,
                "tags": ["runtime", "container"],
            },
            "evidence_references": ["mvp-proof:container-calculator"],
        },
    )
    return (
        RuntimeReflectionCandidate.objects.get(execution=execution),
        RuntimeKnowledgeCandidate.objects.get(execution=execution),
    )


@pytest.mark.django_db
def test_mvp_proof_semantic_layer_can_be_destroyed_and_reconstructed_from_akb() -> None:
    """Phase 10: AKB survives semantic deletion and reproduces retrieval behaviour."""
    project = _project("mvp-proof-reproducibility")
    _active(
        project,
        "container:calculation",
        "Shipping container calculation",
        (
            "Calculate containers by dividing the shipment volume by the usable "
            "container capacity and rounding up."
        ),
        "RUNBOOK",
    )
    _active(
        project,
        "container:validation",
        "Container capacity validation",
        (
            "Validate usable capacity and shipment volume before calculating "
            "shipping containers."
        ),
        "RUNBOOK",
    )
    store = DjangoVectorStore()
    pipeline = KnowledgePipeline(store)
    assert store.index_project(project) == {"indexed": 2, "cached": 0, "eligible": 2}

    query = "How do we calculate shipping containers?"
    baseline = pipeline.retrieve_context(
        project,
        work_context_id="mvp-proof:container-calculator",
        role_context_id="ENGINEERING",
        query=query,
    )
    baseline_payload = baseline.payload
    baseline_entry_ids = baseline.entry_ids
    baseline_embedding_ids = [
        item["evidence"]["embedding_id"] for item in baseline_payload["candidates"]
    ]
    akb_snapshot = list(
        KnowledgeEntry.objects.filter(project=project)
        .order_by("pk")
        .values("pk", "entry_key", "content", "status", "version", "approval_reference")
    )
    revision_snapshot = list(
        KnowledgeRevision.objects.filter(entry__project=project)
        .order_by("entry_id", "new_version")
        .values("entry_id", "new_version", "content_snapshot", "approval_reference")
    )
    approval_count = GovernanceApproval.objects.filter(project=project).count()
    baseline_reflection, baseline_candidate = _runtime_from_context(project, baseline)

    # Test-only destructive phase: derived retrieval artifacts disappear; AKB does not.
    SemanticEmbedding.objects.filter(entry__project=project).delete()
    KnowledgeContextPackage.objects.filter(project=project).delete()
    assert not SemanticEmbedding.objects.filter(entry__project=project).exists()
    assert not KnowledgeContextPackage.objects.filter(project=project).exists()
    assert (
        list(
            KnowledgeEntry.objects.filter(project=project)
            .order_by("pk")
            .values(
                "pk", "entry_key", "content", "status", "version", "approval_reference"
            )
        )
        == akb_snapshot
    )
    assert (
        list(
            KnowledgeRevision.objects.filter(entry__project=project)
            .order_by("entry_id", "new_version")
            .values("entry_id", "new_version", "content_snapshot", "approval_reference")
        )
        == revision_snapshot
    )
    assert GovernanceApproval.objects.filter(project=project).count() == approval_count

    assert store.index_project(project) == {"indexed": 2, "cached": 0, "eligible": 2}
    rebuilt = pipeline.retrieve_context(
        project,
        work_context_id="mvp-proof:container-calculator",
        role_context_id="ENGINEERING",
        query=query,
    )
    assert rebuilt.package_hash == baseline.package_hash
    assert rebuilt.entry_ids == baseline_entry_ids
    assert rebuilt.payload == baseline_payload
    assert [
        item["evidence"]["embedding_id"] for item in rebuilt.payload["candidates"]
    ] == baseline_embedding_ids

    rebuilt_reflection, rebuilt_candidate = _runtime_from_context(project, rebuilt)
    assert rebuilt_reflection.summary == baseline_reflection.summary
    assert rebuilt_reflection.reflection_text == baseline_reflection.reflection_text
    assert (
        rebuilt_reflection.verification_result
        == baseline_reflection.verification_result
    )
    assert rebuilt_candidate.title == baseline_candidate.title
    assert rebuilt_candidate.summary == baseline_candidate.summary
    assert rebuilt_candidate.body == baseline_candidate.body

    for number, reflection in enumerate(
        (baseline_reflection, rebuilt_reflection), start=1
    ):
        experience = record_experience(project, reflection)
        behaviour = propose_behaviour(
            project,
            experience,
            strategy_key="verified-container-calculation",
            guidance="Use approved capacity evidence before calculating containers.",
            applicability=["engineering", "shipping"],
            actor="mvp-proof",
        )
        approval = GovernanceApproval.objects.create(
            reference=f"mvp-proof-behaviour-{number}",
            project=project,
            approved_action="cognitive_evolution.govern_behaviour",
            approved_by="PO",
        )
        govern_behaviour(
            project,
            behaviour,
            decision="APPROVE",
            actor="PO",
            approval_reference=approval.reference,
        )
    guidance = build_guidance(project, query=query)
    assert len(guidance.candidate_ids) == 2
    assert {pattern["strategy_key"] for pattern in guidance.patterns} == {
        "verified-container-calculation"
    }
    assert guidance.metrics["approved_pattern_count"] == 2

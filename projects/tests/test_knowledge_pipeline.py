"""Sprint 06 acceptance for the independent Runtime candidate -> AKB pipeline."""

from __future__ import annotations

from uuid import uuid4

import pytest

from projects.decision_contract.framework import (
    CONTRACT_VERSION,
    DecisionEvidence,
    DecisionPlanItem,
    ExecutionRequest,
)
from projects.knowledge_pipeline import KnowledgePipeline
from projects.models import (
    GovernanceApproval,
    KnowledgeEntry,
    KnowledgePipelineReceipt,
    Project,
    RuntimeKnowledgeCandidate,
    SemanticEmbedding,
)
from projects.orki_runtime import (
    execute_structured_decision,
    start_structured_decision_execution,
)


def _project() -> Project:
    return Project.objects.create(
        project_id="knowledge-pipeline",
        display_name="Knowledge Pipeline",
        repository_full_name="example/knowledge-pipeline",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _runtime_candidate(
    project: Project, *, tags: list[str] | None = None
) -> RuntimeKnowledgeCandidate:
    request = ExecutionRequest(
        contract_version=CONTRACT_VERSION,
        decision_id=uuid4(),
        goal="Create reusable runtime knowledge.",
        plan=(DecisionPlanItem("verify", "Verify", (), "Verified"),),
        required_capabilities=(),
        required_tools=(),
        required_workflows=(),
        evidence=DecisionEvidence(
            knowledge_entry_ids=(),
            embedding_hits=(),
            behaviour="ENGINEERING",
            plan_identifiers=("verify",),
            critic_observations=(),
        ),
    )
    execution = start_structured_decision_execution(project, request, actor="test")
    execute_structured_decision(
        str(execution.token),
        actor="test",
        operation=lambda: {
            "verification": {"passed": True},
            "reflection_candidate": {
                "summary": "Verification completed.",
                "reflection_text": "The evidence is reusable.",
                "confidence": 0.9,
            },
            "knowledge_candidate": {
                "title": "Vector retrieval lesson",
                "summary": "Semantic retrieval uses active knowledge embeddings.",
                "body": (
                    "Promoted knowledge is embedded only after governed activation."
                ),
                "reason": "The verified execution provides reusable evidence.",
                "confidence": 0.9,
                "tags": tags or ["runtime", "knowledge_type:runbook"],
            },
            "evidence_references": ["runtime:test-proof"],
        },
    )
    return RuntimeKnowledgeCandidate.objects.get(execution=execution)


@pytest.mark.django_db
def test_pipeline_requires_governed_promotion_then_indexes_and_retrieves() -> None:
    project = _project()
    candidate = _runtime_candidate(project)
    pipeline = KnowledgePipeline()

    review = pipeline.process(candidate, actor="pipeline")
    assert review.status == KnowledgePipelineReceipt.Status.IN_REVIEW
    assert review.knowledge_entry_id is not None
    entry = KnowledgeEntry.objects.get(pk=review.knowledge_entry_id)
    assert entry.status == KnowledgeEntry.Status.IN_REVIEW
    assert entry.knowledge_type == "RUNBOOK"
    assert not SemanticEmbedding.objects.exists()

    approval = GovernanceApproval.objects.create(
        reference="knowledge-pipeline-approval",
        project=project,
        approved_action="akb.review_candidate",
        approved_by="PO",
    )
    promoted = pipeline.process(
        candidate,
        actor="pipeline",
        decision="APPROVE",
        approval_reference=approval.reference,
    )
    promoted_again = pipeline.process(
        candidate,
        actor="pipeline",
        decision="APPROVE",
        approval_reference=approval.reference,
    )
    entry.refresh_from_db()
    assert promoted.status == KnowledgePipelineReceipt.Status.PROMOTED
    assert promoted_again == promoted
    assert entry.status == KnowledgeEntry.Status.ACTIVE
    assert promoted.embedding_id
    assert SemanticEmbedding.objects.filter(entry=entry).exists()
    assert [item["event"] for item in promoted.evidence] == [
        "VALIDATED",
        "CANDIDATE_CREATED",
        "REVIEW_REQUESTED",
        "PROMOTED",
    ]

    package = pipeline.retrieve_context(
        project,
        work_context_id="runtime-execution:test",
        role_context_id="ENGINEERING",
        query="how are active knowledge embeddings retrieved?",
    )
    assert package.entry_ids == [entry.pk]
    assert package.payload["retrieval_strategy"] == "SEMANTIC_VECTOR"
    assert (
        package.payload["candidates"][0]["evidence"]["embedding_id"]
        == promoted.embedding_id
    )


@pytest.mark.django_db
def test_pipeline_deduplicates_content_without_second_akb_or_vector_mutation() -> None:
    project = _project()
    pipeline = KnowledgePipeline()
    first = _runtime_candidate(project)
    second = _runtime_candidate(project)

    first_outcome = pipeline.process(first, actor="pipeline")
    duplicate = pipeline.process(second, actor="pipeline")

    assert first_outcome.status == KnowledgePipelineReceipt.Status.IN_REVIEW
    assert duplicate.status == KnowledgePipelineReceipt.Status.DUPLICATE
    assert duplicate.duplicate is True
    assert duplicate.knowledge_entry_id == first_outcome.knowledge_entry_id
    assert KnowledgeEntry.objects.count() == 1
    assert SemanticEmbedding.objects.count() == 0
    assert duplicate.evidence[-1]["event"] == "DEDUPLICATED"


@pytest.mark.django_db
def test_pipeline_rejects_unapproved_promotion_without_activating_knowledge() -> None:
    project = _project()
    candidate = _runtime_candidate(project, tags=["runtime"])
    pipeline = KnowledgePipeline()
    pipeline.process(candidate, actor="pipeline")

    with pytest.raises(ValueError, match="APPROVAL_REQUIRED"):
        pipeline.process(candidate, actor="pipeline", decision="APPROVE")

    entry = KnowledgeEntry.objects.get()
    assert entry.status == KnowledgeEntry.Status.IN_REVIEW
    assert entry.knowledge_type == "GENERAL"
    assert not SemanticEmbedding.objects.exists()

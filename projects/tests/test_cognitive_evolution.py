"""Acceptance coverage for Sprint 07 Cognitive & Behaviour Evolution."""

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
from projects.models import (
    BehaviourCandidate,
    GovernanceApproval,
    Project,
    RuntimeCandidateImmutableError,
    RuntimeReflectionCandidate,
)
from projects.orki_runtime import (
    execute_structured_decision,
    start_structured_decision_execution,
)


def _project(project_id: str = "cognitive-evolution") -> Project:
    return Project.objects.create(
        project_id=project_id,
        display_name="Cognitive Evolution",
        repository_full_name=f"example/{project_id}",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )


def _reflection(project: Project, *, passed: bool = True) -> RuntimeReflectionCandidate:
    request = ExecutionRequest(
        contract_version=CONTRACT_VERSION,
        decision_id=uuid4(),
        goal="Verify governed cognitive learning.",
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
            "verification": {"passed": passed},
            "reflection_candidate": {
                "summary": "Governed verification completed.",
                "reflection_text": (
                    "Evidence must be reviewed before behavioural reuse."
                ),
                "confidence": 0.9,
            },
            "knowledge_candidate": {
                "title": "Unrelated knowledge candidate",
                "summary": "Sprint seven does not process this knowledge candidate.",
                "body": "Knowledge pipeline ownership remains frozen.",
                "reason": "Boundary test.",
                "confidence": 0.9,
                "tags": ["boundary"],
            },
            "evidence_references": ["runtime:cognitive-proof"],
        },
    )
    return RuntimeReflectionCandidate.objects.get(execution=execution)


@pytest.mark.django_db
def test_canonical_cognitive_e2e_requires_explicit_governance() -> None:
    project = _project()
    reflection = _reflection(project)

    experience = record_experience(project, reflection)
    assert record_experience(project, reflection).pk == experience.pk
    candidate = propose_behaviour(
        project,
        experience,
        strategy_key="evidence-first-review",
        guidance="Require verified evidence before reusing an execution lesson.",
        applicability=["engineering", "governance"],
        actor="reflection-evaluator",
    )
    assert candidate.status == BehaviourCandidate.Status.CANDIDATE
    assert build_guidance(project, query="engineering").candidate_ids == ()

    with pytest.raises(ValueError, match="BEHAVIOUR_GOVERNANCE_APPROVAL_REQUIRED"):
        govern_behaviour(
            project,
            candidate,
            decision="APPROVE",
            actor="PO",
            approval_reference="missing",
        )

    approval = GovernanceApproval.objects.create(
        reference="cognitive-behaviour-approval",
        project=project,
        approved_action="cognitive_evolution.govern_behaviour",
        approved_by="PO",
    )
    approved = govern_behaviour(
        project,
        candidate,
        decision="APPROVE",
        actor="PO",
        approval_reference=approval.reference,
    )
    assert approved.status == BehaviourCandidate.Status.APPROVED
    assert (
        govern_behaviour(
            project,
            candidate,
            decision="APPROVE",
            actor="PO",
            approval_reference=approval.reference,
        ).pk
        == candidate.pk
    )

    guidance = build_guidance(project, query="not-a-selector")
    assert guidance.candidate_ids == (candidate.pk,)
    assert guidance.patterns[0]["strategy_key"] == "evidence-first-review"
    assert guidance.evidence[0]["approval_reference"] == approval.reference
    assert guidance.metrics["experience_count"] == 1
    assert guidance.metrics["approved_pattern_count"] == 1

    candidate.guidance = "Mutable runtime instruction"
    with pytest.raises(RuntimeCandidateImmutableError):
        candidate.save()


@pytest.mark.django_db
def test_cognitive_inputs_and_guidance_are_project_isolated() -> None:
    project = _project()
    other_project = _project("cognitive-evolution-other")
    reflection = _reflection(project)

    with pytest.raises(ValueError, match="COGNITIVE_EXPERIENCE_PROJECT_MISMATCH"):
        record_experience(other_project, reflection)

    experience = record_experience(project, reflection)
    candidate = propose_behaviour(
        project,
        experience,
        strategy_key="verified-review",
        guidance="Keep behavioural evidence attributable.",
        applicability=["engineering"],
        actor="reflection-evaluator",
    )
    approval = GovernanceApproval.objects.create(
        reference="cognitive-isolation-approval",
        project=project,
        approved_action="cognitive_evolution.govern_behaviour",
        approved_by="PO",
    )
    govern_behaviour(
        project,
        candidate,
        decision="APPROVE",
        actor="PO",
        approval_reference=approval.reference,
    )

    assert build_guidance(other_project).candidate_ids == ()
    with pytest.raises(ValueError, match="BEHAVIOUR_GOVERNANCE_PROJECT_MISMATCH"):
        govern_behaviour(
            other_project,
            candidate,
            decision="APPROVE",
            actor="PO",
            approval_reference=approval.reference,
        )

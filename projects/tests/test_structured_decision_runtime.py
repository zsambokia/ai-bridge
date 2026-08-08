"""Sprint 05 canonical StructuredDecision-to-Runtime acceptance coverage."""

from uuid import uuid4

from django.test import TestCase

from projects.decision_contract.framework import (
    CONTRACT_VERSION,
    DecisionEvidence,
    DecisionPlanItem,
    ExecutionRequest,
)
from projects.models import (
    KnowledgeEntry,
    OrkiExecution,
    Project,
    RuntimeKnowledgeCandidate,
)
from projects.orki_runtime import (
    execute_structured_decision,
    execution_projection,
    recover_structured_decision,
    start_structured_decision_execution,
)


class StructuredDecisionRuntimeTests(TestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(
            project_id="sprint-05-runtime",
            display_name="Sprint 05 Runtime",
            repository_full_name="example/sprint-05-runtime",
            definition_path="projects/sprint-05-runtime.yaml",
            repository_root="C:/workspace/sprint-05-runtime",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        self.request = ExecutionRequest(
            contract_version=CONTRACT_VERSION,
            decision_id=uuid4(),
            goal="Create a verified Runtime artifact.",
            plan=(
                DecisionPlanItem("write", "Write artifact", (), "Artifact exists"),
                DecisionPlanItem("verify", "Verify artifact", ("write",), "Read back"),
            ),
            required_capabilities=("filesystem",),
            required_tools=("workspace",),
            required_workflows=("engineering",),
            evidence=DecisionEvidence(
                knowledge_entry_ids=(1,),
                embedding_hits=({"entry_id": 1, "score": 0.9},),
                behaviour="ENGINEERING",
                plan_identifiers=("write", "verify"),
                critic_observations=("approved",),
            ),
        )

    def test_canonical_path_completes_without_akb_mutation(self) -> None:
        execution = start_structured_decision_execution(
            self.project, self.request, actor="runtime-test"
        )
        self.assertEqual(execution.state, OrkiExecution.State.READY)
        self.assertEqual(execution.plan.contract_version, CONTRACT_VERSION)
        self.assertTrue(execution.plan.plan_hash)

        execution = execute_structured_decision(
            str(execution.token),
            actor="runtime-test",
            operation=lambda: {
                "verification": {"passed": True},
                "reflection_candidate": {
                    "summary": "The artifact was verified.",
                    "reflection_text": "Verification evidence confirms the goal.",
                    "confidence": 0.95,
                },
                "knowledge_candidate": {
                    "title": "Candidate only",
                    "summary": "A verified Runtime artifact.",
                    "body": "The artifact exists and was read back successfully.",
                    "reason": "Reusable execution evidence.",
                    "confidence": 0.9,
                    "tags": ["runtime", "verification"],
                },
                "evidence_references": ["artifact:runtime-proof"],
            },
        )
        self.assertEqual(execution.state, OrkiExecution.State.COMPLETED)
        self.assertEqual(execution.plan.goal.status, "ACHIEVED")
        self.assertTrue(
            RuntimeKnowledgeCandidate.objects.filter(execution=execution).exists()
        )
        self.assertFalse(KnowledgeEntry.objects.filter(project=self.project).exists())
        projection = execution_projection(execution)
        self.assertEqual(projection["behaviour"], "ENGINEERING")
        self.assertEqual(projection["stage"], OrkiExecution.State.COMPLETED)
        self.assertEqual(projection["provider"], "runtime-operation-gateway")
        self.assertEqual(projection["knowledge_integration_status"], "NOT_REQUIRED")
        self.assertEqual(
            set(execution.events.values_list("event_type", flat=True)),
            {
                "GoalCreated",
                "PlanningStarted",
                "PlanningCompleted",
                "STATE_TRANSITION",
                "ExecutionStarted",
                "TaskStarted",
                "ProviderStarted",
                "ProviderCompleted",
                "TaskCompleted",
                "VerificationStarted",
                "VerificationCompleted",
                "ReflectionStarted",
                "ReflectionCompleted",
                "KnowledgeCandidateCreated",
                "GoalCompleted",
                "Finished",
            },
        )

    def test_failed_execution_is_recoverable_and_retries(self) -> None:
        execution = start_structured_decision_execution(
            self.project, self.request, actor="runtime-test"
        )
        execution = execute_structured_decision(
            str(execution.token),
            actor="runtime-test",
            operation=lambda: (_ for _ in ()).throw(RuntimeError("temporary")),
        )
        self.assertEqual(execution.state, OrkiExecution.State.FAILED)
        execution = recover_structured_decision(
            str(execution.token), actor="runtime-test"
        )
        self.assertEqual(execution.state, OrkiExecution.State.RETRYING)

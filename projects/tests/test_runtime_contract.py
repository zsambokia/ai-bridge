"""Sprint 05.1 regression tests for pure, immutable Runtime candidates."""

from dataclasses import replace
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
    Project,
    RuntimeKnowledgeCandidate,
    RuntimeReflectionCandidate,
)
from projects.orki_runtime import (
    execute_structured_decision,
    start_structured_decision_execution,
)
from projects.runtime_contract import (
    RUNTIME_CANDIDATE_SCHEMA_VERSION,
    RuntimeCandidateImmutableError,
    RuntimeCandidateValidationError,
)


class RuntimeCandidateContractTests(TestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(
            project_id="runtime-contract",
            display_name="Runtime Contract",
            repository_full_name="example/runtime-contract",
            definition_path="projects/runtime-contract.yaml",
            repository_root="C:/workspace/runtime-contract",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        self.request = ExecutionRequest(
            contract_version=CONTRACT_VERSION,
            decision_id=uuid4(),
            goal="Produce a pure candidate.",
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

    def _operation(self, **knowledge_overrides: object) -> dict[str, object]:
        candidate: dict[str, object] = {
            "title": "Pure candidate",
            "summary": "A candidate without knowledge-pipeline ownership.",
            "body": "The Runtime only describes reusable execution evidence.",
            "reason": "The verified result may be useful later.",
            "confidence": 0.9,
            "tags": ["runtime", "pure"],
        }
        candidate.update(knowledge_overrides)
        return {
            "verification": {"passed": True},
            "reflection_candidate": {
                "summary": "Verification completed.",
                "reflection_text": "The operation supplied valid evidence.",
                "confidence": 0.95,
            },
            "knowledge_candidate": candidate,
            "evidence_references": ["runtime-contract:proof"],
        }

    def _execute(self, operation: dict[str, object]) -> RuntimeKnowledgeCandidate:
        execution = start_structured_decision_execution(
            self.project, self.request, actor="runtime-contract-test"
        )
        execute_structured_decision(
            str(execution.token),
            actor="runtime-contract-test",
            operation=lambda: operation,
        )
        return RuntimeKnowledgeCandidate.objects.get(execution=execution)

    def test_canonical_runtime_candidate_is_explicit_and_pure(self) -> None:
        candidate = self._execute(self._operation())
        reflection = candidate.reflection_candidate
        self.assertEqual(candidate.schema_version, RUNTIME_CANDIDATE_SCHEMA_VERSION)
        self.assertEqual(reflection.goal_id, candidate.execution.plan.goal.token)
        self.assertFalse(hasattr(candidate, "payload"))
        self.assertFalse(hasattr(reflection, "payload"))
        self.assertEqual(candidate.tags, ["runtime", "pure"])
        self.assertFalse(KnowledgeEntry.objects.filter(project=self.project).exists())

    def test_forbidden_knowledge_pipeline_fields_are_rejected(self) -> None:
        for field in ("embedding", "knowledge_entry_id", "vector_id", "activation"):
            with self.subTest(field=field):
                self.request = replace(self.request, decision_id=uuid4())
                execution = start_structured_decision_execution(
                    self.project, self.request, actor=f"runtime-contract-{field}"
                )
                invalid_operation = self._operation(**{field: "x"})
                with self.assertRaisesRegex(
                    RuntimeCandidateValidationError,
                    f"RUNTIME_CANDIDATE_FORBIDDEN_FIELD:{field}",
                ):
                    execute_structured_decision(
                        str(execution.token),
                        actor=f"runtime-contract-{field}",
                        operation=lambda: invalid_operation,
                    )

    def test_candidates_are_immutable_after_creation(self) -> None:
        candidate = self._execute(self._operation())
        candidate.title = "Changed"
        with self.assertRaisesRegex(
            RuntimeCandidateImmutableError, "RUNTIME_CANDIDATE_IMMUTABLE"
        ):
            candidate.save()
        reflection = RuntimeReflectionCandidate.objects.get(
            pk=candidate.reflection_candidate_id
        )
        reflection.summary = "Changed"
        with self.assertRaisesRegex(
            RuntimeCandidateImmutableError, "RUNTIME_CANDIDATE_IMMUTABLE"
        ):
            reflection.save()

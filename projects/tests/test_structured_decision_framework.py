from __future__ import annotations

from copy import deepcopy

from django.test import TestCase

from projects.decision_contract import (
    CONTRACT_VERSION,
    DecisionValidator,
    StructuredDecisionBuilder,
    StructuredDecisionV1,
    to_execution_request,
)
from projects.reasoning import ReasoningFramework
from projects.semantic import SemanticCandidate, SemanticContextV2


def semantic_context() -> SemanticContextV2:
    candidate = SemanticCandidate(
        entry_id=41,
        score=0.92,
        reason="COSINE_SIMILARITY",
        metadata={"title": "Container application architecture"},
        evidence={"embedding_id": "embedding-41", "provider": "LOCAL_HASH"},
        content="A container tracking application uses a bounded API design.",
    )
    return SemanticContextV2(
        "Create a container tracking application",
        {
            "repository_available": True,
            "project_available": True,
            "bootstrap_ready": True,
        },
        (candidate,),
        candidate.content,
        (candidate.evidence,),
    )


def valid_contract() -> StructuredDecisionV1:
    context = semantic_context()
    internal = ReasoningFramework().decide(context)
    return StructuredDecisionBuilder().build(
        internal,
        context,
        required_capabilities=("APPLICATION_DELIVERY",),
        required_tools=("REPOSITORY",),
        required_workflows=("IMPLEMENTATION",),
    )


class StructuredDecisionFrameworkTests(TestCase):
    def test_canonical_pipeline_stops_at_validated_contract(self) -> None:
        contract = valid_contract()
        validation = DecisionValidator().validate(contract)
        request = to_execution_request(contract, validation)

        self.assertTrue(validation.valid)
        self.assertEqual(contract.contract_version, CONTRACT_VERSION)
        self.assertEqual(contract.intent, "new_application")
        self.assertEqual(contract.evidence.knowledge_entry_ids, (41,))
        self.assertEqual(contract.evidence.embedding_hits[0]["entry_id"], 41)
        self.assertEqual(request.decision_id, contract.decision_id)
        self.assertFalse(hasattr(request, "dispatch"))

    def test_confidence_and_evidence_are_complete(self) -> None:
        contract = valid_contract()

        self.assertGreaterEqual(contract.confidence.overall, 0.7)
        self.assertEqual(contract.confidence.semantic, 0.92)
        self.assertGreater(contract.confidence.reasoning, 0)
        self.assertEqual(contract.confidence.critic, 1.0)
        self.assertEqual(contract.evidence.behaviour, contract.behaviour)
        self.assertEqual(
            contract.evidence.plan_identifiers,
            tuple(item.identifier for item in contract.plan),
        )

    def test_validator_returns_reasoning_repair_feedback(self) -> None:
        contract = valid_contract()
        broken = deepcopy(contract)
        object.__setattr__(broken, "goal", "")
        object.__setattr__(broken, "plan", ())
        object.__setattr__(broken, "required_capabilities", ())
        validation = DecisionValidator().validate(broken)

        self.assertFalse(validation.valid)
        self.assertIn("MISSING_GOAL", validation.errors)
        self.assertIn("MISSING_PLAN", validation.errors)
        self.assertIn("MISSING_CAPABILITIES", validation.errors)
        self.assertIn("MISSING_GOAL", validation.feedback)
        with self.assertRaisesRegex(ValueError, "DECISION_CONTRACT_INVALID"):
            to_execution_request(broken, validation)

    def test_decision_api_is_contract_only_and_auditable(self) -> None:
        payload = {
            "goal": "Create a container tracking application",
            "runtime_state": {
                "repository_available": True,
                "project_available": True,
                "bootstrap_ready": True,
            },
            "candidates": [
                {
                    "entry_id": 41,
                    "score": 0.92,
                    "content": (
                        "A container tracking application uses a bounded API design."
                    ),
                    "metadata": {"title": "Container application architecture"},
                    "evidence": {"embedding_id": "embedding-41"},
                }
            ],
            "required_capabilities": ["APPLICATION_DELIVERY"],
            "required_tools": ["REPOSITORY"],
            "required_workflows": ["IMPLEMENTATION"],
        }
        created = self.client.post(
            "/reasoning/decision", data=payload, content_type="application/json"
        )

        self.assertEqual(created.status_code, 201)
        created_payload = created.json()
        self.assertTrue(created_payload["validation"]["valid"])
        self.assertEqual(
            created_payload["decision"]["contract_version"], CONTRACT_VERSION
        )
        decision_id = created_payload["decision"]["decision_id"]
        detail = self.client.get(f"/reasoning/decision/{decision_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["decision"]["decision_id"], decision_id)
        schema = self.client.get("/reasoning/schema")
        self.assertEqual(schema.status_code, 200)
        self.assertEqual(schema.json()["execution"], "forbidden")

    def test_invalid_api_contract_returns_repair_feedback_without_audit(self) -> None:
        payload = {
            "goal": "Review container application",
            "runtime_state": {"repository_available": True, "project_available": True},
            "candidates": [
                {"entry_id": 41, "score": 0.92, "content": "architecture evidence"}
            ],
            "required_capabilities": [],
        }
        response = self.client.post(
            "/reasoning/decision", data=payload, content_type="application/json"
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("MISSING_CAPABILITIES", response.json()["validation"]["errors"])

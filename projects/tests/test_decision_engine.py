"""Independent capability scenarios for ORKI-004 Decision Intelligence."""

from __future__ import annotations

from django.test import TestCase

from projects.decision_engine import accept_decision, decision_projection, open_decision
from projects.mission_understanding import record_mission_understanding
from projects.models import CognitiveStateEntry, Project
from projects.recommendation_engine import record_recommendation


class DecisionEngineTests(TestCase):
    def setUp(self) -> None:
        self.primary = self._project("decision-primary")
        self.secondary = self._project("decision-secondary")
        self._prepare_material_recommendation(self.primary)

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
        )

    @staticmethod
    def _conversation_source(message_id: int) -> dict[str, object]:
        return {
            "source_type": "TEST_DECISION_OBSERVATION",
            "conversation_message_id": message_id,
            "conversation_message_sha256": f"sha256-{message_id}",
        }

    @staticmethod
    def _owner_source(reference: str = "po-confirmation-1") -> dict[str, object]:
        return {
            "source_type": "PRODUCT_OWNER_CONFIRMATION",
            "actor_type": "PRODUCT_OWNER",
            "actor_id": "owner@example.test",
            "confirmation_reference": reference,
        }

    @staticmethod
    def _mission() -> dict[str, object]:
        return {
            "stated_intent": "Make stockout risk visible earlier",
            "inferred_business_goal": "Reduce lost revenue from stockouts",
            "inference_confidence": 0.78,
            "stated_constraints": ["First release has read-only ERP access"],
            "solution_proposals": ["Stockout forecasting"],
            "technology_preferences": ["ERP API"],
            "safe_assumptions": ["Historical order data is available"],
            "material_unknowns": [],
            "question": None,
        }

    @staticmethod
    def _recommendation(*, material: bool = True) -> dict[str, object]:
        return {
            "recommendation_key": "read-only-pilot",
            "priority": "HIGH",
            "recommendation": "Start with a read-only stockout-risk pilot.",
            "rationale": "It proves value before operational write access.",
            "business_impact": "Earlier action reduces missed-sales exposure.",
            "dependencies": ["ERP API access"],
            "next_safe_action": "Validate the historical-order data contract.",
            "requires_product_owner_decision": material,
            "evidence_attributes": ["stated_intent", "inferred_business_goal"],
            "assumption_attributes": ["safe_assumptions"],
            "alternatives": [
                {"option": "Read-only pilot", "summary": "Low-risk evidence first."},
                {
                    "option": "Full ERP rollout",
                    "summary": "Broader scope before evidence.",
                },
            ],
            "trade_offs": [
                {
                    "option": "Read-only pilot",
                    "benefit": "Low risk",
                    "cost": "No writes",
                },
                {
                    "option": "Full ERP rollout",
                    "benefit": "Faster reach",
                    "cost": "Higher risk",
                },
            ],
            "confidence": 0.82,
        }

    @staticmethod
    def _decision() -> dict[str, object]:
        return {
            "decision_key": "pilot-scope",
            "recommendation_key": "read-only-pilot",
            "question": "Approve the read-only pilot as the first delivery scope?",
            "materiality_reason": (
                "The choice determines delivery risk and ERP permissions."
            ),
            "options": [
                {"option": "Read-only pilot", "summary": "Prove value safely."},
                {"option": "Full ERP rollout", "summary": "Broaden the initial scope."},
            ],
            "recommended_option": "Read-only pilot",
            "impact_if_decided": "The team can prepare the agreed scope.",
            "impact_if_deferred": "The pilot boundary remains ambiguous.",
        }

    def _prepare_material_recommendation(self, project: Project) -> None:
        record_mission_understanding(
            project,
            observation=self._mission(),
            provenance=self._conversation_source(1),
        )
        record_recommendation(
            project,
            observation=self._recommendation(),
            provenance=self._conversation_source(2),
        )

    def test_open_decision_is_explainable_and_evidence_bound(self) -> None:
        projection = open_decision(
            self.primary,
            observation=self._decision(),
            provenance=self._conversation_source(3),
        )
        entry = projection["decision:pilot-scope"]
        self.assertEqual(entry["kind"], CognitiveStateEntry.Kind.OPEN_DECISION)
        self.assertEqual(entry["confidence"], 0.82)
        self.assertEqual(len(entry["value"]["options"]), 2)
        self.assertEqual(len(entry["value"]["alternatives"]), 2)
        self.assertEqual(len(entry["value"]["trade_offs"]), 2)
        self.assertEqual(len(entry["value"]["evidence_entry_ids"]), 2)

    def test_non_material_recommendation_and_cross_project_state_are_rejected(
        self,
    ) -> None:
        self._prepare_material_recommendation(self.secondary)
        record_recommendation(
            self.secondary,
            observation=self._recommendation(material=False),
            provenance=self._conversation_source(4),
        )
        with self.assertRaisesMessage(ValueError, "DECISION_NOT_MATERIAL"):
            open_decision(
                self.secondary,
                observation=self._decision(),
                provenance=self._conversation_source(5),
            )
        with self.assertRaisesMessage(ValueError, "DECISION_OPEN_STALE_OR_UNAVAILABLE"):
            accept_decision(
                self.secondary,
                decision_key="pilot-scope",
                open_decision_entry_id=999999,
                selected_option="Read-only pilot",
                provenance=self._owner_source(),
            )

    def test_only_explicit_product_owner_confirmation_accepts_and_stale_is_rejected(
        self,
    ) -> None:
        opened = open_decision(
            self.primary,
            observation=self._decision(),
            provenance=self._conversation_source(3),
        )
        open_entry = opened["decision:pilot-scope"]
        with self.assertRaisesMessage(ValueError, "DECISION_ACCEPTANCE_SOURCE_INVALID"):
            accept_decision(
                self.primary,
                decision_key="pilot-scope",
                open_decision_entry_id=open_entry["id"],
                selected_option="Read-only pilot",
                provenance={**self._owner_source(), "source_type": "PROVIDER_RESPONSE"},
            )
        accepted = accept_decision(
            self.primary,
            decision_key="pilot-scope",
            open_decision_entry_id=open_entry["id"],
            selected_option="Read-only pilot",
            provenance=self._owner_source(),
        )
        result = accepted["decision:pilot-scope"]
        self.assertEqual(result["kind"], CognitiveStateEntry.Kind.ACCEPTED_DECISION)
        self.assertEqual(result["value"]["selected_option"], "Read-only pilot")
        with self.assertRaisesMessage(ValueError, "DECISION_OPEN_STALE_OR_UNAVAILABLE"):
            accept_decision(
                self.primary,
                decision_key="pilot-scope",
                open_decision_entry_id=open_entry["id"],
                selected_option="Read-only pilot",
                provenance=self._owner_source("po-confirmation-2"),
            )
        self.assertFalse(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.OPEN_DECISION,
                content__attribute="decision:pilot-scope",
                status=CognitiveStateEntry.Status.ACTIVE,
            ).exists()
        )
        self.assertEqual(len(decision_projection(self.primary)), 1)

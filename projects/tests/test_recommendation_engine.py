"""Independent capability scenarios for the ORKI-003 Recommendation Engine."""

from __future__ import annotations

from django.test import TestCase

from projects.mission_understanding import record_mission_understanding
from projects.models import CognitiveStateEntry, Project
from projects.recommendation_engine import (
    recommendation_projection,
    record_recommendation,
)


class RecommendationEngineTests(TestCase):
    def setUp(self) -> None:
        self.primary = self._project("recommendation-primary")
        self.secondary = self._project("recommendation-secondary")
        record_mission_understanding(
            self.primary,
            observation=self._mission_observation(),
            provenance=self._provenance(1),
        )

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
        )

    @staticmethod
    def _provenance(message_id: int) -> dict[str, object]:
        return {
            "source_type": "TEST_RECOMMENDATION_OBSERVATION",
            "conversation_message_id": message_id,
            "conversation_message_sha256": f"sha256-{message_id}",
        }

    @staticmethod
    def _mission_observation() -> dict[str, object]:
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
    def _observation(**overrides: object) -> dict[str, object]:
        observation: dict[str, object] = {
            "recommendation_key": "read-only-pilot",
            "priority": "HIGH",
            "recommendation": "Start with a read-only stockout-risk pilot.",
            "rationale": "It proves value before any operational write access.",
            "business_impact": "Earlier action reduces missed-sales exposure.",
            "dependencies": ["ERP API access"],
            "next_safe_action": "Validate the historical-order data contract.",
            "requires_product_owner_decision": False,
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
        observation.update(overrides)
        return observation

    def test_evidence_assumptions_alternatives_and_trade_offs_are_explainable(
        self,
    ) -> None:
        projection = record_recommendation(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(2),
        )
        result = projection["recommendation:read-only-pilot"]
        recommendation = result["recommendation"]
        self.assertEqual(recommendation["confidence"], 0.82)
        self.assertEqual(recommendation["value"]["priority"], "HIGH")
        self.assertEqual(len(result["evidence"]), 2)
        self.assertTrue(
            all(item["kind"] != "ASSUMPTION" for item in result["evidence"])
        )
        self.assertEqual(result["assumptions"][0]["kind"], "ASSUMPTION")
        self.assertEqual(len(result["alternatives"]["value"]), 2)
        self.assertEqual(len(result["trade_offs"]["value"]), 2)

    def test_recommendation_evolves_by_supersession_without_authority_leakage(
        self,
    ) -> None:
        record_recommendation(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(2),
        )
        evolved = self._observation(
            recommendation="Start with a two-week read-only stockout-risk pilot.",
            confidence=0.91,
            requires_product_owner_decision=True,
        )
        projection = record_recommendation(
            self.primary, observation=evolved, provenance=self._provenance(3)
        )
        value = projection["recommendation:read-only-pilot"]["recommendation"]["value"]
        self.assertTrue(value["requires_product_owner_decision"])
        active = self.primary.cognitive_state.entries.get(
            kind=CognitiveStateEntry.Kind.RECOMMENDATION,
            status=CognitiveStateEntry.Status.ACTIVE,
        )
        prior = self.primary.cognitive_state.entries.get(
            kind=CognitiveStateEntry.Kind.RECOMMENDATION,
            status=CognitiveStateEntry.Status.SUPERSEDED,
        )
        self.assertEqual(active.supersedes_id, prior.pk)
        self.assertFalse(
            self.primary.cognitive_state.entries.filter(
                content__attribute__startswith="accepted_decision:"
            ).exists()
        )

    def test_missing_or_foreign_state_cannot_be_recommendation_evidence(self) -> None:
        with self.assertRaisesMessage(
            ValueError, "RECOMMENDATION_EVIDENCE_UNAVAILABLE"
        ):
            record_recommendation(
                self.primary,
                observation=self._observation(
                    evidence_attributes=["not-a-state-entry"]
                ),
                provenance=self._provenance(2),
            )
        record_mission_understanding(
            self.secondary,
            observation=self._mission_observation(),
            provenance=self._provenance(4),
        )
        with self.assertRaisesMessage(
            ValueError, "RECOMMENDATION_EVIDENCE_UNAVAILABLE"
        ):
            record_recommendation(
                self.secondary,
                observation=self._observation(
                    evidence_attributes=["recommendation:read-only-pilot"]
                ),
                provenance=self._provenance(5),
            )
        self.assertEqual(recommendation_projection(self.secondary), {})

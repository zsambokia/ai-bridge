"""Behavioural capability scenarios for the ORKI-010 Operational Reasoning Engine."""

from __future__ import annotations

from django.test import TestCase

from projects.mission_understanding import record_mission_understanding
from projects.models import CognitiveStateEntry, Project
from projects.operational_reasoning import (
    operational_reasoning_projection,
    record_operational_reasoning,
)
from projects.product_owner_model import record_product_owner_profile


class OperationalReasoningTests(TestCase):
    def setUp(self) -> None:
        self.primary = self._project("operational-reasoning-primary")
        self.isolated = self._project("operational-reasoning-isolated")
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
            "source_type": "TEST_OPERATIONAL_REASONING",
            "conversation_message_id": message_id,
            "conversation_message_sha256": f"reasoning-sha-{message_id}",
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
            "reasoning_key": "inventory-pilot",
            "mission_attributes": ["stated_intent"],
            "evidence_attributes": ["stated_intent", "inferred_business_goal"],
            "assumption_attributes": ["safe_assumptions"],
            "unknowns": ["ERP history coverage has not yet been measured"],
            "alternatives": [
                {
                    "option": "Read-only pilot",
                    "summary": "Prove stockout signals before operational change.",
                    "cost": "Small integration and analysis effort.",
                    "risk": "Limited first-release coverage.",
                    "long_term_effect": "Creates measured evidence for expansion.",
                    "simplicity_score": 9,
                },
                {
                    "option": "Full ERP rollout",
                    "summary": "Integrate writes and alerts in the first release.",
                    "cost": "Large cross-team delivery investment.",
                    "risk": "Operational disruption before value is proven.",
                    "long_term_effect": "May accelerate scale if assumptions hold.",
                    "simplicity_score": 3,
                },
                {
                    "option": "Manual reporting",
                    "summary": "Produce weekly stockout reports without integration.",
                    "cost": "Ongoing analyst effort.",
                    "risk": "Slow learning and inconsistent action.",
                    "long_term_effect": (
                        "Does not create a reusable operating capability."
                    ),
                    "simplicity_score": 7,
                },
            ],
            "trade_offs": [
                {
                    "option": "Read-only pilot",
                    "benefit": "Low operational risk",
                    "cost": "No automated action",
                },
                {
                    "option": "Full ERP rollout",
                    "benefit": "Broad reach",
                    "cost": "High delivery and change risk",
                },
                {
                    "option": "Manual reporting",
                    "benefit": "No integration dependency",
                    "cost": "Recurring manual work",
                },
            ],
            "counter_arguments": [
                {
                    "option": "Read-only pilot",
                    "reason": "It can delay value if data quality is already proven.",
                },
                {
                    "option": "Full ERP rollout",
                    "reason": (
                        "It is unjustified while read access and value are unproven."
                    ),
                },
                {
                    "option": "Manual reporting",
                    "reason": (
                        "It does not meet the need for earlier operational signals."
                    ),
                },
            ],
            "recommendation": "Read-only pilot",
            "reasoning": (
                "The pilot best balances proof of value, reversible scope, and the "
                "known ERP constraint."
            ),
            "expected_impact": (
                "Earlier stockout intervention with a bounded first-release investment."
            ),
            "priority": "HIGH",
            "dependencies": ["ERP API access"],
            "next_safe_action": "Validate historical-order coverage and data quality.",
            "required_decision": {"required": False},
            "product_owner_profile_dimensions": [],
            "confidence": 0.82,
        }
        observation.update(overrides)
        return observation

    def test_reasoning_is_complete_explainable_and_recommendation_is_derived(
        self,
    ) -> None:
        projection = record_operational_reasoning(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(2),
        )
        result = projection["operational-reasoning:inventory-pilot"]
        value = result["reasoning"]["value"]
        self.assertEqual(value["recommendation"], "Read-only pilot")
        self.assertEqual(len(value["alternatives"]), 3)
        self.assertEqual(len(value["trade_offs"]), 3)
        self.assertEqual(len(value["counter_arguments"]), 3)
        self.assertEqual(value["alternatives"][0]["simplicity_score"], 9)
        self.assertEqual(
            result["recommendation"]["recommendation"]["value"]["recommendation"],
            "Read-only pilot",
        )
        self.assertEqual(len(result["evidence"]), 2)
        self.assertEqual(result["assumptions"][0]["kind"], "ASSUMPTION")
        self.assertFalse(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.ACCEPTED_DECISION
            ).exists()
        )

    def test_reasoning_evolves_and_stays_project_isolated(self) -> None:
        record_operational_reasoning(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(2),
        )
        evolved = self._observation(
            confidence=0.91,
            unknowns=[],
            reasoning=(
                "Measured evidence now strengthens the reversible pilot decision."
            ),
        )
        projection = record_operational_reasoning(
            self.primary, observation=evolved, provenance=self._provenance(3)
        )
        self.assertEqual(
            projection["operational-reasoning:inventory-pilot"]["reasoning"][
                "confidence"
            ],
            0.91,
        )
        self.assertEqual(operational_reasoning_projection(self.isolated), {})
        self.assertEqual(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.OPERATIONAL_REASONING,
                status=CognitiveStateEntry.Status.SUPERSEDED,
            ).count(),
            1,
        )

    def test_twenty_five_reasoning_revisions_remain_stable(self) -> None:
        """A long working relationship keeps one active, explainable cycle."""
        for message_id in range(2, 27):
            projection = record_operational_reasoning(
                self.primary,
                observation=self._observation(confidence=message_id / 30),
                provenance=self._provenance(message_id),
            )

        result = projection["operational-reasoning:inventory-pilot"]
        self.assertEqual(result["reasoning"]["confidence"], 26 / 30)
        self.assertEqual(len(result["reasoning"]["value"]["alternatives"]), 3)
        self.assertEqual(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.OPERATIONAL_REASONING,
                status=CognitiveStateEntry.Status.ACTIVE,
            ).count(),
            1,
        )
        self.assertEqual(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.OPERATIONAL_REASONING,
                status=CognitiveStateEntry.Status.SUPERSEDED,
            ).count(),
            24,
        )

    def test_incomplete_or_foreign_reasoning_is_rejected(self) -> None:
        alternatives = self._observation()["alternatives"]
        assert isinstance(alternatives, list)
        with self.assertRaisesMessage(
            ValueError, "OPERATIONAL_REASONING_ALTERNATIVES_INSUFFICIENT"
        ):
            record_operational_reasoning(
                self.primary,
                observation=self._observation(alternatives=alternatives[:2]),
                provenance=self._provenance(2),
            )
        with self.assertRaisesMessage(
            ValueError, "OPERATIONAL_REASONING_MISSION_UNAVAILABLE"
        ):
            record_operational_reasoning(
                self.isolated,
                observation=self._observation(),
                provenance=self._provenance(3),
            )
        self.assertEqual(operational_reasoning_projection(self.isolated), {})

    def test_product_owner_preference_is_explicit_evidence_not_hidden_personalization(
        self,
    ) -> None:
        record_product_owner_profile(
            self.primary,
            observation={
                "dimension": "sprint_size_preference",
                "preference": "Incremental MVP scope",
                "rationale": "The owner consistently chose a reversible first release.",
                "evidence_attributes": ["stated_intent", "inferred_business_goal"],
                "confidence": 0.80,
            },
            provenance=self._provenance(2),
        )
        projection = record_operational_reasoning(
            self.primary,
            observation=self._observation(
                product_owner_profile_dimensions=["sprint_size_preference"]
            ),
            provenance=self._provenance(3),
        )
        influences = projection["operational-reasoning:inventory-pilot"]["reasoning"][
            "value"
        ]["product_owner_influences"]
        self.assertEqual(influences[0]["dimension"], "sprint_size_preference")
        self.assertEqual(
            influences[0]["preference"]["preference"], "Incremental MVP scope"
        )

"""Independent HTTP-level behavioural Release Gate for ORKI-003."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.mission_understanding import record_mission_understanding
from projects.models import (
    CognitiveStateEntry,
    ExecutionProvider,
    FactoryChatMessage,
    FactoryMission,
    FactoryPlan,
    Project,
)
from projects.operational_reasoning import operational_reasoning_projection
from projects.recommendation_engine import recommendation_projection


@unittest.skip("Superseded: Factory Chat now records durable Conversations only.")
class RecommendationEngineReleaseGateTests(TestCase):
    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            "recommendation-gate-owner", password="test"
        )
        self.primary = self._project("recommendation-gate-primary")
        self.isolated = self._project("recommendation-gate-isolated")
        record_mission_understanding(
            self.primary,
            observation=self._mission_observation(),
            provenance={
                "source_type": "RECOMMENDATION_GATE_SEED",
                "conversation_message_id": 1,
                "conversation_message_sha256": "seed-sha",
            },
        )
        ExecutionProvider.objects.create(
            provider_id="recommendation-gate-provider",
            name="Recommendation Gate Provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="recommendation-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "recommendation-gate-model"},
        )
        self.client.force_login(self.owner)

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
            onboarding_status=Project.OnboardingStatus.READY,
        )

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
    def _reasoning(confidence: float = 0.82) -> dict[str, object]:
        return {
            "reasoning_key": "read-only-pilot",
            "mission_attributes": ["stated_intent"],
            "evidence_attributes": ["stated_intent", "inferred_business_goal"],
            "assumption_attributes": ["safe_assumptions"],
            "unknowns": ["ERP history coverage must be checked"],
            "priority": "HIGH",
            "recommendation": "Read-only pilot",
            "reasoning": "It proves value before operational write access.",
            "expected_impact": "Earlier action reduces missed-sales exposure.",
            "dependencies": ["ERP API access"],
            "next_safe_action": "Validate the historical-order data contract.",
            "required_decision": {"required": False},
            "product_owner_profile_dimensions": [],
            "alternatives": [
                {
                    "option": "Read-only pilot",
                    "summary": "Low-risk evidence first.",
                    "cost": "Small pilot effort.",
                    "risk": "Limited first release.",
                    "long_term_effect": "Creates measured expansion evidence.",
                    "simplicity_score": 9,
                },
                {
                    "option": "Full ERP rollout",
                    "summary": "Broader scope before evidence.",
                    "cost": "Large delivery investment.",
                    "risk": "Unproven operational change.",
                    "long_term_effect": "May scale after value is shown.",
                    "simplicity_score": 3,
                },
                {
                    "option": "Manual reporting",
                    "summary": "No integration in the first release.",
                    "cost": "Recurring analyst effort.",
                    "risk": "Slow and inconsistent learning.",
                    "long_term_effect": "Does not create an operating capability.",
                    "simplicity_score": 7,
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
                {
                    "option": "Manual reporting",
                    "benefit": "No integration",
                    "cost": "Manual effort",
                },
            ],
            "counter_arguments": [
                {"option": "Read-only pilot", "reason": "It can defer scale."},
                {"option": "Full ERP rollout", "reason": "Value is not yet proven."},
                {
                    "option": "Manual reporting",
                    "reason": "It delays operational learning.",
                },
            ],
            "confidence": confidence,
        }

    def _send(self, project: Project, response: dict[str, object]) -> None:
        self.client.get(reverse("factory-chat"), {"project": project.project_id})
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "recommendation-gate-provider",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": json.dumps(response),
                "usage": {},
            }
            result = self.client.post(
                f"{reverse('factory-chat-message')}?project={project.project_id}",
                {"message": "CONFIDENTIAL OWNER TRANSCRIPT"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(result.status_code, 200)

    def test_recommendation_engine_release_gate(self) -> None:
        self._send(
            self.primary,
            {
                "reply": "I recommend a safe pilot.",
                "plan": None,
                "understanding": {"operational_reasoning": self._reasoning()},
            },
        )
        self._send(
            self.primary,
            {
                "reply": "The evidence strengthened.",
                "plan": None,
                "understanding": {"operational_reasoning": self._reasoning(0.91)},
            },
        )
        projection = recommendation_projection(self.primary)
        result = projection["recommendation:read-only-pilot"]
        self.assertEqual(result["recommendation"]["confidence"], 0.91)
        self.assertEqual(len(result["evidence"]), 2)
        self.assertEqual(result["assumptions"][0]["kind"], "ASSUMPTION")
        self.assertEqual(len(result["alternatives"]["value"]), 3)
        self.assertEqual(len(result["trade_offs"]["value"]), 3)
        reasoning = operational_reasoning_projection(self.primary)[
            "operational-reasoning:read-only-pilot"
        ]["reasoning"]["value"]
        self.assertEqual(len(reasoning["counter_arguments"]), 3)
        self.assertEqual(recommendation_projection(self.isolated), {})
        self.assertEqual(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.RECOMMENDATION,
                status=CognitiveStateEntry.Status.SUPERSEDED,
            ).count(),
            1,
        )
        self.assertFalse(FactoryPlan.objects.filter(project=self.primary).exists())
        legacy_missions = FactoryMission.objects.filter(session__project=self.primary)
        self.assertFalse(legacy_missions.filter(plan__isnull=False).exists())
        self.assertFalse(
            legacy_missions.exclude(phase=FactoryMission.Phase.DISCOVERY).exists()
        )

    def test_factory_chat_rejects_direct_provider_recommendation_without_reasoning(
        self,
    ) -> None:
        self._send(
            self.primary,
            {
                "reply": "I would skip reasoning.",
                "plan": None,
                "understanding": {
                    "recommendation": {"recommendation_key": "unsafe-shortcut"}
                },
            },
        )
        failed = FactoryChatMessage.objects.filter(
            session__project=self.primary,
            role=FactoryChatMessage.Role.ORKI,
            status=FactoryChatMessage.Status.FAILED,
        ).latest("created_at", "pk")
        self.assertEqual(failed.error_code, "OPERATIONAL_REASONING_REQUIRED")
        self.assertEqual(recommendation_projection(self.primary), {})

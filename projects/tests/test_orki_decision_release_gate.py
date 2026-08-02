"""Independent HTTP-level behavioural Release Gate for ORKI-004."""

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.decision_engine import decision_projection
from projects.mission_understanding import record_mission_understanding
from projects.models import (
    CognitiveStateEntry,
    ExecutionProvider,
    FactoryMission,
    FactoryPlan,
    Project,
)
from projects.recommendation_engine import record_recommendation


class DecisionIntelligenceReleaseGateTests(TestCase):
    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            "decision-gate-owner", password="test"
        )
        self.primary = self._project("decision-gate-primary")
        self.isolated = self._project("decision-gate-isolated")
        record_mission_understanding(
            self.primary,
            observation=self._mission_observation(),
            provenance={
                "source_type": "DECISION_GATE_SEED",
                "conversation_message_id": 1,
                "conversation_message_sha256": "seed-sha",
            },
        )
        record_recommendation(
            self.primary,
            observation=self._recommendation(),
            provenance={
                "source_type": "DECISION_GATE_SEED",
                "conversation_message_id": 2,
                "conversation_message_sha256": "seed-sha",
            },
        )
        ExecutionProvider.objects.create(
            provider_id="decision-gate-provider",
            name="Decision Gate Provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="decision-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "decision-gate-model"},
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
    def _recommendation() -> dict[str, object]:
        return {
            "recommendation_key": "read-only-pilot",
            "priority": "HIGH",
            "recommendation": "Start with a read-only stockout-risk pilot.",
            "rationale": "It proves value before operational write access.",
            "business_impact": "Earlier action reduces missed-sales exposure.",
            "dependencies": ["ERP API access"],
            "next_safe_action": "Ask the Product Owner to select pilot scope.",
            "requires_product_owner_decision": True,
            "evidence_attributes": ["stated_intent", "inferred_business_goal"],
            "assumption_attributes": ["safe_assumptions"],
            "alternatives": [
                {"option": "Read-only pilot", "summary": "Low-risk evidence first."},
                {"option": "Full ERP rollout", "summary": "Broader scope first."},
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
            "question": "Which pilot scope should the team prepare?",
            "materiality_reason": "It changes delivery risk and ERP permissions.",
            "options": [
                {"option": "Read-only pilot", "summary": "Prove value safely."},
                {"option": "Full ERP rollout", "summary": "Broaden initial scope."},
            ],
            "recommended_option": "Read-only pilot",
            "impact_if_decided": "The team can prepare the agreed scope.",
            "impact_if_deferred": "The delivery boundary stays ambiguous.",
        }

    def _send(self, response: dict[str, object]) -> None:
        self.client.get(reverse("factory-chat"), {"project": self.primary.project_id})
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "decision-gate-provider",
                },
            ),
            patch("projects.factory_orki.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": json.dumps(response),
                "usage": {},
            }
            result = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.primary.project_id}",
                {"message": "CONFIDENTIAL OWNER TRANSCRIPT"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(result.status_code, 200)

    def test_provider_opens_an_explainable_decision_but_cannot_accept_or_execute(
        self,
    ) -> None:
        self._send(
            {
                "reply": "A biztonságos alapértelmezés a csak olvasható pilot.",
                "plan": None,
                "understanding": {"decision": self._decision()},
            }
        )
        decision = decision_projection(self.primary)["decision:pilot-scope"]
        self.assertEqual(decision["kind"], CognitiveStateEntry.Kind.OPEN_DECISION)
        self.assertEqual(decision["value"]["recommended_option"], "Read-only pilot")
        self.assertEqual(len(decision["value"]["evidence_entry_ids"]), 2)
        self.assertEqual(len(decision["value"]["trade_offs"]), 2)
        self.assertFalse(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.ACCEPTED_DECISION,
                status=CognitiveStateEntry.Status.ACTIVE,
            ).exists()
        )
        self.assertEqual(decision_projection(self.isolated), {})
        self.assertFalse(FactoryPlan.objects.filter(project=self.primary).exists())
        self.assertFalse(
            FactoryMission.objects.filter(session__project=self.primary)
            .exclude(phase=FactoryMission.Phase.DISCOVERY)
            .exists()
        )
        self.assertFalse(
            self.primary.cognitive_state.entries.filter(
                content__icontains="CONFIDENTIAL OWNER TRANSCRIPT"
            ).exists()
        )

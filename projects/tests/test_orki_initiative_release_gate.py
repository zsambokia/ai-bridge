"""HTTP-level behavioural Release Gate for ORKI-007 Initiative Engine."""

from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.initiative_engine import dismiss_initiative, initiative_projection
from projects.models import ExecutionProvider, FactoryPlan, Project


@unittest.skip("Superseded: Factory Chat now records durable Conversations only.")
class InitiativeEngineReleaseGateTests(TestCase):
    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            "initiative-gate-owner", password="test"
        )
        self.primary = self._project("initiative-gate-primary")
        self.isolated = self._project("initiative-gate-isolated")
        ExecutionProvider.objects.create(
            provider_id="initiative-gate-provider",
            name="Initiative Gate Provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="initiative-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "initiative-gate-model"},
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

    def test_conversation_creates_unsolicited_state_derived_initiative(self) -> None:
        observation = {
            "stated_intent": "Show stockout risk before purchasing commits",
            "inferred_business_goal": "Reduce lost sales",
            "inference_confidence": 0.8,
            "stated_constraints": ["The initial ERP integration is read-only"],
            "solution_proposals": ["Stockout-risk pilot"],
            "technology_preferences": [],
            "safe_assumptions": ["Historical orders are available"],
            "material_unknowns": [],
            "question": None,
        }
        self.client.get(reverse("factory-chat"), {"project": self.primary.project_id})
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "initiative-gate-provider",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": json.dumps(
                    {
                        "reply": "The mission has been understood.",
                        "plan": None,
                        "understanding": {"mission_understanding": observation},
                    }
                ),
                "usage": {},
            }
            response = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.primary.project_id}",
                {"message": "CONFIDENTIAL PRODUCT OWNER TRANSCRIPT"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )

        self.assertEqual(response.status_code, 200)
        initiatives = initiative_projection(self.primary)
        self.assertEqual(len(initiatives), 1)
        value = initiatives[0]["initiative"]["value"]
        self.assertEqual(value["category"], "MISSING_EVIDENCE")
        self.assertEqual(value["authority"], "NONE")
        self.assertTrue(value["dismissible"])
        self.assertEqual(initiative_projection(self.isolated), [])
        self.assertNotIn(
            "CONFIDENTIAL PRODUCT OWNER TRANSCRIPT", json.dumps(initiatives)
        )
        dismiss_initiative(
            self.primary,
            initiative_entry_id=initiatives[0]["initiative"]["id"],
            actor_id=self.owner.get_username(),
            reason="The assumption is accepted for discovery.",
        )
        self.assertEqual(initiative_projection(self.primary), [])
        self.assertFalse(FactoryPlan.objects.filter(project=self.primary).exists())

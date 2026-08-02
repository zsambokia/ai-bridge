"""HTTP-level behavioural Release Gate for ORKI-006 Memory Intelligence."""

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.memory_engine import memory_projection
from projects.mission_understanding import record_mission_understanding
from projects.models import ExecutionProvider, FactoryPlan, Project


class MemoryIntelligenceReleaseGateTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            "memory-owner", password="test"
        )
        self.project = Project.objects.create(
            project_id="memory-gate",
            display_name="Memory gate",
            repository_full_name="example/memory-gate",
            definition_path="memory-gate.yaml",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        record_mission_understanding(
            self.project,
            observation={
                "stated_intent": "Reduce stockout loss",
                "inferred_business_goal": "Protect revenue",
                "inference_confidence": 0.8,
                "stated_constraints": ["Read-only ERP"],
                "solution_proposals": [],
                "technology_preferences": [],
                "safe_assumptions": [],
                "material_unknowns": [],
                "question": None,
            },
            provenance={
                "source_type": "GATE",
                "conversation_message_id": 1,
                "conversation_message_sha256": "seed",
            },
        )
        ExecutionProvider.objects.create(
            provider_id="memory-gate-provider",
            name="Memory provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="memory-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "test"},
        )
        self.client.force_login(self.owner)

    def test_provider_creates_reusable_memory_without_delivery_side_effects(self):
        memory = {
            "memory_key": "stockout-rule",
            "statement": "Keep ERP integration read-only until pilot evidence exists.",
            "tags": ["erp", "safety"],
            "evidence_attributes": ["stated_intent"],
            "confidence": 0.82,
        }
        self.client.get(reverse("factory-chat"), {"project": self.project.project_id})
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "memory-gate-provider",
                },
            ),
            patch("projects.factory_orki.model_adapter_for") as adapter,
        ):
            adapter.return_value.invoke_model.return_value = {
                "output_text": json.dumps(
                    {
                        "reply": "A tudás rögzítve.",
                        "plan": None,
                        "understanding": {"memory": memory},
                    }
                ),
                "usage": {},
            }
            response = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.project.project_id}",
                {"message": "CONFIDENTIAL MEMORY TRANSCRIPT"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            memory_projection(self.project)[0]["content"]["tags"], ["erp", "safety"]
        )
        self.assertFalse(FactoryPlan.objects.filter(project=self.project).exists())
        self.assertFalse(
            self.project.cognitive_state.entries.filter(
                content__icontains="CONFIDENTIAL MEMORY TRANSCRIPT"
            ).exists()
        )

"""HTTP-level behavioural Release Gate for ORKI-005 Planning Intelligence."""

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.mission_understanding import record_mission_understanding
from projects.models import ExecutionProvider, FactoryPlan, Project
from projects.planning_engine import planning_projection
from projects.recommendation_engine import record_recommendation


class PlanningIntelligenceReleaseGateTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            "planning-owner", password="test"
        )
        self.project = Project.objects.create(
            project_id="planning-gate",
            display_name="Planning gate",
            repository_full_name="example/planning-gate",
            definition_path="planning-gate.yaml",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        record_mission_understanding(
            self.project,
            observation={
                "stated_intent": "Make stockout risk visible earlier",
                "inferred_business_goal": "Reduce stockout losses",
                "inference_confidence": 0.8,
                "stated_constraints": ["Read-only ERP"],
                "solution_proposals": ["Forecasting"],
                "technology_preferences": ["ERP API"],
                "safe_assumptions": ["Orders exist"],
                "material_unknowns": [],
                "question": None,
            },
            provenance={
                "source_type": "GATE",
                "conversation_message_id": 1,
                "conversation_message_sha256": "seed",
            },
        )
        record_recommendation(
            self.project,
            observation={
                "recommendation_key": "pilot",
                "priority": "HIGH",
                "recommendation": "Start read-only.",
                "rationale": "Evidence before writes.",
                "business_impact": "Reduce losses.",
                "dependencies": ["ERP"],
                "next_safe_action": "Create plan.",
                "requires_product_owner_decision": False,
                "evidence_attributes": ["stated_intent", "inferred_business_goal"],
                "assumption_attributes": ["safe_assumptions"],
                "alternatives": [
                    {"option": "Pilot", "summary": "Safe."},
                    {"option": "Rollout", "summary": "Broad."},
                ],
                "trade_offs": [
                    {"option": "Pilot", "benefit": "Low risk", "cost": "Limited"},
                    {"option": "Rollout", "benefit": "Reach", "cost": "Risk"},
                ],
                "confidence": 0.8,
            },
            provenance={
                "source_type": "GATE",
                "conversation_message_id": 2,
                "conversation_message_sha256": "seed",
            },
        )
        ExecutionProvider.objects.create(
            provider_id="planning-gate-provider",
            name="Planning provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="planning-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "test"},
        )
        self.client.force_login(self.owner)

    def test_provider_creates_explainable_cognitive_plan_without_delivery_side_effect(
        self,
    ):
        plan = {
            "plan_key": "pilot",
            "objective": "Deliver a read-only pilot",
            "business_value": "Reduce stockout losses",
            "architecture": "ERP ingest, scoring, dashboard",
            "alternatives": [
                {"option": "Pilot", "summary": "Safe."},
                {"option": "Rollout", "summary": "Broad."},
            ],
            "chosen_strategy": "Pilot",
            "rejected_strategy": "Rollout",
            "risks": ["Data quality"],
            "dependencies": ["ERP access"],
            "acceptance": ["Users can see scored stockout risk"],
            "release_strategy": "One unit, read-only",
            "operational_strategy": "Daily freshness monitoring",
            "recovery_strategy": "Show last verified data",
            "future_evolution": "Consider governed write-back after evidence",
            "evidence_attributes": ["stated_intent", "recommendation:pilot"],
            "confidence": 0.83,
        }
        self.client.get(reverse("factory-chat"), {"project": self.project.project_id})
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "planning-gate-provider",
                },
            ),
            patch("projects.factory_orki.model_adapter_for") as adapter,
        ):
            adapter.return_value.invoke_model.return_value = {
                "output_text": json.dumps(
                    {
                        "reply": "Van egy biztonságos terv.",
                        "plan": None,
                        "understanding": {"planning": plan},
                    }
                ),
                "usage": {},
            }
            response = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.project.project_id}",
                {"message": "CONFIDENTIAL PLAN TRANSCRIPT"},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(response.status_code, 200)
        stored = planning_projection(self.project)["plan:pilot"]
        self.assertEqual(
            stored["plan"]["value"]["recovery_strategy"], "Show last verified data"
        )
        self.assertEqual(len(stored["evidence"]), 2)
        self.assertFalse(FactoryPlan.objects.filter(project=self.project).exists())
        self.assertFalse(
            self.project.cognitive_state.entries.filter(
                content__icontains="CONFIDENTIAL PLAN TRANSCRIPT"
            ).exists()
        )

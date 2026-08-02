"""Independent HTTP-level behavioural Release Gate for ORKI-002."""

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.mission_understanding import mission_projection
from projects.models import (
    CognitiveStateEntry,
    ExecutionProvider,
    FactoryMission,
    FactoryPlan,
    Project,
)


class MissionUnderstandingReleaseGateTests(TestCase):
    """Prove Mission Understanding through the same Factory Chat boundary as the UI."""

    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            "mission-gate-owner", password="test"
        )
        self.primary = self._project("mission-gate-primary")
        self.equivalent = self._project("mission-gate-equivalent")
        self.isolated = self._project("mission-gate-isolated")
        ExecutionProvider.objects.create(
            provider_id="mission-gate-provider",
            name="Mission Gate Provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="mission-gate-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "mission-gate-model"},
        )
        self.client.force_login(self.owner)

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
            repository_root=f"C:/workspace/{project_id}",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    @staticmethod
    def _observation(
        *, confidence: float = 0.76, question: dict[str, str] | None = None
    ) -> dict[str, object]:
        return {
            "stated_intent": "Enable purchasing to see stockout risk early",
            "inferred_business_goal": "Reduce revenue loss caused by stockouts",
            "inference_confidence": confidence,
            "stated_constraints": ["Read-only ERP access for the first release"],
            "solution_proposals": ["A stockout forecasting application"],
            "technology_preferences": ["ERP API"],
            "safe_assumptions": ["Historical order data is available"],
            "material_unknowns": ["Pilot business unit"] if question else [],
            "question": question,
        }

    @staticmethod
    def _response(observation: dict[str, object]) -> dict[str, object]:
        return {
            "output_text": json.dumps(
                {
                    "reply": "I have recorded the mission state.",
                    "plan": None,
                    "understanding": {"mission_understanding": observation},
                }
            ),
            "usage": {},
        }

    def _send(self, project: Project, message: str) -> None:
        self.client.get(reverse("factory-chat"), {"project": project.project_id})
        response = self.client.post(
            f"{reverse('factory-chat-message')}?project={project.project_id}",
            {"message": message},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 200)

    def test_mission_understanding_release_gate(self) -> None:
        """Prove rephrasing, inference, separation, question discipline, evolution."""
        confidential_transcript = "CONFIDENTIAL-OWNER-WORDS-MUST-NOT-BECOME-MEMORY"
        question = {
            "text": "Which business unit should be the pilot?",
            "purpose": "Set the initial ownership and data boundary.",
            "material_effect": "Changes the pilot scope and selected ERP data.",
        }
        responses = [
            self._response(self._observation()),
            self._response(self._observation()),
            self._response(self._observation(confidence=0.91, question=question)),
        ]
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only-value",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "mission-gate-provider",
                },
            ),
            patch("projects.factory_orki.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.side_effect = responses
            self._send(self.primary, confidential_transcript)
            self._send(
                self.equivalent,
                "Prevent missed sales by predicting inventory shortages.",
            )
            self._send(
                self.primary,
                "Start with the business unit where the pilot matters most.",
            )

        primary = mission_projection(self.primary)
        equivalent = mission_projection(self.equivalent)
        for attribute in (
            "stated_intent",
            "inferred_business_goal",
            "stated_constraints",
            "solution_proposals",
            "technology_preferences",
        ):
            self.assertEqual(
                primary[attribute]["value"], equivalent[attribute]["value"]
            )
        self.assertEqual(
            primary["inferred_business_goal"]["kind"],
            CognitiveStateEntry.Kind.INFERENCE,
        )
        self.assertEqual(
            primary["solution_proposals"]["kind"], CognitiveStateEntry.Kind.FACT
        )
        self.assertEqual(
            primary["technology_preferences"]["kind"], CognitiveStateEntry.Kind.FACT
        )
        self.assertEqual(
            primary["safe_assumptions"]["kind"], CognitiveStateEntry.Kind.ASSUMPTION
        )
        self.assertEqual(primary["mission_question"]["value"], question)
        self.assertEqual(primary["inferred_business_goal"]["confidence"], 0.91)
        self.assertNotIn(
            confidential_transcript, json.dumps(primary, ensure_ascii=False)
        )
        self.assertEqual(mission_projection(self.isolated), {})
        self.assertFalse(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.RECOMMENDATION,
            ).exists()
        )
        scoped_missions = FactoryMission.objects.filter(
            session__project__in=[self.primary, self.equivalent, self.isolated]
        )
        self.assertFalse(scoped_missions.filter(plan__isnull=False).exists())
        self.assertFalse(
            scoped_missions.exclude(phase=FactoryMission.Phase.DISCOVERY).exists()
        )
        self.assertFalse(
            FactoryPlan.objects.filter(
                project__in=[self.primary, self.equivalent, self.isolated]
            ).exists()
        )
        self.assertEqual(
            self.primary.cognitive_state.entries.filter(
                kind=CognitiveStateEntry.Kind.INFERENCE,
                content__attribute="inferred_business_goal",
                status=CognitiveStateEntry.Status.SUPERSEDED,
            ).count(),
            1,
        )

"""Independent capability scenarios for ORKI-002 Mission Understanding."""

from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.mission_understanding import (
    mission_projection,
    record_mission_understanding,
)
from projects.models import CognitiveStateEntry, ExecutionProvider, Project


class MissionUnderstandingTests(TestCase):
    def setUp(self) -> None:
        self.primary = self._project("mission-primary")
        self.secondary = self._project("mission-secondary")

    @staticmethod
    def _project(project_id: str) -> Project:
        return Project.objects.create(
            project_id=project_id,
            display_name=project_id,
            repository_full_name=f"example/{project_id}",
            definition_path=f"projects/{project_id}.yaml",
        )

    @staticmethod
    def _provenance(
        message_id: int, message: str = "raw transcript"
    ) -> dict[str, object]:
        return {
            "source_type": "TEST_MISSION_OBSERVATION",
            "conversation_message_id": message_id,
            "conversation_message_sha256": f"sha256-{message_id}",
            "raw_message_not_state": message,
        }

    @staticmethod
    def _observation(**overrides: object) -> dict[str, object]:
        observation: dict[str, object] = {
            "stated_intent": "A beszerzési csapat korán lássa a várható készlethiányt",
            "inferred_business_goal": (
                "A készlethiányból eredő bevételkiesés csökkentése"
            ),
            "inference_confidence": 0.78,
            "stated_constraints": ["Első körben csak olvasható ERP kapcsolat"],
            "solution_proposals": ["Készlethiány-előrejelző alkalmazás"],
            "technology_preferences": ["ERP API"],
            "safe_assumptions": ["A történeti rendelési adatok hozzáférhetők"],
            "material_unknowns": [],
            "question": None,
        }
        observation.update(overrides)
        return observation

    def test_equivalent_formulations_produce_the_same_mission_state(self) -> None:
        first = self._observation(
            stated_constraints=["első körben csak olvasható erp kapcsolat"],
            technology_preferences=["erp api"],
        )
        second = self._observation(
            stated_intent="  A beszerzési csapat korán lássa a várható készlethiányt  ",
            stated_constraints=["Első körben csak olvasható ERP kapcsolat"],
            technology_preferences=["ERP API"],
        )
        first_projection = record_mission_understanding(
            self.primary, observation=first, provenance=self._provenance(1)
        )
        second_projection = record_mission_understanding(
            self.secondary, observation=second, provenance=self._provenance(2)
        )
        for key in (
            "stated_intent",
            "inferred_business_goal",
            "stated_constraints",
            "technology_preferences",
            "proposed_mission",
        ):
            self.assertEqual(
                first_projection[key]["value"], second_projection[key]["value"]
            )

    def test_goal_is_inference_not_fact_and_preferences_remain_separate(self) -> None:
        result = record_mission_understanding(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(1),
        )
        self.assertEqual(result["stated_intent"]["kind"], CognitiveStateEntry.Kind.FACT)
        self.assertEqual(
            result["inferred_business_goal"]["kind"], CognitiveStateEntry.Kind.INFERENCE
        )
        self.assertEqual(
            result["solution_proposals"]["kind"], CognitiveStateEntry.Kind.FACT
        )
        self.assertEqual(
            result["technology_preferences"]["kind"], CognitiveStateEntry.Kind.FACT
        )
        self.assertEqual(
            result["safe_assumptions"]["kind"], CognitiveStateEntry.Kind.ASSUMPTION
        )
        self.assertEqual(result["mission_question"]["value"], None)
        self.assertEqual(result["proposed_mission"]["value"]["state"], "PROPOSED")

    def test_only_a_material_question_is_permitted_and_evolution_is_explainable(
        self,
    ) -> None:
        record_mission_understanding(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(1),
        )
        evolved = self._observation(
            inferred_business_goal=(
                "A készlethiányból eredő bevételkiesés és sürgős beszerzés csökkentése"
            ),
            inference_confidence=0.91,
            material_unknowns=["Melyik üzleti egység legyen a pilot?"],
            question={
                "text": "Melyik üzleti egység legyen a pilot?",
                "purpose": "A kezdeti adat- és felelősségi határ meghatározása",
                "material_effect": "A pilot hatóköre és az ERP-adatok kiválasztása",
            },
        )
        result = record_mission_understanding(
            self.primary, observation=evolved, provenance=self._provenance(2)
        )
        self.assertEqual(result["inferred_business_goal"]["confidence"], 0.91)
        self.assertEqual(
            result["mission_question"]["value"]["purpose"],
            evolved["question"]["purpose"],
        )
        prior = self.primary.cognitive_state.entries.get(
            kind=CognitiveStateEntry.Kind.INFERENCE,
            content__attribute="inferred_business_goal",
            status=CognitiveStateEntry.Status.SUPERSEDED,
        )
        active = self.primary.cognitive_state.entries.get(
            kind=CognitiveStateEntry.Kind.INFERENCE,
            content__attribute="inferred_business_goal",
            status=CognitiveStateEntry.Status.ACTIVE,
        )
        self.assertEqual(active.supersedes_id, prior.pk)
        with self.assertRaisesMessage(ValueError, "QUESTION_NOT_MATERIAL"):
            record_mission_understanding(
                self.secondary,
                observation=self._observation(
                    question={
                        "text": "Felesleges?",
                        "purpose": "Nincs",
                        "material_effect": "Nincs",
                    }
                ),
                provenance=self._provenance(3),
            )

    def test_transcript_is_not_state_and_projects_remain_isolated(self) -> None:
        raw = "BIZALMAS-NYERS-PO-TRANSCRIPT-NEM-LEHET-MEMORIA"
        record_mission_understanding(
            self.primary,
            observation=self._observation(),
            provenance=self._provenance(1, raw),
        )
        primary = mission_projection(self.primary)
        self.assertNotIn(raw, json.dumps(primary, ensure_ascii=False))
        self.assertEqual(mission_projection(self.secondary), {})


class MissionUnderstandingPublicBoundaryTests(TestCase):
    """The canonical path is exercised through the Factory Chat HTTP boundary."""

    def setUp(self) -> None:
        self.owner = get_user_model().objects.create_user(
            "mission-owner", password="test"
        )
        self.project = Project.objects.create(
            project_id="mission-http",
            display_name="mission-http",
            repository_full_name="example/mission-http",
            definition_path="projects/mission-http.yaml",
            repository_root="C:/workspace/mission-http",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        ExecutionProvider.objects.create(
            provider_id="mission-http-provider",
            name="Mission HTTP Provider",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="mission-http-provider",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "mission-http-model"},
        )
        self.client.force_login(self.owner)

    def test_structured_observation_updates_state_without_copying_owner_text(
        self,
    ) -> None:
        owner_text = "BIZALMAS-CHAT-SZOVEG: szeretném elkerülni a készlethiányt"
        observation = MissionUnderstandingTests._observation()
        response = {
            "output_text": json.dumps(
                {
                    "reply": "Értem a célt.",
                    "plan": None,
                    "understanding": {
                        "mission_understanding": observation,
                    },
                }
            ),
            "usage": {},
        }
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only-value",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "mission-http-provider",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = response
            self.client.get(
                reverse("factory-chat"), {"project": self.project.project_id}
            )
            result = self.client.post(
                f"{reverse('factory-chat-message')}?project={self.project.project_id}",
                {"message": owner_text},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(result.status_code, 200)
        state = mission_projection(self.project)
        self.assertEqual(state["inferred_business_goal"]["kind"], "INFERENCE")
        self.assertNotIn(owner_text, json.dumps(state, ensure_ascii=False))

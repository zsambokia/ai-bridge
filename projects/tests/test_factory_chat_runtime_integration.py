"""Acceptance proof that Factory Chat uses the Runtime as its only provider path."""

from __future__ import annotations

import json
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import StreamingHttpResponse
from django.test import TestCase
from django.urls import reverse

from projects.models import FactoryMission, OrkiExecution, Project


class FactoryChatRuntimeIntegrationTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="runtime-chat-owner", password="test-password"
        )
        self.project = Project.objects.create(
            project_id="factory-runtime-chat",
            display_name="Factory Runtime Chat",
            repository_full_name="example/factory-runtime-chat",
            definition_path="projects/factory-runtime-chat.yaml",
            repository_root="C:/workspace/factory-runtime-chat",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        self.client.force_login(self.user)

    def _start(self, message: str, request_id: str) -> dict[str, Any]:
        accepted = self.client.post(
            f"{reverse('factory-chat-message')}?project={self.project.project_id}",
            {"message": message, "request_id": request_id},
            HTTP_X_REQUESTED_WITH="FactoryChat",
            HTTP_X_ORKI_RUNTIME_ASYNC="1",
        )
        self.assertEqual(accepted.status_code, 202)
        return accepted.json()

    @patch("projects.factory_orki._provider")
    @patch("projects.orki_runtime.model_adapter_for")
    @patch("projects.orki_runtime.model_text_response")
    def test_e2e_underspecified_mission_waits_for_runtime_generated_questions(
        self, model_text_response: Mock, model_adapter_for: Mock, provider: Mock
    ) -> None:
        """A provider reply cannot move an underspecified mission into Planning."""
        entry = SimpleNamespace(provider_id="test-openai")
        provider.return_value = (entry, "test-model")
        model_adapter_for.return_value.invoke_model.return_value = {
            "usage": {"input_tokens": 3}
        }
        model_text_response.return_value = json.dumps(
            {"reply": "The plan is ready.", "understanding": {}}
        )

        ingress = self._start("Container utilization calculator.", "e2e-runtime-1")
        token = ingress["execution"]["token"]
        execution = OrkiExecution.objects.get(token=token)
        self.assertEqual(execution.state, OrkiExecution.State.SEMANTIC_SEARCH)
        self.assertEqual(execution.mode, OrkiExecution.Mode.LIVE)
        self.assertTrue(
            execution.events.filter(event_type="FACTORY_CHAT_INGRESS_ACCEPTED").exists()
        )

        dispatched = self.client.post(ingress["dispatch_url"])
        self.assertEqual(dispatched.status_code, 200)
        result = dispatched.json()
        self.assertEqual(result["state"], OrkiExecution.State.WAITING_USER)
        self.assertEqual(result["goal"]["status"], "OPEN")
        self.assertEqual(
            [message["role"] for message in result["messages"]], ["owner", "orki"]
        )
        self.assertIn("Planning még nem indítható", result["messages"][-1]["text"])
        self.assertTrue(
            any(event["type"] == "gap_analysis.completed" for event in result["events"])
        )
        self.assertTrue(
            any(event["type"] == "questions.generated" for event in result["events"])
        )
        provider.assert_called_once()
        model_adapter_for.return_value.invoke_model.assert_called_once()

        stream = self.client.get(
            reverse("runtime-execution-event-stream", args=[token])
        )
        self.assertEqual(stream.status_code, 200)
        payload = b"".join(
            cast(Iterator[bytes], cast(StreamingHttpResponse, stream).streaming_content)
        ).decode()
        self.assertIn("event: runtime", payload)
        self.assertIn("questions.generated", payload)
        self.assertIn('"messages"', payload)
        self.assertIn("event: snapshot", payload)

    @patch("projects.factory_orki._provider")
    @patch("projects.orki_runtime.model_adapter_for")
    @patch("projects.orki_runtime.model_text_response")
    def test_e2e_multiple_question_rounds_remain_waiting_for_user(
        self, model_text_response: Mock, model_adapter_for: Mock, provider: Mock
    ) -> None:
        entry = SimpleNamespace(provider_id="test-openai")
        provider.return_value = (entry, "test-model")
        model_adapter_for.return_value.invoke_model.return_value = {
            "usage": {"input_tokens": 3}
        }
        model_text_response.side_effect = [
            json.dumps(
                {
                    "reply": "",
                    "understanding": {
                        "objective": "Container calculator",
                        "recommendation_confidence": 1,
                    },
                }
            ),
            json.dumps(
                {
                    "reply": "",
                    "understanding": {
                        "target_users": ["logistics staff"],
                        "primary_workflow": "Calculate from box data",
                        "recommendation_confidence": 1,
                    },
                }
            ),
        ]

        first = self._start("Calculate container utilization.", "e2e-question-round-1")
        first_result = self.client.post(first["dispatch_url"]).json()
        self.assertEqual(first_result["state"], OrkiExecution.State.WAITING_USER)
        first_mission = FactoryMission.objects.get(session__project=self.project)
        first_confidence = first_mission.recommendation_confidence
        self.assertGreater(
            len(first_mission.delivery_status["understanding"]["critical_unknowns"]), 0
        )

        second = self._start(
            "A logistics operator enters box data.", "e2e-question-round-2"
        )
        second_result = self.client.post(second["dispatch_url"]).json()
        self.assertEqual(second_result["state"], OrkiExecution.State.WAITING_USER)
        mission = FactoryMission.objects.get(session__project=self.project)
        self.assertFalse(mission.requirements_sufficient)
        self.assertIsNone(mission.plan)
        self.assertLess(first_confidence, mission.recommendation_confidence)

    @patch("projects.factory_orki._provider")
    @patch("projects.orki_runtime.model_adapter_for")
    @patch("projects.orki_runtime.model_text_response")
    def test_e2e_planning_starts_only_after_critical_unknowns_are_resolved(
        self, model_text_response: Mock, model_adapter_for: Mock, provider: Mock
    ) -> None:
        entry = SimpleNamespace(provider_id="test-openai")
        provider.return_value = (entry, "test-model")
        model_adapter_for.return_value.invoke_model.return_value = {
            "usage": {"input_tokens": 3}
        }
        model_text_response.side_effect = [
            json.dumps(
                {
                    "reply": "",
                    "understanding": {
                        "objective": "Container calculator",
                        "recommendation_confidence": 1,
                    },
                }
            ),
            json.dumps(
                {
                    "reply": "",
                    "understanding": {
                        "target_users": ["logistics staff"],
                        "primary_workflow": "Calculate from box sizes and quantity",
                        "required_inputs": ["box size", "order quantity"],
                        "required_outputs": ["utilization", "containers needed"],
                        "mvp_boundary": "One responsive calculation screen",
                        "persistence_requirements": "No persistent storage",
                        "recommendation_confidence": 1,
                    },
                }
            ),
        ]

        first = self._start("Calculate container utilization.", "e2e-planning-gate-1")
        self.assertEqual(
            self.client.post(first["dispatch_url"]).json()["state"],
            OrkiExecution.State.WAITING_USER,
        )
        second = self._start(
            "Here are the missing product details.", "e2e-planning-gate-2"
        )
        result = self.client.post(second["dispatch_url"]).json()
        self.assertEqual(result["state"], OrkiExecution.State.WAITING_APPROVAL)
        mission = FactoryMission.objects.get(session__project=self.project)
        self.assertTrue(mission.requirements_sufficient)
        self.assertIsNotNone(mission.plan)
        self.assertTrue(
            any(event["type"] == "planning.ready" for event in result["events"])
        )

    def test_provider_configuration_failure_is_a_concrete_runtime_wait(self) -> None:
        accepted = self.client.post(
            f"{reverse('factory-chat-message')}?project={self.project.project_id}",
            {"message": "Start it.", "request_id": "e2e-runtime-unavailable"},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        token = accepted.json()["execution"]["token"]

        with patch(
            "projects.factory_orki._provider",
            side_effect=__import__(
                "projects.factory_orki", fromlist=["ModelProviderSelectionUnavailable"]
            ).ModelProviderSelectionUnavailable(),
        ):
            response = self.client.post(
                reverse("runtime-execution-dispatch", args=[token])
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["state"], OrkiExecution.State.WAITING_EXTERNAL)
        self.assertEqual(payload["wait_reason"]["code"], "MODEL_PROVIDER_UNAVAILABLE")
        self.assertIn("provider", payload["wait_reason"]["message"].lower())

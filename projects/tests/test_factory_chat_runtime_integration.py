"""Acceptance proof that Factory Chat uses the Runtime as its only provider path."""

# ruff: noqa: E501

from __future__ import annotations

import json
from collections.abc import Iterator
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.http import StreamingHttpResponse
from django.test import TestCase
from django.urls import reverse

from projects.models import FactoryChatMessage, OrkiExecution, Project


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

    @patch("projects.factory_orki._provider")
    @patch("projects.orki_runtime.model_adapter_for")
    @patch("projects.orki_runtime.model_text_response")
    def test_chat_message_completes_through_runtime_and_provider_adapter(
        self, model_text_response: Mock, model_adapter_for: Mock, provider: Mock
    ) -> None:
        """External provider is mocked; Runtime, its events and state machine are real."""
        entry = SimpleNamespace(provider_id="test-openai")
        provider.return_value = (entry, "test-model")
        adapter = model_adapter_for.return_value
        adapter.invoke_model.return_value = {"usage": {"input_tokens": 3}}
        model_text_response.return_value = json.dumps(
            {"reply": "A Runtime válasza.", "understanding": {}}
        )

        accepted = self.client.post(
            f"{reverse('factory-chat-message')}?project={self.project.project_id}",
            {"message": "Készíts végrehajtási tervet.", "request_id": "e2e-runtime-1"},
            HTTP_X_REQUESTED_WITH="FactoryChat",
            HTTP_X_ORKI_RUNTIME_ASYNC="1",
        )

        self.assertEqual(accepted.status_code, 202)
        ingress = accepted.json()
        token = ingress["execution"]["token"]
        execution = OrkiExecution.objects.get(token=token)
        self.assertEqual(execution.state, OrkiExecution.State.PLANNING)
        self.assertEqual(execution.mode, OrkiExecution.Mode.LIVE)
        self.assertTrue(execution.events.filter(event_type="FACTORY_CHAT_INGRESS_ACCEPTED").exists())
        self.assertEqual(FactoryChatMessage.objects.filter(session=execution.plan.goal.source_session).count(), 1)

        dispatched = self.client.post(ingress["dispatch_url"])

        self.assertEqual(dispatched.status_code, 200)
        result = dispatched.json()
        self.assertEqual(result["state"], OrkiExecution.State.COMPLETED)
        self.assertEqual(result["goal"]["status"], "ACHIEVED")
        self.assertEqual(result["plan"]["status"], "COMPLETED")
        self.assertEqual(result["active_persona"], "DEFAULT_RUNTIME_PERSPECTIVE")
        self.assertGreater(result["evidence_count"], 0)
        self.assertEqual(
            [message["role"] for message in result["messages"]],
            ["owner", "orki"],
        )
        self.assertTrue(any(event["type"] == "reflection.completed" for event in result["events"]))
        self.assertTrue(any(event["type"] == "GOAL_ACHIEVED" for event in result["events"]))
        self.assertEqual(
            list(
                FactoryChatMessage.objects.filter(
                    session=execution.plan.goal.source_session
                ).values_list("role", flat=True)
            ),
            [FactoryChatMessage.Role.OWNER, FactoryChatMessage.Role.ORKI],
        )
        provider.assert_called_once()
        adapter.invoke_model.assert_called_once()

        stream = self.client.get(
            reverse("runtime-execution-event-stream", args=[token])
        )
        self.assertEqual(stream.status_code, 200)
        payload = b"".join(
            cast(Iterator[bytes], cast(StreamingHttpResponse, stream).streaming_content)
        ).decode()
        self.assertIn("event: runtime", payload)
        self.assertIn("reflection.completed", payload)
        self.assertIn("event: snapshot", payload)

    def test_provider_configuration_failure_is_a_concrete_runtime_wait(self) -> None:
        accepted = self.client.post(
            f"{reverse('factory-chat-message')}?project={self.project.project_id}",
            {"message": "Indítsd el.", "request_id": "e2e-runtime-unavailable"},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        token = accepted.json()["execution"]["token"]

        with patch(
            "projects.factory_orki._provider",
            side_effect=__import__("projects.factory_orki", fromlist=["ModelProviderSelectionUnavailable"]).ModelProviderSelectionUnavailable(),
        ):
            response = self.client.post(
                reverse("runtime-execution-dispatch", args=[token])
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["state"], OrkiExecution.State.WAITING_EXTERNAL)
        self.assertEqual(payload["wait_reason"]["code"], "MODEL_PROVIDER_UNAVAILABLE")
        self.assertIn("provider", payload["wait_reason"]["message"].lower())

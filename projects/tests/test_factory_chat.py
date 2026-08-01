from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project


class FactoryChatTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="factory-owner", password="test-password"
        )
        self.project = Project.objects.create(
            project_id="factory-chat-test",
            display_name="Factory Chat Test",
            repository_full_name="example/factory-chat-test",
            definition_path="projects/factory-chat-test.yaml",
            repository_root="C:/workspace/factory-chat-test",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    def test_chat_requires_authenticated_user(self) -> None:
        response = self.client.get(reverse("factory-chat"))
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_chat_renders_server_owned_context(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat"))
        self.assertContains(response, "Factory Chat Test")
        self.assertContains(response, "Aktív munkakörnyezet")
        self.assertContains(response, "Mód: planning")
        self.assertContains(response, reverse("factory-chat-status"))

    def test_mode_panel_and_project_selection_are_restored(self) -> None:
        another = Project.objects.create(
            project_id="second-project",
            display_name="Second Project",
            repository_full_name="example/second-project",
            definition_path="projects/second-project.yaml",
        )
        self.client.force_login(self.user)
        self.client.get(
            reverse("factory-chat"),
            {"project": another.project_id, "mode": "coding", "panel": "chat"},
        )
        response = self.client.get(reverse("factory-chat"))
        self.assertContains(response, "Second Project")
        self.assertContains(response, 'data-panel="chat"')
        self.assertContains(response, "?mode=coding")

    def test_message_is_retained_in_session_without_provider_call(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-message"), {"message": "Készíts tervet."}
        )
        self.assertRedirects(response, reverse("factory-chat"))
        response = self.client.get(reverse("factory-chat"))
        self.assertContains(response, "Készíts tervet.")
        self.assertContains(response, "nem indít közvetlen szolgáltatói műveletet")

    def test_context_refresh_is_authenticated_and_server_rendered(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat-status"))
        self.assertContains(response, "Factory Chat Test")

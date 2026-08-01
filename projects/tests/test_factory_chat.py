from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import FactoryPlan, GovernanceApproval, Project


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

    def test_planning_questionnaire_creates_proposed_artifacts(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-plan-create"),
            {
                "project_id": self.project.project_id,
                "outcome": "Create a governed plan artifact.",
                "title": "Governed plan",
                "kind": "WORK_ITEM",
                "task_type": "FEATURE",
                "technical_constraints": "Keep provider calls on the backend.",
                "acceptance_checks": "Targeted tests pass\nNo provider call",
            },
        )
        self.assertRedirects(
            response, f"/?project={self.project.project_id}&mode=planning"
        )
        plan = FactoryPlan.objects.get(project=self.project)
        self.assertEqual(plan.status, FactoryPlan.Status.PENDING_APPROVAL)
        self.assertEqual(plan.scope.status, "PROPOSED")
        self.assertEqual(plan.scope.record["execution_authorization"], "NONE")
        assert plan.roadmap_candidate is not None
        assert plan.memory_candidate is not None
        self.assertEqual(plan.roadmap_candidate.status, "CANDIDATE")
        self.assertEqual(plan.memory_candidate.status, "CANDIDATE")

    def test_plan_approval_is_once_only_and_does_not_authorize_execution(self) -> None:
        self.client.force_login(self.user)
        self.client.post(
            reverse("factory-plan-create"),
            {
                "project_id": self.project.project_id,
                "outcome": "Plan safely.",
                "task_type": "FEATURE",
            },
        )
        plan = FactoryPlan.objects.get(project=self.project)
        response = self.client.post(reverse("factory-plan-approve", args=[plan.pk]))
        self.assertRedirects(
            response, f"/?project={self.project.project_id}&mode=planning"
        )
        plan.refresh_from_db()
        self.assertEqual(plan.status, FactoryPlan.Status.APPROVED)
        self.assertEqual(plan.scope.status, "PROPOSED")
        self.assertEqual(plan.scope.record["execution_authorization"], "NONE")
        assert plan.approval is not None
        self.assertEqual(plan.approval.approved_action, "PLAN_ARTIFACT_APPROVAL")
        self.assertEqual(GovernanceApproval.objects.filter(scope=plan.scope).count(), 1)
        response = self.client.post(reverse("factory-plan-approve", args=[plan.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(GovernanceApproval.objects.filter(scope=plan.scope).count(), 1)

    def test_enhanced_planning_post_refreshes_context_without_redirect(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-plan-create"),
            {
                "project_id": self.project.project_id,
                "outcome": "Create asynchronously.",
            },
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["X-Factory-Context"], reverse("factory-chat-status"))
        self.assertTrue(FactoryPlan.objects.filter(project=self.project).exists())

    def test_business_escalation_blocks_plan_approval(self) -> None:
        self.client.force_login(self.user)
        self.client.post(
            reverse("factory-plan-create"),
            {
                "project_id": self.project.project_id,
                "outcome": "Choose a market commitment.",
                "business_escalation": "Which market should receive the paid feature?",
            },
        )
        plan = FactoryPlan.objects.get(project=self.project)
        self.assertEqual(plan.status, FactoryPlan.Status.BUSINESS_DECISION_REQUIRED)
        response = self.client.post(reverse("factory-plan-approve", args=[plan.pk]))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(GovernanceApproval.objects.filter(scope=plan.scope).exists())

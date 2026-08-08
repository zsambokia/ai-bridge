from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import OrkiExecution, OrkiGoal, OrkiPlan, Project
from projects.orki_runtime import recover_execution


class OrkiRuntimeTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="runtime-owner", password="test-password"
        )
        self.project = Project.objects.create(
            project_id="orki-runtime-test",
            display_name="Orki Runtime Test",
            repository_full_name="example/orki-runtime-test",
            definition_path="projects/orki-runtime-test.yaml",
            repository_root="C:/workspace/orki-runtime-test",
            onboarding_status=Project.OnboardingStatus.READY,
        )

    def _create_shadow_plan(self) -> OrkiExecution:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-plan-create"),
            {
                "project_id": self.project.project_id,
                "outcome": "Validate Runtime Shadow Mode.",
                "task_type": "FEATURE",
            },
        )
        self.assertEqual(response.status_code, 302)
        return OrkiExecution.objects.get(plan__goal__project=self.project)

    def test_factory_plan_starts_auditable_shadow_execution(self) -> None:
        execution = self._create_shadow_plan()

        self.assertEqual(execution.mode, OrkiExecution.Mode.SHADOW)
        self.assertEqual(execution.state, OrkiExecution.State.WAITING_APPROVAL)
        self.assertIsNone(execution.execution_run_id)
        self.assertIsNone(execution.plan.goal.cognitive_goal_id)
        self.assertIsNone(execution.plan.cognitive_plan_id)
        self.assertEqual(
            list(execution.events.values_list("event_type", flat=True)),
            [
                "EXECUTION_CREATED",
                "PLAN_SELECTED",
                "STATE_TRANSITION",
                "STATE_TRANSITION",
            ],
        )

    def test_approval_is_observed_without_starting_execution_run(self) -> None:
        execution = self._create_shadow_plan()
        plan_id = execution.plan.factory_plan_id
        assert plan_id is not None

        response = self.client.post(reverse("factory-plan-approve", args=[plan_id]))
        self.assertEqual(response.status_code, 302)
        execution.refresh_from_db()

        self.assertEqual(execution.state, OrkiExecution.State.WAITING_GOVERNANCE)
        self.assertIsNone(execution.execution_run_id)
        self.assertEqual(execution.governance_reference["handoff"], "shadow_only")
        self.assertTrue(
            execution.events.filter(
                event_type="SHADOW_GOVERNANCE_HANDOFF_RECORDED"
            ).exists()
        )

    def test_runtime_api_pauses_and_resumes_without_provider_operations(self) -> None:
        execution = self._create_shadow_plan()
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("runtime-execution-pause", args=[execution.token]),
            {"reason": "owner review"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], OrkiExecution.State.PAUSED)
        response = self.client.post(
            reverse("runtime-execution-resume", args=[execution.token])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["state"], OrkiExecution.State.WAITING_APPROVAL)
        self.assertIsNone(execution.execution_run_id)

    def test_recovery_reassesses_external_wait_only(self) -> None:
        goal = OrkiGoal.objects.create(project=self.project)
        plan = OrkiPlan.objects.create(goal=goal, version=1)
        execution = OrkiExecution.objects.create(
            plan=plan,
            mode=OrkiExecution.Mode.SHADOW,
            state=OrkiExecution.State.WAITING_EXTERNAL,
        )

        recover_execution(str(execution.token), actor=self.user.get_username())
        execution.refresh_from_db()

        self.assertEqual(execution.state, OrkiExecution.State.PLANNING)
        self.assertTrue(
            execution.events.filter(event_type="RECOVERY_REASSESSMENT_STARTED").exists()
        )

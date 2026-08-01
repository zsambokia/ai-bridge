from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projects.factory_coding import coding_projection
from projects.knowledge import create_or_upsert_candidate, review_candidate
from projects.models import (
    FactoryPlan,
    GovernanceApproval,
    KnowledgeContextPackage,
    KnowledgeEntry,
    Project,
)


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
        self.assertContains(response, "Aktuális feladat")
        self.assertContains(response, "Beszélgetés a fejlesztésről")
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
        self.assertContains(response, 'id="chat-messages"')
        self.assertContains(response, "?mode=coding")

    def test_message_is_retained_in_session_without_provider_call(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-message"), {"message": "Készíts tervet."}
        )
        self.assertRedirects(response, reverse("factory-chat"))
        response = self.client.get(reverse("factory-chat"))
        self.assertContains(response, "Készíts tervet.")
        self.assertContains(response, "Minek nevezzük ezt a projektet?")

    def test_context_refresh_is_authenticated_and_server_rendered(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat-status"))
        self.assertContains(response, "Factory Chat Test")

    def test_coding_mode_without_run_explains_that_no_execution_exists(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat"), {"mode": "coding"})
        self.assertContains(response, "Még nincs elindított fejlesztés")

    def test_coding_projection_requires_product_owner_for_business_blocker(
        self,
    ) -> None:
        class Run:
            lifecycle = "BLOCKED_BUSINESS_DECISION"
            current_blocker = {"question": "Melyik ügyfélcsoportot válasszuk?"}
            contract = type(
                "Contract",
                (),
                {"payload": {}, "approved_sprint_path": "docs/sprints/example.md"},
            )()

        with (
            patch(
                "projects.factory_coding.lifecycle_status_projection",
                return_value={
                    "status": "BLOCKED_BUSINESS_DECISION",
                    "phase": "AWAITING_DECISION",
                    "heartbeat": {},
                    "queue": {"status": "QUEUED"},
                    "workspace": {"status": "RETAINED"},
                    "evidence": {
                        "evidence_root": "docs/evidence/example",
                        "final_commit_sha": "",
                        "terminal_state": "",
                    },
                },
            ),
            patch(
                "projects.factory_coding.activity_summary",
                return_value={"checklist": [], "latest_events": []},
            ),
        ):
            projection = coding_projection(Run())  # type: ignore[arg-type]
        action = projection["action"]
        assert isinstance(action, dict)
        self.assertTrue(action["required"])
        self.assertEqual(action["title"], "Termék Tulajdonos döntése szükséges")

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

    def _memory_candidate(
        self, project: Project, key: str = "memory-entry"
    ) -> KnowledgeEntry:
        return create_or_upsert_candidate(
            project,
            {
                "entry_key": key,
                "knowledge_type": "GENERAL",
                "title": f"Memory source {key}",
                "content": "A governed Memory source for Factory Chat.",
                "source_reference": "docs/memory-source.md",
                "evidence_references": ["docs/evidence/memory.md"],
                "is_must_know": True,
            },
            self.user.username,
        )

    def test_memory_search_builds_project_bound_context_package(self) -> None:
        self._memory_candidate(self.project)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-memory-search"),
            {"project_id": self.project.project_id, "query": "governed"},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 204)
        response = self.client.get(reverse("factory-chat"), {"mode": "memory"})
        self.assertContains(response, "Memory source memory-entry")
        package = KnowledgeContextPackage.objects.get(project=self.project)
        self.assertEqual(package.retrieval_query, "governed")
        self.assertEqual(package.work_context_id, "factory-chat:memory")

    def test_memory_review_activation_requires_project_approval(self) -> None:
        entry = self._memory_candidate(self.project)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-memory-review", args=[entry.pk]),
            {
                "project_id": self.project.project_id,
                "decision": "REQUEST_REVIEW",
            },
        )
        self.assertRedirects(
            response, f"/?project={self.project.project_id}&mode=memory"
        )
        entry.refresh_from_db()
        self.assertEqual(entry.status, KnowledgeEntry.Status.IN_REVIEW)
        response = self.client.post(
            reverse("factory-memory-review", args=[entry.pk]),
            {
                "project_id": self.project.project_id,
                "decision": "APPROVE",
            },
        )
        self.assertRedirects(
            response, f"/?project={self.project.project_id}&mode=memory"
        )
        entry.refresh_from_db()
        self.assertEqual(entry.status, KnowledgeEntry.Status.ACTIVE)
        self.assertTrue(entry.approval_reference.startswith("factory-memory:"))

    def test_memory_rejection_and_cross_project_isolation_are_enforced(self) -> None:
        another = Project.objects.create(
            project_id="memory-other-project",
            display_name="Memory Other",
            repository_full_name="example/memory-other",
            definition_path="projects/memory-other.yaml",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        own_entry = self._memory_candidate(self.project, "memory-own-entry")
        foreign_entry = self._memory_candidate(another, "memory-foreign-entry")
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-memory-review", args=[foreign_entry.pk]),
            {"project_id": self.project.project_id, "decision": "REJECT"},
        )
        self.assertEqual(response.status_code, 400)
        foreign_entry.refresh_from_db()
        self.assertEqual(foreign_entry.status, KnowledgeEntry.Status.CANDIDATE)
        response = self.client.post(
            reverse("factory-memory-review", args=[own_entry.pk]),
            {"project_id": self.project.project_id, "decision": "REJECT"},
        )
        self.assertRedirects(
            response, f"/?project={self.project.project_id}&mode=memory"
        )
        own_entry.refresh_from_db()
        self.assertEqual(own_entry.status, KnowledgeEntry.Status.REJECTED)

    def test_memory_projection_displays_stale_and_conflict_diagnostics(self) -> None:
        first = self._memory_candidate(self.project, "memory-conflict-one")
        second = self._memory_candidate(self.project, "memory-conflict-two")
        for entry, reference in (
            (first, "memory-conflict-approval-one"),
            (second, "memory-conflict-approval-two"),
        ):
            review_candidate(
                self.project, entry.pk, "REQUEST_REVIEW", self.user.username
            )
            GovernanceApproval.objects.create(
                reference=reference,
                project=self.project,
                approved_action="akb.review_candidate",
                approved_by=self.user.username,
            )
            review_candidate(
                self.project, entry.pk, "APPROVE", self.user.username, reference
            )
        first.conflict_key = second.conflict_key = "shared-memory-fact"
        first.review_due_at = timezone.now()
        first.save(update_fields=["conflict_key", "review_due_at"])
        second.save(update_fields=["conflict_key"])
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat"), {"mode": "memory"})
        self.assertContains(response, "Memória")
        self.assertContains(response, "Technikai részletek")

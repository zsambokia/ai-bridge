from typing import Any
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projects.factory_coding import coding_projection
from projects.factory_orki import availability
from projects.knowledge import create_or_upsert_candidate, review_candidate
from projects.models import (
    CognitiveState,
    CognitiveStateEntry,
    ExecutionProvider,
    FactoryChatMessage,
    FactoryChatSession,
    FactoryMission,
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
        self.assertContains(response, 'aria-label="A beszélgetés munkatérképe"')
        self.assertContains(response, "Mit &#233;rtett meg Orki?")
        self.assertContains(response, reverse("factory-chat-status"))

    def test_new_project_creates_a_durable_project_bound_orki_session(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-new-project"),
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 200)
        project_id = response.json()["project"]["id"]
        project = Project.objects.get(project_id=project_id)
        self.assertEqual(project.onboarding_status, Project.OnboardingStatus.PENDING)
        session = FactoryChatSession.objects.get(project=project)
        first_message = session.messages.first()
        self.assertIsNotNone(first_message)
        assert first_message is not None
        self.assertEqual(first_message.role, FactoryChatMessage.Role.ORKI)
        self.assertEqual(first_message.status, FactoryChatMessage.Status.COMPLETED)
        self.assertIn("Kezdjük el.", first_message.body)

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
        self.assertContains(response, "digitális COO")

    def test_project_switch_restores_its_durable_chat_history(self) -> None:
        another = Project.objects.create(
            project_id="history-project",
            display_name="History Project",
            repository_full_name="example/history-project",
            definition_path="projects/history-project.yaml",
        )
        self.client.force_login(self.user)
        self.client.get(reverse("factory-chat"), {"project": self.project.project_id})
        self.client.post(
            reverse("factory-chat-message"),
            {"message": "Keep this project history."},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )

        self.client.get(reverse("factory-chat"), {"project": another.project_id})
        response = self.client.get(
            reverse("factory-chat"), {"project": self.project.project_id}
        )

        self.assertContains(response, "Keep this project history.")

    def test_chat_reports_exact_unconfigured_provider_message_and_persists_it(
        self,
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-message"), {"message": "K\u00e9sz\u00edts tervet."}
        )
        self.assertRedirects(response, reverse("factory-chat"))
        message = FactoryChatMessage.objects.filter(
            role=FactoryChatMessage.Role.ORKI
        ).latest("pk")
        self.assertIn("Runtime", message.body)
        self.assertIn("modellprovider", message.body)
        self.assertEqual(message.status, FactoryChatMessage.Status.FAILED)
        self.assertEqual(message.error_code, "MODEL_PROVIDER_UNAVAILABLE")

    def test_enhanced_invalid_message_never_reflects_technical_request_content(
        self,
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-message"),
            {"message": "", "request_id": "RuntimeError: internal diagnostic"},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "MESSAGE_INVALID")
        self.assertNotIn("RuntimeError", payload["error"]["message"])
        self.assertNotIn("diagnostic", payload["error"]["message"])

    def test_same_request_identifier_reuses_the_durable_chat_result(self) -> None:
        self.client.force_login(self.user)
        request_id = "fd077351-bb20-4b75-a6ec-a353719af496"
        first = self.client.post(
            reverse("factory-chat-message"),
            {"message": "Készíts tervet.", "request_id": request_id},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        second = self.client.post(
            reverse("factory-chat-message"),
            {"message": "Készíts tervet.", "request_id": request_id},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()["messages"], second.json()["messages"])
        self.assertEqual(
            FactoryChatMessage.objects.filter(correlation_id=request_id).count(), 2
        )

    def test_unexpected_chat_exception_returns_only_a_safe_recovery_message(
        self,
    ) -> None:
        self.client.force_login(self.user)
        with patch(
            "projects.factory_chat.dispatch_factory_chat_execution",
            side_effect=RuntimeError("secret server stack trace"),
        ):
            response = self.client.post(
                reverse("factory-chat-message"),
                {"message": "Készíts tervet."},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
        self.assertEqual(response.status_code, 409)
        payload = response.json()
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["error"]["retryable"])
        self.assertNotIn("secret", payload["error"]["message"])
        self.assertNotIn("stack", payload["error"]["message"])

    def test_chat_accepts_a_product_owner_brief_up_to_twelve_thousand_characters(
        self,
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-message"),
            {"message": "a" * 12_000},
            HTTP_X_REQUESTED_WITH="FactoryChat",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["messages"][0]["text"], "a" * 12_000)

    def test_chat_rejects_a_product_owner_brief_over_twelve_thousand_characters(
        self,
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("factory-chat-message"), {"message": "a" * 12_001}
        )
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "12 000 karakter", status_code=400)

    def test_configured_provider_without_credential_is_not_reported_as_unconfigured(
        self,
    ) -> None:
        ExecutionProvider.objects.create(
            provider_id="credential-missing-openai",
            name="Credential missing OpenAI",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="credential-missing-openai",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
        )
        self.client.force_login(self.user)
        with patch.dict(
            "os.environ",
            {"AI_BRIDGE_FACTORY_ORKI_PROVIDER": "credential-missing-openai"},
            clear=True,
        ):
            response = self.client.post(
                reverse("factory-chat-message"),
                {"message": "K\u00e9sz\u00edts tervet."},
            )
            self.assertRedirects(response, reverse("factory-chat"))
            message = FactoryChatMessage.objects.filter(
                role=FactoryChatMessage.Role.ORKI
            ).latest("pk")
            self.assertEqual(message.status, FactoryChatMessage.Status.FAILED)
            self.assertEqual(message.error_code, "PROVIDER_CREDENTIAL_UNAVAILABLE")
            self.assertNotEqual(message.error_code, "MODEL_PROVIDER_UNAVAILABLE")
            self.assertEqual(availability()["state"], "runtime")

    def test_mocked_model_round_trip_is_persisted_with_safe_audit_metadata(
        self,
    ) -> None:
        ExecutionProvider.objects.create(
            provider_id="factory-chat-openai",
            name="Test OpenAI",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="factory-chat-openai",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
            configuration={"model": "test-model"},
        )
        self.client.force_login(self.user)
        payload = '{"reply":"Mi az elfogad\u00e1si felt\u00e9tel?","plan":null}'
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only-value",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "factory-chat-openai",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": payload,
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
            response = self.client.post(
                reverse("factory-chat-message"),
                {"message": "Legyen \u00faj riportoldal."},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )
            prompt = adapter_for.return_value.invoke_model.call_args.args[1]
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Planning még nem indítható", response.json()["messages"][-1]["text"]
        )
        message = FactoryChatMessage.objects.filter(
            role=FactoryChatMessage.Role.ORKI
        ).latest("pk")
        self.assertEqual(message.status, FactoryChatMessage.Status.COMPLETED)
        self.assertEqual(message.provider_id, "factory-chat-openai")
        self.assertEqual(message.model, "test-model")
        self.assertEqual(message.token_usage, {"input_tokens": 10, "output_tokens": 5})
        self.assertEqual(len(message.prompt_hash), 64)
        self.assertEqual(len(message.response_hash), 64)
        self.assertNotIn("test-only-value", message.body)
        self.assertIn("Factory Chat Test", prompt)
        self.assertIn("Legyen új riportoldal.", prompt)

    def test_default_model_identifier_is_persisted_for_openai(self) -> None:
        ExecutionProvider.objects.create(
            provider_id="factory-chat-default-openai",
            name="Default-model OpenAI",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="factory-chat-default-openai",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
        )
        self.client.force_login(self.user)
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only-value",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "factory-chat-default-openai",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": '{"reply":"Rendben.","plan":null}',
            }
            self.client.post(
                reverse("factory-chat-message"), {"message": "Legyen terv."}
            )
        message = FactoryChatMessage.objects.filter(
            role=FactoryChatMessage.Role.ORKI
        ).latest("pk")
        self.assertEqual(message.model, "gpt-4.1-mini")

    def test_provider_json_wrapped_in_a_code_fence_is_accepted(self) -> None:
        ExecutionProvider.objects.create(
            provider_id="fenced-json-openai",
            name="Fenced JSON OpenAI",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="fenced-json-openai",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
        )
        self.client.force_login(self.user)
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test-only-value",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "fenced-json-openai",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": '```json\n{"reply":"Rendben.","plan":null}\n```',
            }
            response = self.client.post(
                reverse("factory-chat-message"), {"message": "Kezdj\u00fck."}
            )
        self.assertEqual(response.status_code, 302)
        message = FactoryChatMessage.objects.filter(
            role=FactoryChatMessage.Role.ORKI
        ).latest("pk")
        self.assertEqual(message.status, FactoryChatMessage.Status.COMPLETED)
        self.assertIn("Planning még nem indítható", message.body)

    def test_sufficient_understanding_creates_a_canonical_plan_artifact(self) -> None:
        ExecutionProvider.objects.create(
            provider_id="mission-openai",
            name="Mission OpenAI",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="mission-openai",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
        )
        payload: dict[str, Any] = {
            "reply": "Már elegendő információm van a tervhez.",
            "plan": None,
            "understanding": {
                "objective": "Konténerkalkulátor",
                "target_users": ["logisztikai ügyintézők"],
                "primary_workflow": "Dobozméretből konténerszámot számol",
                "required_inputs": ["dobozméret", "MOQ"],
                "required_outputs": ["konténerszám"],
                "mvp_boundary": "Egy számítási folyamat",
                "persistence_requirements": "SQLite",
                "recommendations": ["Django és egyszerű webes űrlap"],
                "risks": ["pontatlan bemeneti adatok"],
                "assumptions": ["egységes mértékegység"],
                "unresolved_decisions": [],
                "recommendation_confidence": 0.9,
                "repository_proposal": {
                    "mode": "create",
                    "owner": "owner",
                    "name": "container-calc",
                    "visibility": "private",
                },
            },
        }
        self.client.force_login(self.user)
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "mission-openai",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": __import__("json").dumps(payload)
            }
            response = self.client.post(
                reverse("factory-chat-message"),
                {
                    "message": (
                        "Készíts egy konténerkalkulátort logisztikai "
                        "ügyintézőknek, dobozméret és MOQ alapján."
                    )
                },
            )
        self.assertRedirects(response, reverse("factory-chat"))
        mission = FactoryMission.objects.get(session__project=self.project)
        self.assertTrue(mission.requirements_sufficient)
        self.assertEqual(
            mission.phase, FactoryMission.Phase.AWAITING_PRODUCT_OWNER_APPROVAL
        )
        self.assertIsNotNone(mission.plan)
        assert mission.plan is not None
        self.assertEqual(mission.plan.plan_document["objective"], "Konténerkalkulátor")

    def test_explicit_plan_request_cannot_bypass_unresolved_critical_information(
        self,
    ) -> None:
        """An affirmative phrase never substitutes for missing mission facts."""
        ExecutionProvider.objects.create(
            provider_id="plan-request-openai",
            name="Plan request OpenAI",
            kind=ExecutionProvider.Kind.OPENAI,
            role=ExecutionProvider.Role.MODEL_API,
            status=ExecutionProvider.Status.ACTIVE,
            adapter_key="plan-request-openai",
            enabled=True,
            capabilities=["MODEL_INFERENCE"],
            credential_binding="OPENAI_API_KEY",
        )
        session = FactoryChatSession.objects.create(
            project=self.project, actor_identity=self.user.get_username()
        )
        FactoryMission.objects.create(
            session=session,
            objective="Konténerkihasználtság-kalkulátor",
            primary_workflow="A beszerző megadja a méreteket, majd számítást kér.",
            unresolved_decisions=["Kell export?"],
        )
        payload: dict[str, Any] = {
            "reply": "Rendben, nekilátok.",
            "plan": None,
            "understanding": {"unresolved_decisions": []},
        }
        self.client.force_login(self.user)
        client_session = self.client.session
        client_session["factory_orki_session"] = str(session.token)
        client_session.save()
        with (
            patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "test",
                    "AI_BRIDGE_FACTORY_ORKI_PROVIDER": "plan-request-openai",
                },
            ),
            patch("projects.orki_runtime.model_adapter_for") as adapter_for,
        ):
            adapter_for.return_value.invoke_model.return_value = {
                "output_text": __import__("json").dumps(payload)
            }
            response = self.client.post(
                reverse("factory-chat-message"), {"message": "ok, mehet"}
            )
        self.assertRedirects(response, reverse("factory-chat"))
        mission = FactoryMission.objects.get(session=session)
        self.assertFalse(mission.requirements_sufficient)
        self.assertEqual(mission.unresolved_decisions, [])
        self.assertEqual(mission.phase, FactoryMission.Phase.QUESTION_REQUIRED)
        self.assertIsNone(mission.plan)
        self.assertContains(
            self.client.get(reverse("factory-chat")),
            "Planning még nem indítható",
        )

    def test_plan_approval_stops_at_execution_preparation(self) -> None:
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
        session = FactoryChatSession.objects.create(
            project=self.project, actor_identity=self.user.get_username()
        )
        mission = FactoryMission.objects.create(
            session=session,
            plan=plan,
            requirements_sufficient=True,
            repository_proposal={"mode": "create"},
        )
        response = self.client.post(reverse("factory-plan-approve", args=[plan.pk]))
        self.assertEqual(response.status_code, 302)
        mission.refresh_from_db()
        self.assertEqual(mission.phase, FactoryMission.Phase.PLAN_APPROVED)
        self.assertEqual(mission.delivery_status["state"], "execution_preparation")

    def test_natural_language_approval_uses_the_canonical_approval_path(self) -> None:
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
        session = FactoryChatSession.objects.create(
            project=self.project, actor_identity=self.user.get_username()
        )
        mission = FactoryMission.objects.create(
            session=session,
            plan=plan,
            requirements_sufficient=True,
            repository_proposal={"mode": "create"},
        )
        response = self.client.post(
            reverse("factory-chat-message"), {"message": "Jóváhagyom"}
        )
        self.assertRedirects(response, reverse("factory-chat"))
        plan.refresh_from_db()
        mission.refresh_from_db()
        self.assertEqual(plan.status, FactoryPlan.Status.APPROVED)
        self.assertEqual(mission.phase, FactoryMission.Phase.PLAN_APPROVED)
        self.assertTrue(
            FactoryChatMessage.objects.filter(
                session__project=self.project,
                role=FactoryChatMessage.Role.ORKI,
                body__contains="átvette a szállítást",
            ).exists()
        )

    def test_workspace_uses_multiline_composer_and_human_mission_labels(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat"))
        self.assertContains(response, '<textarea id="message"')
        self.assertContains(response, "e.isComposing")
        self.assertContains(response, "shiftKey")
        self.assertContains(response, 'id="orki-thinking"')
        self.assertContains(response, "Hol tart a tervez&#233;s?")
        self.assertNotContains(response, "AWAITING_PRODUCT_OWNER_APPROVAL")

    def test_workspace_shell_projects_canonical_views_and_repository_actions(
        self,
    ) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat"))
        self.assertContains(response, 'data-workspace-view="home"')
        self.assertContains(response, 'data-workspace-view="orki"')
        self.assertContains(response, 'data-workspace-screen="knowledge"')
        self.assertContains(response, 'data-workspace-screen="runtime"')
        self.assertContains(response, reverse("workspace-repository-action"))
        self.assertContains(response, "Repository Lifecycle")
        self.assertContains(response, "EventSource")

    def test_repository_workspace_action_requires_governed_approval_reference(
        self,
    ) -> None:
        self.client.force_login(self.user)
        self.client.get(reverse("factory-chat"))
        response = self.client.post(
            reverse("workspace-repository-action"), {"action": "bootstrap"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"], "APPROVAL_REFERENCE_REQUIRED"
        )

    def test_pending_plan_renders_the_review_and_decision_in_the_chat(self) -> None:
        self.client.force_login(self.user)
        self.client.post(
            reverse("factory-plan-create"),
            {
                "project_id": self.project.project_id,
                "outcome": "Render an approval card.",
                "task_type": "FEATURE",
            },
        )

        response = self.client.get(reverse("factory-chat"))
        plan = FactoryPlan.objects.get(project=self.project)

        html = response.content.decode()
        chat_start = html.index('id="chat-messages"')
        chat_end = html.index('id="orki-thinking"')
        sidebar_start = html.index('id="context-status"')
        sidebar_end = html.index('</aside>', sidebar_start)

        self.assertIn("data-plan-review", html[chat_start:chat_end])
        self.assertNotIn(
            "Product Owner döntés szükséges", html[sidebar_start:sidebar_end]
        )
        self.assertIn("data-plan-review-fragment", html[sidebar_start:sidebar_end])
        self.assertContains(response, "data-quick-action")
        self.assertContains(response, f"/factory/plans/{plan.pk}/approve/")
        self.assertContains(response, f"/factory/plans/{plan.pk}/changes/")
        self.assertContains(response, f"/factory/plans/{plan.pk}/reject/")

    def test_context_refresh_is_authenticated_and_server_rendered(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat-status"))
        self.assertContains(response, "Factory Chat Test")

    def test_coding_mode_without_run_explains_that_no_execution_exists(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("factory-chat"), {"mode": "coding"})
        self.assertContains(response, 'aria-label="A beszélgetés munkatérképe"')

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

    def test_planning_request_creates_proposed_artifacts(self) -> None:
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
        self.assertEqual(plan.roadmap_candidate.status, "CANDIDATE")
        self.assertIsNone(plan.memory_candidate)

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
        self.assertContains(response, 'aria-label="A beszélgetés munkatérképe"')
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
        self.assertContains(response, 'aria-label="A beszélgetés munkatérképe"')
        self.assertContains(response, "Mit javasol?")

    def test_status_is_a_project_isolated_cognitive_state_projection(self) -> None:
        another = Project.objects.create(
            project_id="workspace-other-project",
            display_name="Workspace Other",
            repository_full_name="example/workspace-other",
            definition_path="projects/workspace-other.yaml",
        )
        state = CognitiveState.objects.create(project=self.project)
        CognitiveStateEntry.objects.create(
            state=state,
            kind=CognitiveStateEntry.Kind.FACT,
            content={"value": "Inventory data is the verified source."},
            provenance={"source": "test"},
            confidence=0.91,
        )
        foreign_state = CognitiveState.objects.create(project=another)
        CognitiveStateEntry.objects.create(
            state=foreign_state,
            kind=CognitiveStateEntry.Kind.FACT,
            content={"value": "FOREIGN WORKSPACE FACT"},
            provenance={"source": "test"},
            confidence=0.91,
        )
        session = FactoryChatSession.objects.create(project=self.project)
        FactoryChatMessage.objects.create(
            session=session,
            role=FactoryChatMessage.Role.OWNER,
            body="TRANSCRIPT ONLY - NOT A STATE FACT",
        )
        self.client.force_login(self.user)
        self.client.get(reverse("factory-chat"), {"project": self.project.project_id})
        response = self.client.get(reverse("factory-chat-status"))

        self.assertContains(response, "data-cognitive-state")
        self.assertContains(response, "canonical-cognitive-state")
        self.assertContains(response, "Inventory data is the verified source.")
        self.assertNotContains(response, "FOREIGN WORKSPACE FACT")
        self.assertNotContains(response, "TRANSCRIPT ONLY - NOT A STATE FACT")

    def test_enhanced_chat_converts_operational_errors_to_retryable_message(
        self,
    ) -> None:
        self.client.force_login(self.user)
        request_id = "e3196b9d-c29a-4a98-99b2-640dedbdcb8a"
        with patch(
            "projects.factory_chat.dispatch_factory_chat_execution",
            side_effect=OSError("database down"),
        ):
            response = self.client.post(
                reverse("factory-chat-message"),
                {"message": "Please prepare a plan.", "request_id": request_id},
                HTTP_X_REQUESTED_WITH="FactoryChat",
            )

        self.assertEqual(response.status_code, 409)
        payload = response.json()
        self.assertFalse(payload["ok"])
        self.assertFalse(payload["error"]["retryable"])
        self.assertEqual(payload["correlation_id"], request_id)
        self.assertNotIn("database down", payload["error"]["message"])

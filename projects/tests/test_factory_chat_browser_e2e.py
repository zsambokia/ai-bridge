"""Browser acceptance for the bounded Issue #17 Factory Chat mission."""

from __future__ import annotations

import os
from typing import ClassVar

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from projects.knowledge import (
    create_or_upsert_candidate,
    record_context_use,
    review_candidate,
)
from projects.models import (
    ExecutionContract,
    ExecutionRun,
    ExecutionStartRequest,
    GovernanceApproval,
    KnowledgeContextPackage,
    OrchestrationSession,
    Project,
)


class FactoryChatBrowserE2ETests(StaticLiveServerTestCase):
    """Exercise the delivered UI in a real desktop and mobile Chromium page."""

    _previous_async_unsafe: ClassVar[str | None]
    _playwright: ClassVar[Playwright]
    _browser: ClassVar[Browser]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # The synchronous Playwright driver owns an asyncio loop while the
        # live-server test performs ordinary synchronous ORM setup.
        cls._previous_async_unsafe = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls._playwright = sync_playwright().start()
        cls._browser = cls._playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._browser.close()
        cls._playwright.stop()
        if cls._previous_async_unsafe is None:
            del os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"]
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = cls._previous_async_unsafe
        super().tearDownClass()

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="factory-browser-owner", password="test-password"
        )
        self.project = Project.objects.create(
            project_id="factory-chat-browser",
            display_name="Factory Chat Browser Mission",
            repository_full_name="example/factory-chat-browser",
            definition_path="projects/factory-chat-browser.yaml",
            repository_root="C:/workspace/factory-chat-browser",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        self.entry = create_or_upsert_candidate(
            self.project,
            {
                "entry_key": "browser-mission-memory",
                "knowledge_type": "GENERAL",
                "title": "Browser mission memory",
                "content": (
                    "Factory Chat browser mission keeps provider calls server-owned."
                ),
                "source_reference": "docs/evidence/issue-017-browser-mission.md",
                "evidence_references": ["docs/evidence/issue-017-browser-mission.md"],
            },
            self.user.username,
        )
        review_candidate(
            self.project, self.entry.pk, "REQUEST_REVIEW", self.user.username
        )
        approval = GovernanceApproval.objects.create(
            reference="browser-memory-approval",
            project=self.project,
            approved_action="akb.review_candidate",
            approved_by=self.user.username,
        )
        review_candidate(
            self.project,
            self.entry.pk,
            "APPROVE",
            self.user.username,
            approval.reference,
        )

    def _login(self, page: Page) -> None:
        page.goto(f"{self.live_server_url}/")
        page.get_by_label("Username").fill(self.user.username)
        page.get_by_label("Password").fill("test-password")
        page.get_by_role("button", name="Belépés").click()
        page.wait_for_url(f"{self.live_server_url}/")

    def test_bounded_multi_sprint_mission_across_desktop_and_mobile(self) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        desktop.get_by_role("link", name="Tervezés").click()
        desktop.get_by_label("Cél").fill("Deliver the bounded Factory Chat mission.")
        desktop.get_by_label("Cím").fill("Browser mission plan")
        desktop.get_by_role("button", name="Terv készítése").click()
        desktop.wait_for_timeout(100)
        self.assertTrue(self.project.factory_plans.exists())
        desktop_display = desktop.locator("main").evaluate(
            "node => getComputedStyle(node).display"
        )
        self.assertEqual(desktop_display, "grid")

        desktop.get_by_role("link", name="Memória").click()
        desktop.locator("#memory-query").fill("provider")
        desktop.get_by_role("button", name="Search").click()
        desktop.wait_for_timeout(100)
        desktop.get_by_text("Browser mission memory", exact=True).wait_for()
        package = KnowledgeContextPackage.objects.filter(project=self.project).first()
        self.assertIsNotNone(package)
        assert package is not None

        session = OrchestrationSession.objects.create(
            project=self.project,
            idempotency_key="factory-chat-browser-mission",
            provider_id="orki",
            status=OrchestrationSession.Status.COMPLETED,
            request_summary="Factory Chat browser mission",
            correlation_id="factory-chat-browser-mission",
            context_package_hash=package.package_hash,
            context_entry_ids=package.entry_ids,
        )
        record_context_use(package.pk, session=session)
        contract = ExecutionContract.objects.create(
            project=self.project,
            handoff_identifier="factory-chat-browser-contract",
            approved_sprint_path="docs/sprints/issue-017-sprint-6-factory-chat-end-to-end-acceptance.md",
            contract_hash="a" * 64,
            payload={
                "scope": {
                    "identifier": "issue-017-browser",
                    "epic_reference": "issue-017",
                }
            },
            lifecycle=ExecutionContract.Lifecycle.CONSUMED,
            orchestration_session=session,
        )
        authorization = GovernanceApproval.objects.create(
            reference="browser-execution-approval",
            project=self.project,
            approved_action="AUTHORIZE_EXECUTION",
            approved_by=self.user.username,
        )
        request = ExecutionStartRequest.objects.create(
            contract=contract, approval=authorization
        )
        ExecutionRun.objects.create(
            contract=contract,
            start_request=request,
            repository=self.project.repository_full_name,
            branch="main",
            baseline_commit="b" * 40,
            contract_hash=contract.contract_hash,
            workspace_identifier="factory-chat-browser-workspace",
            provider_name="codex-cli",
            lifecycle=ExecutionRun.Lifecycle.COMPLETED,
            current_phase="CLOSING",
            evidence_root="docs/evidence/issue-017-sprint-6-factory-chat-end-to-end-acceptance",
            final_commit_sha="c" * 40,
            terminal_state="PASS — READY FOR PRODUCT OWNER REVIEW",
            orchestration_session=session,
        )
        desktop.get_by_role("link", name="Kódolás").click()
        desktop.get_by_text("Coding status:", exact=False).wait_for()
        self.assertTrue(ExecutionRun.objects.filter(orchestration_session=session).exists())
        self.assertEqual(package.uses.get().session_id, session.pk)

        mobile = self._browser.new_page(viewport={"width": 390, "height": 844})
        self._login(mobile)
        mobile.get_by_role("link", name="Chat").click()
        mobile.get_by_role("heading", name="Kontextusos beszélgetés").wait_for()
        self.assertEqual(
            mobile.locator("main").evaluate("node => getComputedStyle(node).display"),
            "block",
        )
        self.assertTrue(mobile.locator(".mobile-tabs").is_visible())
        desktop.close()
        mobile.close()

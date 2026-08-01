"""Real Chromium acceptance for the conversational Factory Chat journey."""

from __future__ import annotations

import os
from typing import ClassVar

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from projects.knowledge import create_or_upsert_candidate
from projects.models import Project


class FactoryChatBrowserE2ETests(StaticLiveServerTestCase):
    """Exercise the delivered product-owner experience in Chromium."""

    _previous_async_unsafe: ClassVar[str | None]
    _playwright: ClassVar[Playwright]
    _browser: ClassVar[Browser]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
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

    def _login(self, page: Page) -> None:
        page.goto(f"{self.live_server_url}/")
        page.get_by_label("Username").fill(self.user.username)
        page.get_by_label("Password").fill("test-password")
        page.get_by_role("button", name="Belépés").click()
        page.wait_for_url(f"{self.live_server_url}/")

    def _send(self, page: Page, message: str) -> None:
        messages = page.locator("#chat-messages .message")
        before = messages.count()
        page.get_by_label("Üzenet").fill(message)
        page.get_by_role("button", name="Küldés").click()
        messages.nth(before + 1).wait_for()

    def _complete_discovery(self, page: Page, name: str = "Demo17") -> None:
        messages = page.locator("#chat-messages .message")
        before = messages.count()
        page.get_by_role("button", name="Új projekt").click()
        messages.nth(before).wait_for()
        self.assertIn("Minek nevezzük", messages.nth(before).inner_text())
        for answer in (
            name,
            "Belső kollégák",
            "Új bejegyzés felvétele és megőrzése",
            "Kihagyom",
        ):
            self._send(page, answer)
        page.get_by_text("Jóváhagyás szükséges.", exact=True).wait_for()

    def test_new_project_stays_in_factory_chat_and_is_approved(self) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        self._complete_discovery(desktop, "Új Factory Chat projekt")
        self.assertNotIn("admin", desktop.url)
        self.assertNotIn("registry", desktop.url)
        desktop.get_by_role("button", name="Jóváhagyom a tervet").click()
        desktop.get_by_text("A tervet jóváhagytad.", exact=False).wait_for()
        self.assertTrue(
            Project.objects.filter(display_name="Új Factory Chat projekt").exists()
        )
        self.assertEqual(
            desktop.locator("main").evaluate("node => getComputedStyle(node).display"),
            "grid",
        )
        desktop.close()

    def test_existing_project_question_returns_the_live_url(self) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        self._send(desktop, "Hogyan érhető el az alkalmazás?")
        desktop.get_by_text(self.live_server_url, exact=False).wait_for()
        self.assertNotIn(
            "kanonikus munkakörnyezet", desktop.locator("body").inner_text()
        )
        desktop.close()

    def test_default_state_uses_no_engineering_language(self) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        body = desktop.locator("body").inner_text()
        for forbidden in (
            "ExecutableScope object",
            "Active scope",
            "Governed conversation",
            "BREAK_GLASS_TERMINALIZED",
            "EXECUTION_QUEUED",
            "canonical server-owned approval card",
        ):
            self.assertNotIn(forbidden, body)
        self.assertIn("aktuális feladat", body.casefold())
        desktop.close()

    def test_memory_candidate_can_be_reviewed_without_an_internal_reference(
        self,
    ) -> None:
        entry = create_or_upsert_candidate(
            self.project,
            {
                "entry_key": "reviewable-browser-memory",
                "knowledge_type": "GENERAL",
                "title": "Javasolt emlékeztető",
                "content": "A kiadás ellenőrzése szükséges.",
                "source_reference": "browser",
                "evidence_references": ["browser"],
            },
            self.user.username,
        )
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        desktop.goto(f"{self.live_server_url}/?mode=memory")
        desktop.get_by_role("button", name="Átnézem").click()
        desktop.get_by_role("button", name="Jóváhagyom a frissítést").wait_for()
        desktop.get_by_role("button", name="Jóváhagyom a frissítést").click()
        desktop.get_by_text("Nincs jóváhagyásra váró memóriafrissítés.").wait_for()
        entry.refresh_from_db()
        self.assertEqual(entry.status, "ACTIVE")
        desktop.close()

    def test_mobile_planning_and_approval_flow(self) -> None:
        mobile = self._browser.new_page(viewport={"width": 390, "height": 844})
        self._login(mobile)
        self._complete_discovery(mobile, "Mobil terv")
        mobile.get_by_role("button", name="Jóváhagyom a tervet").click()
        mobile.get_by_text("A tervet jóváhagytad.", exact=False).wait_for()
        self.assertEqual(
            mobile.locator("main").evaluate("node => getComputedStyle(node).display"),
            "block",
        )
        self.assertTrue(mobile.locator(".mobile-tabs").is_visible())
        mobile.close()

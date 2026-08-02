"""Real Chromium acceptance for the conversational Factory Chat journey."""

from __future__ import annotations

import json
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

    def _mock_message_response(self, page: Page) -> None:
        """Keep UI acceptance deterministic; provider behavior has backend tests."""
        page.route(
            "**/factory/message/",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "messages": [
                            {"role": "owner", "text": "Teszt", "status": "COMPLETED"},
                            {
                                "role": "orki",
                                "text": "Orki gyors válasza.",
                                "status": "COMPLETED",
                            },
                        ],
                        "ok": True,
                        "orki_availability": {
                            "label": "Orki online",
                            "state": "available",
                        },
                    }
                ),
            ),
        )

    def test_new_initiative_stays_in_factory_chat_and_starts_a_conversation(
        self,
    ) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        messages = desktop.locator("#chat-messages .message")
        before = messages.count()
        desktop.get_by_role("button", name="Új kezdeményezés").click()
        messages.nth(before).wait_for()
        self.assertNotIn("admin", desktop.url)
        self.assertNotIn("registry", desktop.url)
        self.assertIn("Kezdjük el.", messages.nth(before).inner_text())
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(
            desktop.locator("main").evaluate("node => getComputedStyle(node).display"),
            "grid",
        )
        desktop.close()

    def test_command_k_returns_focus_to_the_conversation_composer(self) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        desktop.locator("body").click(position={"x": 5, "y": 5})
        desktop.keyboard.press("Control+K")
        self.assertEqual(desktop.evaluate("document.activeElement.id"), "message")
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

    def test_browser_sends_one_persisted_orki_response(self) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        sent_bodies: list[str] = []
        desktop.on(
            "request",
            lambda request: (
                sent_bodies.append(request.post_data or "")
                if request.url.endswith("/factory/message/")
                else None
            ),
        )
        self._mock_message_response(desktop)
        message = "K\u00e9sz\u00edts tervet."
        self._send(desktop, message)
        self.assertGreaterEqual(desktop.locator("#chat-messages .message").count(), 2)
        self.assertTrue(any(message in body for body in sent_bodies))
        self.assertIn("Orki", desktop.locator("#orki-status").inner_text())
        desktop.close()

    def test_desktop_keeps_panels_and_composer_fixed_while_only_chat_scrolls(
        self,
    ) -> None:
        desktop = self._browser.new_page(viewport={"width": 1440, "height": 960})
        self._login(desktop)
        desktop.evaluate(
            """() => {
                const messages = document.querySelector('#chat-messages');
                for (let i = 0; i < 80; i += 1) {
                    const markup = '<article class="message">' + String(i)
                        + '</article>';
                    messages.insertAdjacentHTML('beforeend', markup);
                }
            }"""
        )
        self.assertEqual(
            desktop.locator(".workspace").evaluate(
                "node => getComputedStyle(node).gridTemplateColumns.split(' ').length"
            ),
            3,
        )
        self.assertEqual(
            desktop.locator("#chat-messages").evaluate(
                "node => getComputedStyle(node).overflowY"
            ),
            "auto",
        )
        self.assertEqual(
            desktop.locator(".projects").evaluate(
                "node => getComputedStyle(node).overflowY"
            ),
            "auto",
        )
        self.assertTrue(desktop.locator(".composer").is_visible())
        desktop.close()

    def test_multiline_composer_preserves_shift_enter_and_blocks_empty_submit(
        self,
    ) -> None:
        desktop = self._browser.new_page(viewport={"width": 1280, "height": 900})
        self._login(desktop)
        self._mock_message_response(desktop)
        composer = desktop.get_by_label("Üzenet")
        composer.fill("első sor")
        composer.press("Shift+Enter")
        composer.type("második sor")
        self.assertEqual(composer.input_value(), "első sor\nmásodik sor")
        messages_before = desktop.locator("#chat-messages .message").count()
        composer.press("Enter")
        desktop.locator("#chat-messages .message").nth(messages_before).wait_for()
        self.assertEqual(
            desktop.locator("#chat-messages .message").count(), messages_before + 2
        )
        composer.fill("   ")
        composer.press("Enter")
        desktop.get_by_text("Üres üzenetet nem lehet küldeni.", exact=True).wait_for()
        desktop.close()

    def test_thinking_state_locks_composer_until_the_server_response_arrives(
        self,
    ) -> None:
        desktop = self._browser.new_page(viewport={"width": 1280, "height": 900})
        self._login(desktop)
        desktop.route(
            "**/factory/message/",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "messages": [
                            {"role": "owner", "text": "Teszt", "status": "COMPLETED"},
                            {
                                "role": "orki",
                                "text": "A szerver válasza megérkezett.",
                                "status": "COMPLETED",
                            },
                        ],
                        "ok": True,
                        "orki_availability": {
                            "label": "Orki online",
                            "state": "available",
                        },
                    }
                ),
            ),
        )
        desktop.evaluate(
            """() => {
                const originalFetch = window.fetch.bind(window);
                window.fetch = (...args) => new Promise((resolve, reject) => {
                    window.setTimeout(
                        () => originalFetch(...args).then(resolve, reject), 300
                    );
                });
            }"""
        )
        composer = desktop.locator("#message")
        composer.fill("Teszt")
        composer.press("Enter")
        desktop.locator("#orki-thinking").wait_for(state="visible")
        self.assertTrue(composer.is_disabled())
        submit_button = desktop.locator(".composer button[type='submit']")
        self.assertTrue(submit_button.is_disabled())
        desktop.locator("#chat-messages .message").nth(1).wait_for()
        desktop.wait_for_timeout(500)
        self.assertFalse(composer.is_disabled())
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

    def test_mobile_keeps_chat_primary_and_opens_secondary_panels_on_demand(
        self,
    ) -> None:
        mobile = self._browser.new_page(viewport={"width": 390, "height": 844})
        self._login(mobile)
        self.assertTrue(mobile.locator(".conversation").is_visible())
        self.assertFalse(mobile.locator(".mission").is_visible())
        self.assertFalse(mobile.locator(".projects").is_visible())
        self.assertTrue(mobile.locator(".mobile-nav").is_visible())
        mobile.get_by_role("button", name="Terv").click()
        self.assertTrue(mobile.locator(".mission").is_visible())
        self.assertFalse(mobile.locator(".conversation").is_visible())
        mobile.get_by_role("button", name="Chat").click()
        self.assertTrue(mobile.locator(".conversation").is_visible())
        mobile.get_by_role("button", name="Projektek").click()
        self.assertTrue(mobile.locator(".projects").is_visible())
        self.assertEqual(
            mobile.locator("main").evaluate(
                "node => getComputedStyle(node).gridTemplateColumns.split(' ').length"
            ),
            1,
        )
        mobile.close()

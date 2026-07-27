"""Application-registry tests for Storybook."""

from __future__ import annotations

from django.apps import apps


def test_storybook_application_is_loaded() -> None:
    """The configured Storybook Django application is available at startup."""
    config = apps.get_app_config("storybook")

    assert config.name == "storybook"
    assert config.label == "storybook"

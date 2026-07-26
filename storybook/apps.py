"""Application configuration for Storybook."""

from __future__ import annotations

from django.apps import AppConfig


class StorybookConfig(AppConfig):
    """Configure the Storybook Django application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "storybook"

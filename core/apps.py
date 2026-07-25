"""Application configuration for the core app."""

from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configure the minimal core application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

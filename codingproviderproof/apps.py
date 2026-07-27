"""Django application configuration for the governed coding proof."""

from __future__ import annotations

from django.apps import AppConfig


class CodingProviderProofConfig(AppConfig):
    """Configure the intentionally empty coding-provider proof application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "codingproviderproof"

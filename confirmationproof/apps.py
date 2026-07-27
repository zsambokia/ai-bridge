"""Application configuration for Confirmation Proof."""

from __future__ import annotations

from django.apps import AppConfig


class ConfirmationProofConfig(AppConfig):
    """Configure the Confirmation Proof Django application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "confirmationproof"

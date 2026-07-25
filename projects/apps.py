"""Django app configuration for the canonical Project domain."""

from __future__ import annotations

from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """Configure the canonical Project Registry application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "projects"

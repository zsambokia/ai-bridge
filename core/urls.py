"""URL routing for the core application."""

from __future__ import annotations

from django.urls import path

from core.views import health

urlpatterns = [path("", health, name="health")]

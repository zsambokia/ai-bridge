"""Root URL routing for AI Bridge."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [path("health/", include("core.urls"))]

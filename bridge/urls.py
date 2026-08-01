"""Root URL routing for AI Bridge."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("projects.ui_urls")),
    path("admin/", admin.site.urls),
    path("health/", include("core.urls")),
    path("mcp/", include("projects.urls")),
]

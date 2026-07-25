"""HTTP views for the core application."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse


def health(request: HttpRequest) -> JsonResponse:
    """Return the minimal service health contract."""
    return JsonResponse({"status": "ok", "service": "ai-bridge"})

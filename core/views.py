"""HTTP views for the core application."""

from __future__ import annotations

import os

from django.conf import settings
from django.http import HttpRequest, JsonResponse


def health(request: HttpRequest) -> JsonResponse:
    """Return runtime identity as well as the minimal service health contract."""
    return JsonResponse(
        {
            "status": "ok",
            "service": "ai-bridge",
            # Deployment targets must set this from their immutable artifact.
            # An absent value stays explicit rather than claiming the server's
            # source checkout is an accepted runtime revision.
            "build_sha": os.environ.get("AI_BRIDGE_BUILD_SHA", ""),
            "runtime_database": str(settings.DATABASES["default"]["NAME"]),
        }
    )

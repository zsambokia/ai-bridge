"""Internal Factory Development Mode entry point for the automated proof."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST

from .github_provider_e2e import run_github_provider_e2e_suite


@require_POST
@staff_member_required
def github_provider_e2e_proof(request: HttpRequest) -> JsonResponse:
    """Run the proof in the credential-owning Django process, never in admin."""
    try:
        body = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"status": "FAIL", "reason": "INVALID_JSON"}, status=400)
    provider_id = str(body.get("provider_id", "github"))
    owner = str(body.get("owner", "zsambokia"))
    try:
        result = run_github_provider_e2e_suite(
            provider_id=provider_id,
            owner=owner,
            evidence_root=Path(settings.BASE_DIR)
            / "docs"
            / "evidence"
            / "ai-bridge-2.0-mvp-proof"
            / "github-provider-e2e",
        )
    except ValueError as exc:
        return JsonResponse({"status": "FAIL", "reason": str(exc)}, status=502)
    return JsonResponse(result)

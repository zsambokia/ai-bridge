"""HTTP transport for the registered lightweight MCP operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST

from .mcp import invoke_operation, registered_operations


@require_POST
def mcp_endpoint(request: HttpRequest) -> JsonResponse:
    """Expose one JSON endpoint without creating a second domain API."""
    try:
        request_body: Any = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "INVALID_REQUEST", "error": "JSON required."}, status=400
        )
    if not isinstance(request_body, dict):
        return JsonResponse(
            {"status": "INVALID_REQUEST", "error": "Object required."}, status=400
        )
    operation = request_body.get("operation")
    payload = request_body.get("payload", {})
    if not isinstance(operation, str) or not isinstance(payload, dict):
        return JsonResponse(
            {"status": "INVALID_REQUEST", "error": "operation and payload required."},
            status=400,
        )
    if operation == "list_operations":
        return JsonResponse({"status": "OK", "operations": registered_operations()})
    result = invoke_operation(operation, payload, Path(settings.BASE_DIR))
    return JsonResponse(
        result, status=400 if result["status"] == "INVALID_OPERATION" else 200
    )

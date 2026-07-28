"""Streamable HTTP MCP transport for the public, read-only Bridge tools."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .governed_mcp import TOOL_SURFACE_VERSION, invoke_public_tool, public_tools

MCP_PROTOCOL_VERSION = "2025-03-26"
MCP_SERVER_INFO = {"name": "ai-bridge", "version": TOOL_SURFACE_VERSION}


def _response(payload: dict[str, Any], status: int = 200) -> JsonResponse:
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store, private"
    response["MCP-Protocol-Version"] = MCP_PROTOCOL_VERSION
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _error(request_id: Any, code: int, message: str, status: int = 400) -> JsonResponse:
    return _response(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        },
        status,
    )


def _authenticate(request: HttpRequest) -> JsonResponse | None:
    """Authenticate machine callers; missing configuration fails closed."""
    mode = settings.MCP_AUTH_MODE
    if mode != "bearer":
        return _error(None, -32001, "MCP authentication is not configured.", 503)
    configured_token = settings.MCP_API_TOKEN
    if not configured_token:
        return _error(None, -32001, "MCP authentication is not configured.", 503)
    supplied = request.headers.get("Authorization", "")
    expected = f"Bearer {configured_token}"
    if not hmac.compare_digest(supplied, expected):
        response = _error(None, -32001, "Authentication required.", 401)
        response["WWW-Authenticate"] = 'Bearer realm="ai-bridge-mcp"'
        return response
    return None


def _tool_result(name: str, arguments: Any, caller: str) -> dict[str, Any]:
    try:
        status = invoke_public_tool(name, arguments, caller=caller)
    except (ValueError, KeyError) as exc:
        return {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    except Exception:
        # The public MCP boundary must never turn an operational failure into a
        # JSON-RPC internal error. Do not expose exception details here.
        return {
            "content": [{"type": "text", "text": "INTERNAL_ERROR"}],
            "isError": True,
        }
    return {
        "content": [{"type": "text", "text": json.dumps(status, sort_keys=True)}],
        "structuredContent": status,
        "isError": False,
    }


@csrf_exempt
def mcp_endpoint(request: HttpRequest) -> HttpResponse:
    """Serve JSON-RPC over Streamable HTTP without browser-only middleware."""
    if request.method != "POST":
        response: HttpResponse = _error(None, -32600, "POST is required.", 405)
        response["Allow"] = "POST"
        return response
    authentication_error = _authenticate(request)
    if authentication_error is not None:
        return authentication_error
    caller = hashlib.sha256(
        request.headers["Authorization"].encode("utf-8")
    ).hexdigest()
    try:
        message = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error(None, -32700, "Parse error.")
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return _error(None, -32600, "JSON-RPC 2.0 object required.")
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {})
    if not isinstance(method, str) or not isinstance(params, dict):
        return _error(request_id, -32600, "Method and object params required.")
    if method == "initialize":
        version = params.get("protocolVersion")
        if not isinstance(version, str):
            return _error(request_id, -32602, "protocolVersion is required.")
        return _response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": MCP_SERVER_INFO,
                    "instructions": (
                        "AI Bridge exposes governed, project-scoped tools. "
                        "State-changing tools require a durable Product Owner "
                        "approval reference."
                    ),
                },
            }
        )
    if method == "notifications/initialized" and "id" not in message:
        response = HttpResponse(status=202)
        response["Cache-Control"] = "no-store, private"
        response["MCP-Protocol-Version"] = MCP_PROTOCOL_VERSION
        return response
    if method == "tools/list":
        return _response(
            {"jsonrpc": "2.0", "id": request_id, "result": {"tools": public_tools()}}
        )
    if method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str):
            return _error(request_id, -32602, "Tool name is required.")
        return _response(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": _tool_result(name, params.get("arguments", {}), caller),
            }
        )
    return _error(request_id, -32601, "Method not found.")

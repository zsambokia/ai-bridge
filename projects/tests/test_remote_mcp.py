"""Protocol, authentication and proxy acceptance tests for remote MCP."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client, override_settings

from projects.models import Project

TOKEN = "test-mcp-token"


def _post(client: Client, body: dict[str, object], token: str = TOKEN) -> Any:
    return client.post(
        "/mcp/",
        data=json.dumps(body),
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )


def _initialize(client: Client) -> Any:
    return _post(
        client,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {}},
        },
    )


@pytest.mark.django_db
def test_streamable_http_initializes_lists_and_calls_real_status() -> None:
    Project.objects.create(
        project_id="bridge-alpha",
        display_name="Bridge Alpha",
        repository_full_name="example/bridge-alpha",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    client = Client()
    initialization = _initialize(client)
    assert initialization.status_code == 200
    assert initialization.json()["result"]["capabilities"] == {
        "tools": {"listChanged": False}
    }
    assert initialization["Cache-Control"] == "no-store, private"

    tools = _post(
        client, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    )
    tool = tools.json()["result"]["tools"][0]
    assert tool["name"] == "factory.get_status"
    assert tool["inputSchema"]["type"] == "object"
    assert tool["annotations"]["readOnlyHint"] is True

    called = _post(
        client,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "factory.get_status", "arguments": {}},
        },
    )
    result = called.json()["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["projects"][0]["project_id"] == "bridge-alpha"


@pytest.mark.django_db
def test_authentication_and_protocol_failures_are_json_not_html() -> None:
    client = Client()
    missing = client.post("/mcp/", data="{}", content_type="application/json")
    assert missing.status_code == 401
    assert missing["Content-Type"].startswith("application/json")
    assert missing["WWW-Authenticate"].startswith("Bearer")
    assert missing.json()["error"]["code"] == -32001

    invalid = _post(
        client, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, "wrong"
    )
    assert invalid.status_code == 401

    malformed = _post(client, {"operation": "list_operations"})
    assert malformed.status_code == 400
    assert malformed.json()["error"]["code"] == -32600

    wrong_method = client.get("/mcp/", HTTP_AUTHORIZATION=f"Bearer {TOKEN}")
    assert wrong_method.status_code == 405
    assert wrong_method["Content-Type"].startswith("application/json")


@pytest.mark.django_db
@override_settings(MCP_API_TOKEN="")
def test_missing_server_secret_fails_closed() -> None:
    response = _initialize(Client())
    assert response.status_code == 503
    assert response.json()["error"]["code"] == -32001


@pytest.mark.django_db
def test_cloudflare_hosts_and_forwarded_https_are_accepted() -> None:
    client = Client()
    response = _initialize(
        Client(
            HTTP_HOST="stage.artificial-software-factory.com",
            HTTP_X_FORWARDED_PROTO="https",
        )
    )
    assert response.status_code == 200
    request = client.get("/health/", HTTP_X_FORWARDED_PROTO="https")
    assert request.wsgi_request.is_secure() is True

    unapproved = Client(HTTP_HOST="unapproved.example").post(
        "/mcp/", data="{}", content_type="application/json"
    )
    assert unapproved.status_code == 400

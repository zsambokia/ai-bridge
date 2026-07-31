"""Protocol, authentication and proxy acceptance tests for remote MCP."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import pytest
from django.test import Client, override_settings

from projects.models import (
    ConversationOrchestration,
    KnowledgeContextUse,
    Project,
    ProjectContext,
)

TOKEN = "test-mcp-token"


def test_local_settings_bind_the_ignored_e2e_token_to_mcp_runtime() -> None:
    """The local settings process reuses the existing .env loader safely."""
    environment = os.environ.copy()
    environment["MCP_API_TOKEN"] = ""
    environment["MCP_TEST_API_TOKEN"] = "test-local-e2e-token"
    environment["DJANGO_SETTINGS_MODULE"] = "bridge.settings.local"
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from django.conf import settings; "
                "import os; "
                "print(settings.MCP_API_TOKEN == os.environ['MCP_TEST_API_TOKEN'])"
            ),
        ],
        cwd=Path(__file__).resolve().parents[2],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.strip() == "True"


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


def _call(
    client: Client, request_id: int, name: str, arguments: dict[str, object]
) -> dict[str, Any]:
    response = _post(
        client,
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
    )
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["isError"] is False, result
    return result["structuredContent"]


def _acceptance_repository(root: Path) -> str:
    files = {
        "AGENTS.md": "# Acceptance repository\n",
        "docs/constitution/BRIDGE_CONSTITUTION.md": "# Constitution\n",
        "docs/workflows/EVIDENCE_DRIVEN_SPRINT.md": "# Workflow\n",
        "docs/contracts/HANDOFF_EXECUTION_CONTRACT.md": "# Handoff\n",
        "docs/roadmap/ROADMAP.md": "# Roadmap\n",
        "docs/akb/CURRENT_STATE.md": "# Current state\n",
        ".bridge/project.yaml": """project:
  id: acceptance-bridge
  name: Acceptance Bridge
repository:
  full_name: example/acceptance-bridge
  default_branch: main
  integration_branch: main
paths:
  agents: AGENTS.md
  constitution: docs/constitution/BRIDGE_CONSTITUTION.md
  execution_workflow: docs/workflows/EVIDENCE_DRIVEN_SPRINT.md
  handoff_contract: docs/contracts/HANDOFF_EXECUTION_CONTRACT.md
  roadmap: docs/roadmap/ROADMAP.md
  primary_current_state: docs/akb/CURRENT_STATE.md
release_gates:
  repository_wide:
    - id: python-version
      command: python --version
evidence:
  path_template: docs/evidence/{sprint_slug}
execution:
  allowed_terminal_states:
    - PASS — READY FOR PRODUCT OWNER REVIEW
""",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    for command in (
        ["git", "init", "-b", "main"],
        ["git", "config", "user.email", "acceptance@example.test"],
        ["git", "config", "user.name", "Acceptance Test"],
        [
            "git",
            "remote",
            "add",
            "origin",
            "https://github.com/example/acceptance-bridge.git",
        ],
        ["git", "add", "."],
        ["git", "commit", "-m", "acceptance baseline"],
    ):
        subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()


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
def test_storybook_request_flows_from_http_mcp_to_orchestrated_contract(
    tmp_path: Path,
) -> None:
    """Acceptance proof: natural-language request never enters execution.prepare."""
    baseline = _acceptance_repository(tmp_path)
    project = Project.objects.create(
        project_id="acceptance-bridge",
        display_name="Acceptance Bridge",
        repository_full_name="example/acceptance-bridge",
        definition_path=".bridge/project.yaml",
        onboarding_status=Project.OnboardingStatus.READY,
    )
    client = Client()
    with override_settings(BASE_DIR=tmp_path):
        listed = _post(
            client, {"jsonrpc": "2.0", "id": 10, "method": "tools/list", "params": {}}
        ).json()["result"]["tools"]
        prepare_schema = next(
            tool for tool in listed if tool["name"] == "execution.prepare"
        )["inputSchema"]
        assert set(prepare_schema["required"]) == {
            "project_id",
            "scope_identifier",
            "idempotency_key",
        }

        proposed = _call(
            client,
            11,
            "work_item.propose",
            {
                "project_id": project.project_id,
                "request": 'Create a new Django application named "storybook".',
                "idempotency_key": "storybook-propose-001",
            },
        )
        assert proposed["status"] == "SCOPE_PROPOSED"
        scope_identifier = proposed["scope"]["identifier"]
        review = _call(
            client,
            12,
            "scope.review",
            {"project_id": project.project_id, "scope_identifier": scope_identifier},
        )["proposal_review"]
        ProjectContext.objects.create(
            project=project,
            repository_full_name=project.repository_full_name,
            constitution_path="docs/constitution/BRIDGE_CONSTITUTION.md",
            roadmap_path="docs/roadmap/ROADMAP.md",
            sprint_path="docs/sprints/SPRINT_003.md",
            current_state_path="docs/akb/CURRENT_STATE.md",
            validation_status=ProjectContext.ValidationStatus.VALID,
            source_commit_sha=baseline,
        )
        confirmed = _call(
            client,
            13,
            "conversation.confirm",
            {
                "project_id": project.project_id,
                "scope_identifier": scope_identifier,
                "confirmation_text": "igen",
            },
        )
        assert confirmed["status"] == "EXECUTION_QUEUED"
        assert confirmed["proposal_version"] == review["proposal_version"]
        assert confirmed["proposal_hash"] == review["proposal_hash"]
        assert confirmed["orki"]["project_id"] == project.project_id
        assert confirmed["orki"]["context_package_hash"]
        assert confirmed["handoff_identifier"].startswith("bridge:acceptance-bridge")

        flow = ConversationOrchestration.objects.get(scope__identifier=scope_identifier)
        assert flow.orchestration_session_id
        assert flow.contract_id
        assert flow.run_id
        assert flow.contract is not None
        assert flow.run is not None
        assert flow.orchestration_session is not None
        assert flow.contract.orchestration_session_id == flow.orchestration_session_id
        assert flow.run.orchestration_session_id == flow.orchestration_session_id
        context_use = KnowledgeContextUse.objects.get(
            session=flow.orchestration_session
        )
        assert context_use.decision_id == flow.orchestration_session.decision.pk
        assert context_use.execution_contract_id == flow.contract_id
        assert context_use.execution_run_id == flow.run_id
        assert (
            flow.orchestration_session.context_package_hash
            == confirmed["orki"]["context_package_hash"]
        )

    assert not (tmp_path / "storybook").exists()


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

    invalid_utf8 = client.post(
        "/mcp/",
        data=b'{"confirmation_text":"Igen, j\xf3 lesz."}',
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {TOKEN}",
    )
    assert invalid_utf8.status_code == 400
    assert invalid_utf8.json()["error"]["code"] == -32700

    wrong_method = client.get("/mcp/", HTTP_AUTHORIZATION=f"Bearer {TOKEN}")
    assert wrong_method.status_code == 405
    assert wrong_method["Content-Type"].startswith("application/json")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, arguments",
    [
        ("execution.get_run_status", {}),
        ("execution.get_activity_summary", {}),
        ("execution.list_events", {}),
        (
            "execution.cancel",
            {
                "confirmation_reference": "PO-missing-execution",
                "idempotency_key": "cancel-missing-execution-001",
                "reason": "Product Owner requested cancellation",
                "requested_by": "test-product-owner",
            },
        ),
    ],
)
def test_execution_tools_return_controlled_missing_run_errors_over_mcp(
    name: str, arguments: dict[str, str]
) -> None:
    response = _post(
        Client(),
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": {"execution_token": str(uuid.uuid4()), **arguments},
            },
        },
    )

    assert response.status_code == 200
    result = response.json()["result"]
    assert result["isError"] is True
    assert result["content"][0]["text"] == "EXECUTION_NOT_FOUND"


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

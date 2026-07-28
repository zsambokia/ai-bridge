"""Protocol, authentication and proxy acceptance tests for remote MCP."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from django.test import Client, override_settings

from projects.models import GovernanceApproval, Project, ProjectContext

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
def test_storybook_request_flows_from_http_mcp_to_issued_contract(
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
        _call(client, 12, "scope.validate", {"scope_identifier": scope_identifier})

        approval = GovernanceApproval.objects.create(
            reference="PO-storybook-acceptance",
            project=project,
            approved_action="AUTHORIZE_EXECUTION",
            approved_by="Product Owner",
        )
        approved = _call(
            client,
            13,
            "scope.approve",
            {
                "scope_identifier": scope_identifier,
                "approval_reference": approval.reference,
                "idempotency_key": "storybook-approve-001",
            },
        )
        assert approved["status"] == "SCOPE_APPROVED"
        published = _call(
            client,
            14,
            "scope.publish",
            {
                "scope_identifier": scope_identifier,
                "idempotency_key": "storybook-publish-001",
            },
        )
        assert published["status"] == "SCOPE_PUBLISHED"
        ProjectContext.objects.create(
            project=project,
            repository_full_name=project.repository_full_name,
            constitution_path="docs/constitution/BRIDGE_CONSTITUTION.md",
            roadmap_path="docs/roadmap/ROADMAP.md",
            sprint_path=published["published_path"],
            current_state_path="docs/akb/CURRENT_STATE.md",
            validation_status=ProjectContext.ValidationStatus.VALID,
            source_commit_sha=baseline,
        )

        prepared = _call(
            client,
            15,
            "execution.prepare",
            {
                "project_id": project.project_id,
                "scope_identifier": scope_identifier,
                "idempotency_key": "storybook-prepare-001",
            },
        )
        assert prepared["status"] == "EXECUTION_PREPARED"
        token = prepared["preparation_token"]
        assert prepared["next_allowed_action"] == "contract.generate"
        status = _call(client, 16, "execution.get_status", {"preparation_token": token})
        handoff = _call(
            client, 17, "execution.render_handoff", {"preparation_token": token}
        )
        assert status["status"] == "PREPARED"
        assert published["published_path"] in handoff["handoff"]

        generated = _call(
            client,
            18,
            "contract.generate",
            {
                "project_id": project.project_id,
                "scope_identifier": scope_identifier,
                "preparation_token": token,
                "idempotency_key": "storybook-generate-001",
            },
        )
        assert generated["status"] == "EXECUTION_CONTRACT_GENERATED"
        contract_id = generated["execution_contract"]["handoff_identifier"]
        validated = _call(
            client,
            19,
            "contract.validate",
            {
                "handoff_identifier": contract_id,
                "idempotency_key": "storybook-validate-001",
            },
        )
        assert validated["status"] == "EXECUTION_CONTRACT_VALIDATED"
        issued = _call(
            client,
            20,
            "contract.issue",
            {
                "handoff_identifier": contract_id,
                "approval_reference": approval.reference,
                "idempotency_key": "storybook-issue-001",
            },
        )
        assert issued["status"] == "EXECUTION_CONTRACT_ISSUED"

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

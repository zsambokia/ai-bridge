from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from subprocess import CompletedProcess
from typing import cast
from urllib.request import Request

import pytest
from django.core.exceptions import ValidationError

from projects.governed_mcp import invoke_public_tool
from projects.models import ExecutionProvider, ProviderAuditEvent
from projects.provider_events import project_provider_line
from projects.providers import (
    CodexCliAdapter,
    GitHubAdapter,
    OpenAIAdapter,
    check_health,
    credential_value,
    model_adapter_for,
    public_provider,
    repository_adapter_for,
    select_model_provider,
    select_provider,
    select_repository_provider,
    structured_model_response,
)


@pytest.mark.django_db
def test_github_repository_writes_use_only_provider_binding_and_are_audited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="github-provider-e2e-test",
        name="GitHub provider E2E test",
        kind=ExecutionProvider.Kind.GITHUB,
        role=ExecutionProvider.Role.REPOSITORY_SERVICE,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="github-provider-e2e-test-adapter",
        enabled=True,
        capabilities=["REPOSITORY_WRITE"],
        credential_binding="AI_BRIDGE_GITHUB_PROVIDER_TOKEN",
    )
    requests: list[Request] = []

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            if requests[-1].get_method() == "GET":
                return b'{"login": "zsambokia"}'
            return b'{"id": 42, "full_name": "zsambokia/new-repo"}'

    def fake_urlopen(request: Request, timeout: int) -> Response:
        requests.append(request)
        assert timeout == 20
        return Response()

    monkeypatch.setenv("AI_BRIDGE_GITHUB_PROVIDER_TOKEN", "test-provider-token")
    monkeypatch.setattr("projects.providers.urlopen", fake_urlopen)

    result = GitHubAdapter().create_repository(
        entry,
        owner="zsambokia",
        name="new-repo",
        private=True,
        description="provider-only bootstrap test",
    )

    assert result["id"] == 42
    assert requests[0].full_url == "https://api.github.com/user"
    request = requests[1]
    assert request.full_url == "https://api.github.com/user/repos"
    assert request.get_method() == "POST"
    assert request.data is not None
    request_body = cast(bytes, request.data)
    assert json.loads(request_body.decode("utf-8")) == {
        "name": "new-repo",
        "private": True,
        "description": "provider-only bootstrap test",
    }
    assert request.get_header("Authorization") == "Bearer test-provider-token"
    event = ProviderAuditEvent.objects.get(
        provider=entry,
        action="GITHUB_API_REQUEST",
        details__path="user/repos",
    )
    assert event.action == "GITHUB_API_REQUEST"
    assert event.details == {
        "method": "POST",
        "path": "user/repos",
        "authentication": "PROVIDER_ENVIRONMENT_BINDING",
        "credential_binding": "AI_BRIDGE_GITHUB_PROVIDER_TOKEN",
    }
    assert "test-provider-token" not in str(event.details)


@pytest.mark.django_db
def test_github_adapter_reads_repository_content_at_explicit_ref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="github-read-test",
        name="GitHub read test",
        kind=ExecutionProvider.Kind.GITHUB,
        role=ExecutionProvider.Role.REPOSITORY_SERVICE,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="github-read-test-adapter",
        enabled=True,
        capabilities=["REPOSITORY_READ"],
        credential_binding="AI_BRIDGE_GITHUB_PROVIDER_TOKEN",
    )
    requests: list[Request] = []

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"content":"IyBSRUFETUU=","encoding":"base64","size":8}'

    def fake_urlopen(request: Request, timeout: int) -> Response:
        requests.append(request)
        assert timeout == 20
        return Response()

    monkeypatch.setenv("AI_BRIDGE_GITHUB_PROVIDER_TOKEN", "test-provider-token")
    monkeypatch.setattr("projects.providers.urlopen", fake_urlopen)
    result = GitHubAdapter().read_repository_file(
        entry,
        repository="zsambokia/proof",
        path="docs/read me.md",
        ref="a" * 40,
    )

    assert result["encoding"] == "base64"
    assert requests[0].full_url.endswith("contents/docs/read%20me.md?ref=" + "a" * 40)


@pytest.mark.django_db
def test_github_adapter_deletes_disposable_repository_and_accepts_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="github-delete-test",
        name="GitHub delete test",
        kind=ExecutionProvider.Kind.GITHUB,
        role=ExecutionProvider.Role.REPOSITORY_SERVICE,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="github-delete-test-adapter",
        enabled=True,
        capabilities=["REPOSITORY_WRITE"],
        credential_binding="AI_BRIDGE_GITHUB_PROVIDER_TOKEN",
    )

    class Response:
        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b""

    request_seen: list[Request] = []

    def fake_urlopen(request: Request, timeout: int) -> Response:
        request_seen.append(request)
        return Response()

    monkeypatch.setenv("AI_BRIDGE_GITHUB_PROVIDER_TOKEN", "test-provider-token")
    monkeypatch.setattr("projects.providers.urlopen", fake_urlopen)
    GitHubAdapter().delete_repository(entry, repository="zsambokia/disposable-proof")
    assert request_seen[0].get_method() == "DELETE"
    assert request_seen[0].full_url.endswith("repos/zsambokia/disposable-proof")


@pytest.mark.django_db
def test_repository_provider_selection_is_exact_and_requires_capabilities() -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="github-selection-test",
        name="GitHub selection test",
        kind=ExecutionProvider.Kind.GITHUB,
        role=ExecutionProvider.Role.REPOSITORY_SERVICE,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="github-selection-test-adapter",
        enabled=True,
        capabilities=["REPOSITORY_READ", "REPOSITORY_WRITE"],
    )

    assert (
        select_repository_provider(
            entry.provider_id, {"REPOSITORY_READ", "REPOSITORY_WRITE"}
        ).pk
        == entry.pk
    )
    canonical = ExecutionProvider.objects.get(provider_id="github")
    assert isinstance(repository_adapter_for(canonical), GitHubAdapter)
    entry.enabled = False
    entry.save(update_fields=["enabled"])
    with pytest.raises(ValueError, match="REPOSITORY_PROVIDER_UNAVAILABLE"):
        select_repository_provider(entry.provider_id)


@pytest.mark.django_db
def test_openai_model_requests_complete_json_artifact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="openai-json-artifact",
        name="OpenAI JSON artifact",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="openai-json-artifact-adapter",
        enabled=True,
        capabilities=["MODEL_INFERENCE"],
        credential_binding="OPENAI_API_KEY",
    )
    received: dict[str, object] = {}

    def fake_post(
        url: str, headers: dict[str, str], payload: dict[str, object]
    ) -> dict[str, object]:
        received.update({"url": url, "headers": headers, "payload": payload})
        return {"id": "response-test"}

    monkeypatch.setenv("OPENAI_API_KEY", "test-only-value")
    monkeypatch.setattr("projects.providers._post_json", fake_post)

    assert OpenAIAdapter().invoke_model(entry, "mission prompt") == {
        "id": "response-test"
    }
    assert received["payload"] == {
        "model": "gpt-4.1-mini",
        "input": "mission prompt",
        "max_output_tokens": 900,
        "text": {"format": {"type": "json_object"}},
    }


def test_codex_activity_projection_retains_redacted_structured_provider_output() -> (
    None
):
    received: list[dict[str, object]] = []

    CodexCliAdapter._project_activity(
        BytesIO(b'{"type":"item.completed","message":"token=secret"}\nplain output\n'),
        received.append,
    )

    assert received == [
        {
            "event_type": "PROVIDER_MESSAGE",
            "provider": "codex-cli",
            "provider_event_type": "item.completed",
            "provider_timestamp": "",
            "provider_event_id": "",
            "item_identifier": "",
            "message": "[REDACTED]",
            "command": "",
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "file_path": "",
            "source_stream": "stdout",
            "raw_event": {"type": "item.completed", "message": "[REDACTED]"},
        },
        {
            "event_type": "PROVIDER_MESSAGE",
            "provider": "codex-cli",
            "provider_event_type": "plain_text",
            "provider_timestamp": "",
            "provider_event_id": "",
            "item_identifier": "",
            "message": "plain output",
            "command": "",
            "exit_code": None,
            "stdout": "plain output",
            "stderr": "",
            "file_path": "",
            "source_stream": "stdout",
            "raw_event": {"raw_text": "plain output"},
        },
    ]


def test_codex_activity_projection_accepts_a_json_string_without_stopping() -> None:
    received: list[dict[str, object]] = []

    CodexCliAdapter._project_activity(
        BytesIO(b'"provider protocol message"\n{"type":"turn.completed"}\n'),
        received.append,
    )

    assert [event["event_type"] for event in received] == [
        "PROVIDER_MESSAGE",
        "PROVIDER_COMPLETED",
    ]
    assert received[0]["message"] == "provider protocol message"
    assert received[1]["message"] == "Codex reported turn.completed"


def test_codex_activity_projection_continues_after_an_unexpected_projection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[dict[str, object]] = []
    original = project_provider_line
    calls = 0

    def fail_once(line: bytes | str, *, source_stream: str) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise TypeError("unexpected provider event")
        return original(line, source_stream=source_stream)

    monkeypatch.setattr("projects.providers.project_provider_line", fail_once)

    CodexCliAdapter._project_activity(BytesIO(b"first\nsecond\n"), received.append)

    assert [event["event_type"] for event in received] == [
        "PROVIDER_WARNING",
        "PROVIDER_MESSAGE",
    ]
    assert received[0]["raw_event"] == {"error_type": "TypeError"}
    assert received[1]["message"] == "second"


def configure_codex_runtime(
    entry: ExecutionProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    related = ExecutionProvider.objects.get(provider_id="openai")
    related.status = ExecutionProvider.Status.ACTIVE
    related.credential_binding = "OPENAI_API_KEY"
    related.save(update_fields=["status", "credential_binding"])
    entry.related_provider = related
    entry.configuration = {"runtime_executable_environment": "BRIDGE_CODEX_EXECUTABLE"}
    entry.save(update_fields=["related_provider", "configuration"])
    monkeypatch.setenv("BRIDGE_CODEX_EXECUTABLE", "codex")
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-value")


@pytest.mark.django_db
def test_exact_selection_requires_an_active_capable_execution_provider() -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="provider-test",
        name="Provider test",
        kind=ExecutionProvider.Kind.CODEX,
        role=ExecutionProvider.Role.EXECUTION_AGENT,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="provider-test-adapter",
        enabled=True,
        capabilities=["CODE_EXECUTION"],
    )
    assert select_provider(entry.provider_id).pk == entry.pk
    entry.enabled = False
    entry.save(update_fields=["enabled"])
    with pytest.raises(ValueError, match="EXECUTOR_PROVIDER_UNAVAILABLE"):
        select_provider(entry.provider_id)


@pytest.mark.django_db
def test_model_selection_and_response_decoding_stay_in_provider_platform() -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="model-test",
        name="Model test",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        status=ExecutionProvider.Status.ACTIVE,
        adapter_key="model-test-adapter",
        enabled=True,
        capabilities=["MODEL_INFERENCE"],
        credential_binding="OPENAI_API_KEY",
    )
    assert select_model_provider(entry.provider_id).pk == entry.pk
    assert model_adapter_for(entry).__class__.__name__ == "OpenAIAdapter"
    assert structured_model_response(
        entry,
        {"output": [{"content": [{"text": '{"schema_version":"1.0"}'}]}]},
    ) == {"schema_version": "1.0"}
    entry.enabled = False
    entry.save(update_fields=["enabled"])
    with pytest.raises(ValueError, match="MODEL_PROVIDER_UNAVAILABLE"):
        select_model_provider(entry.provider_id)


@pytest.mark.django_db
def test_public_projection_never_reveals_configuration_or_secret_reference() -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="safe-provider",
        name="Safe provider",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        adapter_key="safe-provider-adapter",
        configuration={"endpoint": "private.example"},
        credential_binding="OPENAI_API_KEY",
    )
    projection = public_provider(entry)
    assert "configuration" not in projection
    assert "credential_binding" not in projection
    assert "OPENAI_API_KEY" not in str(projection)


@pytest.mark.django_db
def test_health_check_is_safe_and_mcp_provider_tools_are_read_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    entry = ExecutionProvider.objects.create(
        provider_id="health-provider",
        name="Health provider",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        adapter_key="health-provider-adapter",
        credential_binding="OPENAI_API_KEY",
    )
    result = check_health(entry)
    entry.refresh_from_db()
    assert result["status"] == "UNAVAILABLE"
    assert entry.health_status == ExecutionProvider.HealthStatus.UNAVAILABLE
    response = invoke_public_tool("provider.get", {"provider_id": entry.provider_id})
    assert response["provider_id"] == entry.provider_id
    assert "credential_binding" not in response


@pytest.mark.django_db
def test_configured_openai_health_status_is_a_valid_provider_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-value")
    entry = ExecutionProvider.objects.create(
        provider_id="configured-health-provider",
        name="Configured health provider",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        adapter_key="configured-health-provider-adapter",
        credential_binding="OPENAI_API_KEY",
    )

    result = check_health(entry)
    entry.refresh_from_db()

    assert result["status"] == ExecutionProvider.HealthStatus.CONFIGURED
    assert entry.health_status == ExecutionProvider.HealthStatus.CONFIGURED
    entry.full_clean()


@pytest.mark.django_db
def test_openai_provider_accepts_only_the_openai_environment_reference() -> None:
    entry = ExecutionProvider(
        provider_id="invalid-openai-provider",
        name="Invalid OpenAI provider",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        adapter_key="invalid-openai-provider-adapter",
        credential_binding="OTHER_API_KEY",
    )

    with pytest.raises(ValidationError, match="OPENAI_CREDENTIAL_BINDING_INVALID"):
        entry.full_clean()
    with pytest.raises(ValueError, match="OPENAI_CREDENTIAL_BINDING_INVALID"):
        credential_value(entry)


@pytest.mark.django_db
def test_codex_health_requires_authenticated_runtime_without_serializing_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.get(adapter_key="codex-cli")
    configure_codex_runtime(entry, monkeypatch)
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        "projects.providers.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(
            args, 1, "secret-output", "secret-error"
        ),
    )

    result = check_health(entry)
    entry.refresh_from_db()

    assert result["status"] == "UNAVAILABLE"
    assert result["reason"] == "codex authentication unavailable"
    assert entry.health_status == ExecutionProvider.HealthStatus.UNAVAILABLE
    assert "secret-output" not in str(entry.health)
    assert "secret-error" not in str(entry.last_test_result)


@pytest.mark.django_db
def test_codex_health_accepts_authenticated_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.get(adapter_key="codex-cli")
    configure_codex_runtime(entry, monkeypatch)
    monkeypatch.setenv("MCP_API_TOKEN", "test-mcp-token")
    monkeypatch.setenv("MCP_TEST_API_TOKEN", "test-local-e2e-token")
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        CodexCliAdapter,
        "is_authenticated",
        staticmethod(lambda value, environment: True),
    )
    monkeypatch.setattr(
        "projects.providers.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args, 0),
    )

    assert check_health(entry)["status"] == "HEALTHY"


@pytest.mark.django_db
def test_codex_health_uses_its_login_not_an_openai_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.get(adapter_key="codex-cli")
    related = ExecutionProvider.objects.get(provider_id="openai")
    related.status = ExecutionProvider.Status.ACTIVE
    related.credential_binding = "OPENAI_API_KEY"
    related.save(update_fields=["status", "credential_binding"])
    entry.related_provider = related
    entry.configuration = {"runtime_executable_environment": "BRIDGE_CODEX_EXECUTABLE"}
    entry.save(update_fields=["related_provider", "configuration"])
    monkeypatch.setenv("BRIDGE_CODEX_EXECUTABLE", "codex")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        CodexCliAdapter,
        "is_authenticated",
        staticmethod(lambda value, environment: True),
    )
    monkeypatch.setattr(
        "projects.providers.subprocess.run",
        lambda *args, **kwargs: CompletedProcess(args, 0),
    )

    assert check_health(entry)["status"] == "HEALTHY"


def test_codex_start_refuses_an_unauthenticated_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BRIDGE_CODEX_EXECUTABLE", "codex")
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        CodexCliAdapter,
        "is_authenticated",
        staticmethod(lambda value, environment: False),
    )

    with pytest.raises(ValueError, match="codex authentication unavailable"):
        CodexCliAdapter().start(repository=Path("C:/tmp"), prompt="safe prompt")


def test_codex_cancel_uses_taskkill_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[list[str]] = []

    def taskkill(args: list[str], **kwargs: object) -> CompletedProcess[str]:
        captured.append(args)
        return CompletedProcess(args, 0)

    monkeypatch.setattr("projects.providers.os.name", "nt")
    monkeypatch.setattr("projects.providers.subprocess.run", taskkill)

    CodexCliAdapter().cancel("42")

    assert captured == [["taskkill", "/PID", "42", "/T", "/F"]]


def test_codex_status_uses_native_windows_process_probe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("projects.providers.os.name", "nt")
    monkeypatch.setattr(
        "projects.providers._windows_process_is_running", lambda process_id: False
    )

    assert CodexCliAdapter().status("42") == "FINISHED"


@pytest.mark.django_db
def test_codex_launch_context_excludes_api_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = ExecutionProvider.objects.get(adapter_key="codex-cli")
    configure_codex_runtime(entry, monkeypatch)
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        CodexCliAdapter,
        "is_authenticated",
        staticmethod(lambda value, environment: True),
    )
    captured: list[dict[str, object]] = []

    def run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        captured.append(dict(kwargs))
        return CompletedProcess([], 0)

    monkeypatch.setattr("projects.providers.subprocess.run", run)
    assert check_health(entry)["status"] == "HEALTHY"
    assert captured
    environment = captured[0].get("env")
    assert isinstance(environment, dict)
    assert "OPENAI_API_KEY" not in environment
    assert "MCP_API_TOKEN" not in environment
    assert "MCP_TEST_API_TOKEN" not in environment


@pytest.mark.django_db
def test_codex_relationship_is_non_secret_and_requires_openai_dependency() -> None:
    openai = ExecutionProvider.objects.get(provider_id="openai")
    codex = ExecutionProvider.objects.get(provider_id="codex-cli")
    codex.related_provider = openai
    codex.authentication_mode = ExecutionProvider.AuthenticationMode.CODEX_CLI_LOGIN
    codex.full_clean()

    codex.credential_binding = "OPENAI_API_KEY"
    with pytest.raises(ValidationError, match="CODEX_CREDENTIAL_DUPLICATION_FORBIDDEN"):
        codex.full_clean()

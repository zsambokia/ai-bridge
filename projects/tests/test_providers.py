from __future__ import annotations

from io import BytesIO
from pathlib import Path
from subprocess import CompletedProcess

import pytest
from django.core.exceptions import ValidationError

from projects.governed_mcp import invoke_public_tool
from projects.models import ExecutionProvider
from projects.provider_events import project_provider_line
from projects.providers import (
    CodexCliAdapter,
    check_health,
    credential_value,
    model_adapter_for,
    public_provider,
    select_model_provider,
    select_provider,
    structured_model_response,
)


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

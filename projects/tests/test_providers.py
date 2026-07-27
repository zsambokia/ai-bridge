from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

import pytest
from django.core.exceptions import ValidationError

from projects.governed_mcp import invoke_public_tool
from projects.models import ExecutionProvider
from projects.providers import (
    CodexCliAdapter,
    check_health,
    credential_value,
    public_provider,
    select_provider,
)


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
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        CodexCliAdapter, "is_authenticated", staticmethod(lambda value: True)
    )

    assert check_health(entry)["status"] == "HEALTHY"


def test_codex_start_refuses_an_unauthenticated_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("projects.providers.shutil.which", lambda value: value)
    monkeypatch.setattr(
        CodexCliAdapter, "is_authenticated", staticmethod(lambda value: False)
    )

    with pytest.raises(ValueError, match="CODEX_RUNTIME_UNAVAILABLE"):
        CodexCliAdapter().start(repository=Path("C:/tmp"), prompt="safe prompt")


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

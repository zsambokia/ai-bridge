from __future__ import annotations

import pytest

from projects.governed_mcp import invoke_public_tool
from projects.models import ExecutionProvider
from projects.providers import check_health, public_provider, select_provider


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
def test_health_check_is_safe_and_mcp_provider_tools_are_read_only() -> None:
    entry = ExecutionProvider.objects.create(
        provider_id="health-provider",
        name="Health provider",
        kind=ExecutionProvider.Kind.OPENAI,
        role=ExecutionProvider.Role.MODEL_API,
        adapter_key="health-provider-adapter",
        credential_binding="ABSENT_PROVIDER_TOKEN",
    )
    result = check_health(entry)
    entry.refresh_from_db()
    assert result["status"] == "UNAVAILABLE"
    assert entry.health_status == ExecutionProvider.HealthStatus.UNAVAILABLE
    response = invoke_public_tool("provider.get", {"provider_id": entry.provider_id})
    assert response["provider_id"] == entry.provider_id
    assert "credential_binding" not in response

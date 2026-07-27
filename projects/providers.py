"""Provider-neutral registry, safe projections, and bounded adapter contracts."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.utils import timezone

from .models import ExecutionProvider, ProviderAuditEvent

CAPABILITIES = {
    "CODE_EXECUTION",
    "MODEL_INFERENCE",
    "REPOSITORY_READ",
    "REPOSITORY_WRITE",
    "BRANCH_MANAGEMENT",
    "PULL_REQUEST_MANAGEMENT",
    "DATA_QUERY_READ",
    "DATA_QUERY_WRITE",
    "STREAMING",
    "CANCELLATION",
    "STATUS_POLLING",
    "USAGE_REPORTING",
    "HEALTH_CHECK",
}


@dataclass(frozen=True)
class ProviderStart:
    execution_id: str
    workspace_identifier: str


class ExecutionAdapter(Protocol):
    name: str

    def start(self, *, repository: Path, prompt: str) -> ProviderStart: ...
    def status(self, execution_id: str) -> str: ...
    def cancel(self, execution_id: str) -> None: ...


class ModelAdapter(Protocol):
    def invoke_model(
        self, entry: ExecutionProvider, prompt: str
    ) -> dict[str, object]: ...


class RepositoryAdapter(Protocol):
    def read_repository_state(
        self, entry: ExecutionProvider, repository: str, branch: str
    ) -> dict[str, object]: ...


class DataAdapter(Protocol):
    def execute_read(
        self, entry: ExecutionProvider, query: str
    ) -> dict[str, object]: ...


def credential_value(entry: ExecutionProvider) -> str:
    """Resolve a declared binding only at dispatch time and never serialize it."""
    if not entry.credential_binding:
        raise ValueError("PROVIDER_CREDENTIAL_BINDING_REQUIRED")
    value = os.environ.get(entry.credential_binding)
    if not value:
        raise ValueError("PROVIDER_CREDENTIAL_UNAVAILABLE")
    return value


def _post_json(
    url: str, headers: dict[str, str], body: dict[str, object]
) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:  # noqa: S310
            decoded = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise ValueError("PROVIDER_REMOTE_REQUEST_FAILED") from exc
    if not isinstance(decoded, dict):
        raise ValueError("PROVIDER_REMOTE_RESPONSE_INVALID")
    return decoded


class OpenAIAdapter:
    """Bounded Responses API client; it is a model API, not an executor."""

    def invoke_model(self, entry: ExecutionProvider, prompt: str) -> dict[str, object]:
        token = credential_value(entry)
        model = str(entry.configuration.get("model", "gpt-4.1-mini"))
        base_url = str(entry.configuration.get("base_url", "https://api.openai.com/v1"))
        return _post_json(
            f"{base_url.rstrip('/')}/responses",
            {"Authorization": f"Bearer {token}"},
            {"model": model, "input": prompt[:4000], "max_output_tokens": 256},
        )


class ClaudeAdapter:
    """Bounded Messages API client; it is a model API, not an executor."""

    def invoke_model(self, entry: ExecutionProvider, prompt: str) -> dict[str, object]:
        token = credential_value(entry)
        model = str(entry.configuration.get("model", "claude-3-5-haiku-latest"))
        base_url = str(entry.configuration.get("base_url", "https://api.anthropic.com"))
        return _post_json(
            f"{base_url.rstrip('/')}/v1/messages",
            {"x-api-key": token, "anthropic-version": "2023-06-01"},
            {
                "model": model,
                "max_tokens": 256,
                "messages": [{"role": "user", "content": prompt[:4000]}],
            },
        )


class GitHubAdapter:
    """Bounded repository read client; writes remain governed elsewhere."""

    def read_repository_state(
        self, entry: ExecutionProvider, repository: str, branch: str
    ) -> dict[str, object]:
        token = credential_value(entry)
        url = f"https://api.github.com/repos/{repository}/branches/{branch}"
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310
                decoded = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError) as exc:
            raise ValueError("PROVIDER_REMOTE_REQUEST_FAILED") from exc
        if not isinstance(decoded, dict):
            raise ValueError("PROVIDER_REMOTE_RESPONSE_INVALID")
        return decoded


class BigQueryAdapter:
    """Bounded BigQuery REST read client; it never provides a write operation."""

    def execute_read(self, entry: ExecutionProvider, query: str) -> dict[str, object]:
        token = credential_value(entry)
        project = str(entry.configuration.get("project_id", ""))
        if not project or not query.lstrip().upper().startswith(("SELECT", "WITH")):
            raise ValueError("BIGQUERY_READ_CONFIGURATION_INVALID")
        return _post_json(
            f"https://bigquery.googleapis.com/bigquery/v2/projects/{project}/queries",
            {"Authorization": f"Bearer {token}"},
            {"query": query, "useLegacySql": False, "maximumBytesBilled": "10000000"},
        )


class CodexCliAdapter:
    name = "codex-cli"

    def start(self, *, repository: Path, prompt: str) -> ProviderStart:
        executable = os.environ.get("BRIDGE_CODEX_EXECUTABLE", "codex")
        process = subprocess.Popen(
            [
                executable,
                "exec",
                "--json",
                "--sandbox",
                "workspace-write",
                "-C",
                str(repository),
                prompt,
            ],
            cwd=repository,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )  # noqa: S603
        return ProviderStart(str(process.pid), str(repository))

    def status(self, execution_id: str) -> str:
        try:
            os.kill(int(execution_id), 0)
        except OSError:
            return "FINISHED"
        return "RUNNING"

    def cancel(self, execution_id: str) -> None:
        os.kill(int(execution_id), 15)


def adapter_for(entry: ExecutionProvider) -> ExecutionAdapter:
    if entry.adapter_key == "codex-cli":
        return CodexCliAdapter()
    raise ValueError("PROVIDER_EXECUTION_ADAPTER_UNAVAILABLE")


def select_provider(
    identity: str, required_capabilities: set[str] | None = None
) -> ExecutionProvider:
    """Select exact identity only; never silently fall back by priority."""
    try:
        entry = ExecutionProvider.objects.get(provider_id=identity)
    except ExecutionProvider.DoesNotExist as exc:
        raise ValueError("EXECUTOR_PROVIDER_UNAVAILABLE") from exc
    required = required_capabilities or {"CODE_EXECUTION"}
    if (
        not entry.enabled
        or entry.status != ExecutionProvider.Status.ACTIVE
        or entry.role != ExecutionProvider.Role.EXECUTION_AGENT
        or not required.issubset(set(entry.capabilities))
    ):
        raise ValueError("EXECUTOR_PROVIDER_UNAVAILABLE")
    return entry


def public_provider(entry: ExecutionProvider) -> dict[str, object]:
    """Public projection intentionally excludes config and credential references."""
    return {
        "provider_id": entry.provider_id,
        "name": entry.name,
        "kind": entry.kind,
        "role": entry.role,
        "status": entry.status,
        "enabled": entry.enabled,
        "priority": entry.priority,
        "capabilities": entry.capabilities,
        "health_status": entry.health_status,
        "health": {
            k: v
            for k, v in entry.health.items()
            if k in {"status", "checked_at", "reason"}
        },
        "last_health_at": entry.last_health_at.isoformat()
        if entry.last_health_at
        else None,
    }


def check_health(entry: ExecutionProvider) -> dict[str, object]:
    """Validate local readiness without issuing a remote provider request."""
    result: dict[str, object]
    if entry.adapter_key == "codex-cli":
        ready = (
            shutil.which(os.environ.get("BRIDGE_CODEX_EXECUTABLE", "codex")) is not None
        )
        result = {
            "status": "HEALTHY" if ready else "UNAVAILABLE",
            "reason": None if ready else "codex executable unavailable",
        }
    elif not entry.credential_binding or not os.environ.get(entry.credential_binding):
        result = {"status": "UNAVAILABLE", "reason": "credential binding unavailable"}
    else:
        result = {
            "status": "CONFIGURED",
            "reason": "credential reference resolved; remote call not performed",
        }
    result["checked_at"] = timezone.now().isoformat()
    entry.health = result
    entry.health_status = str(result["status"])
    entry.last_health_at = timezone.now()
    entry.last_test_result = result
    entry.save(
        update_fields=[
            "health",
            "health_status",
            "last_health_at",
            "last_test_result",
            "updated_at",
        ]
    )
    ProviderAuditEvent.objects.create(
        provider=entry, action="HEALTH_CHECK", details=result
    )
    return result

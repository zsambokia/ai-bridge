"""Provider-neutral registry, safe projections, and bounded adapter contracts."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from typing import BinaryIO, Callable, Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
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

CODEX_EXECUTABLE_ENVIRONMENT_REFERENCE = "BRIDGE_CODEX_EXECUTABLE"
SAFE_SUBPROCESS_ENVIRONMENT_KEYS = (
    "APPDATA",
    "CODEX_HOME",
    "COMSPEC",
    "HOME",
    "LANG",
    "LC_ALL",
    "LOCALAPPDATA",
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "WINDIR",
)


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
    if (
        entry.kind == ExecutionProvider.Kind.OPENAI
        and entry.credential_binding != "OPENAI_API_KEY"
    ):
        raise ValueError("OPENAI_CREDENTIAL_BINDING_INVALID")
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

    def __init__(self, entry: ExecutionProvider | None = None) -> None:
        self.entry = entry

    def _runtime_executable(self) -> str:
        """Resolve the governed executable reference; never fall back to PATH."""
        if self.entry is None:
            configured_reference = CODEX_EXECUTABLE_ENVIRONMENT_REFERENCE
        else:
            configured_reference = self.entry.configuration.get(
                "runtime_executable_environment"
            )
        if configured_reference != CODEX_EXECUTABLE_ENVIRONMENT_REFERENCE:
            raise ValueError("CODEX_RUNTIME_CONFIGURATION_INVALID")
        executable = os.environ.get(CODEX_EXECUTABLE_ENVIRONMENT_REFERENCE, "").strip()
        if not executable:
            raise ValueError("CODEX_RUNTIME_EXECUTABLE_UNAVAILABLE")
        resolved = shutil.which(executable)
        if not resolved:
            raise ValueError("CODEX_RUNTIME_EXECUTABLE_UNAVAILABLE")
        return resolved

    @staticmethod
    def _sanitized_environment() -> dict[str, str]:
        """Keep OS and Codex-login context, never pass API or MCP secrets onward."""
        return {
            key: value
            for key in SAFE_SUBPROCESS_ENVIRONMENT_KEYS
            if (value := os.environ.get(key))
        }

    def _related_connection_is_resolved(self) -> bool:
        """Check the declared dependency without copying its secret to Codex."""
        if self.entry is None or self.entry.related_provider_id is None:
            return False
        related = self.entry.related_provider
        return bool(
            related
            and related.kind == ExecutionProvider.Kind.OPENAI
            and related.status == ExecutionProvider.Status.ACTIVE
            and related.credential_binding
            and os.environ.get(related.credential_binding)
        )

    @staticmethod
    def is_authenticated(executable: str, environment: dict[str, str]) -> bool:
        """Check local Codex authentication without reading or retaining credentials."""
        try:
            completed = subprocess.run(
                [executable, "login", "status"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
                shell=False,
                env=environment,
            )  # noqa: S603
        except (OSError, subprocess.TimeoutExpired):
            return False
        return completed.returncode == 0

    def readiness(self, workspace: Path) -> dict[str, object]:
        """Validate the same sanitized process context used for real dispatch."""
        if self.entry is not None and not self._related_connection_is_resolved():
            return {"ready": False, "reason": "related OpenAI connection unavailable"}
        try:
            executable = self._runtime_executable()
        except ValueError as exc:
            return {"ready": False, "reason": str(exc)}
        environment = self._sanitized_environment()
        if not self.is_authenticated(executable, environment):
            return {"ready": False, "reason": "codex authentication unavailable"}
        try:
            probe = subprocess.run(
                [executable, "exec", "--help"],
                cwd=workspace,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
                shell=False,
                env=environment,
            )  # noqa: S603
        except (OSError, subprocess.TimeoutExpired):
            return {"ready": False, "reason": "codex subprocess launch unavailable"}
        if probe.returncode:
            return {"ready": False, "reason": "codex subprocess launch unavailable"}
        return {"ready": True, "executable": executable, "environment": environment}

    def start(self, *, repository: Path, prompt: str) -> ProviderStart:
        return self._start(repository=repository, prompt=prompt)

    def start_with_activity(
        self,
        *,
        repository: Path,
        prompt: str,
        activity_callback: Callable[[dict[str, object]], None],
    ) -> ProviderStart:
        """Launch Codex and project its actual JSON stream as safe activity events."""
        return self._start(
            repository=repository,
            prompt=prompt,
            activity_callback=activity_callback,
        )

    def _start(
        self,
        *,
        repository: Path,
        prompt: str,
        activity_callback: Callable[[dict[str, object]], None] | None = None,
    ) -> ProviderStart:
        readiness = self.readiness(repository)
        if not readiness["ready"]:
            raise ValueError(str(readiness["reason"]))
        resolved_executable = str(readiness["executable"])
        environment = cast(dict[str, str], readiness["environment"])
        capture_activity = bool(
            activity_callback and settings.AI_BRIDGE_DEV_EXECUTION_ACTIVITY
        )
        process = subprocess.Popen(
            [
                resolved_executable,
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
            stdout=subprocess.PIPE if capture_activity else subprocess.DEVNULL,
            stderr=subprocess.STDOUT if capture_activity else subprocess.DEVNULL,
            shell=False,
            env=environment,
        )  # noqa: S603
        time.sleep(0.15)
        if process.poll() is not None:
            raise ValueError("CODEX_SUBPROCESS_EXITED_EARLY")
        if capture_activity and activity_callback and process.stdout is not None:
            Thread(
                target=self._project_activity,
                args=(process.stdout, activity_callback),
                daemon=True,
            ).start()
        return ProviderStart(str(process.pid), str(repository))

    @staticmethod
    def _project_activity(
        stream: BinaryIO, activity_callback: Callable[[dict[str, object]], None]
    ) -> None:
        """Expose output occurrence and type, never provider text or credentials."""
        for line in stream:
            try:
                decoded = json.loads(line)
            except json.JSONDecodeError:
                activity_type = "output"
            else:
                activity_type = str(decoded.get("type", "output"))[:80]
            activity_callback(
                {
                    "activity_type": activity_type,
                    "message": f"Codex reported {activity_type}",
                }
            )

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
        return CodexCliAdapter(entry)
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
        readiness = CodexCliAdapter(entry).readiness(Path.cwd())
        ready = bool(readiness["ready"])
        reason = None if ready else str(readiness["reason"])
        result = {
            "status": (
                "HEALTHY"
                if ready
                else (
                    "MISCONFIGURED"
                    if reason == "CODEX_RUNTIME_CONFIGURATION_INVALID"
                    else "UNAVAILABLE"
                )
            ),
            "reason": reason,
            "execution_ready": ready,
        }
    elif (
        entry.kind == ExecutionProvider.Kind.OPENAI
        and entry.credential_binding != "OPENAI_API_KEY"
    ):
        result = {
            "status": "MISCONFIGURED",
            "reason": "OpenAI credential binding must be OPENAI_API_KEY",
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


def mark_runtime_unavailable(entry: ExecutionProvider, reason: str) -> None:
    """Invalidate a stale readiness projection after a launch failure."""
    result = {
        "status": "UNAVAILABLE",
        "reason": reason[:100],
        "execution_ready": False,
        "checked_at": timezone.now().isoformat(),
    }
    entry.health = result
    entry.health_status = ExecutionProvider.HealthStatus.UNAVAILABLE
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
        provider=entry, action="RUNTIME_FAILURE", details=result
    )

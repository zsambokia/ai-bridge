"""Provider-neutral registry, safe projections, and bounded adapter contracts."""

from __future__ import annotations

import json
import os
import shutil
import signal
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
from .provider_events import project_provider_line

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


def _windows_process_is_running(process_id: int) -> bool:
    """Return whether a PID still has an active Windows process handle.

    ``os.kill(pid, 0)`` is not a reliable existence probe on Windows: it can
    report success for an already-exited PID.  Use the native process handle
    and exit code instead so status polling cannot preserve a ghost run.
    """
    import ctypes

    process_query_limited_information = 0x1000
    still_active = 259
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(process_query_limited_information, False, process_id)
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return False
        return exit_code.value == still_active
    finally:
        kernel32.CloseHandle(handle)


@dataclass(frozen=True)
class ProviderStart:
    execution_id: str
    workspace_identifier: str


class ExecutionAdapter(Protocol):
    name: str

    def start(self, *, repository: Path, prompt: str) -> ProviderStart: ...
    def start_with_runtime(
        self, *, runtime: dict[str, object], prompt: str
    ) -> ProviderStart: ...
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

    def start_with_runtime(
        self, *, runtime: dict[str, object], prompt: str
    ) -> ProviderStart:
        """Start only from the manager-issued, already-verified descriptor."""
        required = {
            "cwd",
            "repository_root",
            "repository_url",
            "base_commit_sha",
            "python_executable",
            "virtual_environment",
            "environment",
            "database_profile",
            "application_database",
            "migration_state",
            "seed_state",
            "runtime_services",
            "provider_environment",
            "health_state",
            "workspace_id",
            "execution_token",
        }
        if required - set(runtime):
            raise ValueError("WORKSPACE_RUNTIME_DESCRIPTOR_INVALID")
        repository = Path(str(runtime["repository_root"])).resolve()
        if Path(str(runtime["cwd"])).resolve() != repository:
            raise ValueError("WORKSPACE_RUNTIME_DESCRIPTOR_INVALID")
        environment = runtime["environment"]
        if not isinstance(environment, dict) or not isinstance(
            runtime["database_profile"], dict
        ):
            raise ValueError("WORKSPACE_RUNTIME_DESCRIPTOR_INVALID")
        return self._start(
            repository=repository,
            prompt=prompt,
            runtime_environment={
                str(key): str(value) for key, value in environment.items()
            },
        )

    def start_with_runtime_activity(
        self,
        *,
        runtime: dict[str, object],
        prompt: str,
        activity_callback: Callable[[dict[str, object]], None],
    ) -> ProviderStart:
        required = {
            "cwd",
            "repository_root",
            "repository_url",
            "base_commit_sha",
            "python_executable",
            "virtual_environment",
            "environment",
            "database_profile",
            "application_database",
            "migration_state",
            "seed_state",
            "runtime_services",
            "provider_environment",
            "health_state",
            "workspace_id",
            "execution_token",
        }
        if required - set(runtime):
            raise ValueError("WORKSPACE_RUNTIME_DESCRIPTOR_INVALID")
        repository = Path(str(runtime["repository_root"])).resolve()
        environment = runtime["environment"]
        if (
            Path(str(runtime["cwd"])).resolve() != repository
            or not isinstance(environment, dict)
            or not isinstance(runtime["database_profile"], dict)
        ):
            raise ValueError("WORKSPACE_RUNTIME_DESCRIPTOR_INVALID")
        return self._start(
            repository=repository,
            prompt=prompt,
            activity_callback=activity_callback,
            runtime_environment={
                str(key): str(value) for key, value in environment.items()
            },
        )

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
        runtime_environment: dict[str, str] | None = None,
    ) -> ProviderStart:
        readiness = self.readiness(repository)
        if not readiness["ready"]:
            raise ValueError(str(readiness["reason"]))
        resolved_executable = str(readiness["executable"])
        environment = cast(dict[str, str], readiness["environment"])
        if runtime_environment:
            environment = {**environment, **runtime_environment}
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
            stderr=subprocess.PIPE if capture_activity else subprocess.DEVNULL,
            shell=False,
            env=environment,
        )  # noqa: S603
        time.sleep(0.15)
        if process.poll() is not None:
            raise ValueError("CODEX_SUBPROCESS_EXITED_EARLY")
        if capture_activity and activity_callback:
            for stream_name, stream in (
                ("stdout", process.stdout),
                ("stderr", process.stderr),
            ):
                if stream is not None:
                    Thread(
                        target=self._project_activity,
                        args=(stream, activity_callback, stream_name),
                        daemon=True,
                    ).start()
            Thread(
                target=self._monitor_activity,
                args=(process, activity_callback),
                daemon=True,
            ).start()
        return ProviderStart(str(process.pid), str(repository))

    @staticmethod
    def _monitor_activity(
        process: subprocess.Popen[bytes],
        activity_callback: Callable[[dict[str, object]], None],
    ) -> None:
        """Keep the durable worker lease alive and record the actual exit."""
        while True:
            exit_code = process.poll()
            if exit_code is not None:
                activity_callback(
                    {
                        "event_type": "PROVIDER_COMPLETED",
                        "provider": "codex-cli",
                        "provider_event_type": "process.exit",
                        "message": "Codex provider process exited",
                        "exit_code": exit_code,
                    }
                )
                return
            activity_callback(
                {
                    "event_type": "PROVIDER_ACTIVITY_RECEIVED",
                    "provider": "codex-cli",
                    "provider_event_type": "process.heartbeat",
                    "message": "Codex provider process remains active",
                }
            )
            time.sleep(20)

    @staticmethod
    def _project_activity(
        stream: BinaryIO,
        activity_callback: Callable[[dict[str, object]], None],
        source_stream: str = "stdout",
    ) -> None:
        """Project each stdout/stderr line without letting one line end the reader."""
        for line in stream:
            try:
                activity = project_provider_line(line, source_stream=source_stream)
            except Exception as error:  # pragma: no cover - defensive provider boundary
                # Provider output is untrusted.  Keep reading after a malformed or
                # newly introduced event shape, without retaining exception text
                # that could include provider content or credentials.
                activity = {
                    "event_type": "PROVIDER_WARNING",
                    "provider": "codex-cli",
                    "provider_event_type": "projection_error",
                    "provider_timestamp": "",
                    "provider_event_id": "",
                    "item_identifier": "",
                    "message": "Codex activity projection failed; reading continues",
                    "command": "",
                    "exit_code": None,
                    "stdout": "",
                    "stderr": "",
                    "file_path": "",
                    "source_stream": source_stream,
                    "raw_event": {"error_type": type(error).__name__},
                }
            try:
                activity_callback(activity)
            except Exception:  # pragma: no cover - persistence boundary
                # A transient persistence failure must not terminate the provider
                # reader or the provider subprocess.  A subsequent line can still
                # be persisted once the database is available again.
                continue

    def status(self, execution_id: str) -> str:
        process_id = int(execution_id)
        if os.name == "nt":
            return "RUNNING" if _windows_process_is_running(process_id) else "FINISHED"
        try:
            os.kill(process_id, 0)
        except OSError:
            return "FINISHED"
        return "RUNNING"

    def cancel(self, execution_id: str) -> None:
        """Terminate the governed child process using the host platform API."""
        process_id = int(execution_id)
        if os.name == "nt":
            completed = subprocess.run(
                ["taskkill", "/PID", str(process_id), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=False,
            )  # noqa: S603
            if completed.returncode:
                raise OSError("CODEX_PROCESS_TERMINATION_FAILED")
            return
        os.kill(process_id, signal.SIGTERM)


def adapter_for(entry: ExecutionProvider) -> ExecutionAdapter:
    if entry.adapter_key == "codex-cli":
        return CodexCliAdapter(entry)
    raise ValueError("PROVIDER_EXECUTION_ADAPTER_UNAVAILABLE")


def model_adapter_for(entry: ExecutionProvider) -> ModelAdapter:
    """Resolve a model adapter from the canonical provider registry entry."""
    adapters: dict[str, ModelAdapter] = {
        ExecutionProvider.Kind.OPENAI: OpenAIAdapter(),
        ExecutionProvider.Kind.CLAUDE: ClaudeAdapter(),
    }
    try:
        return adapters[entry.kind]
    except KeyError as exc:
        raise ValueError("MODEL_PROVIDER_ADAPTER_UNAVAILABLE") from exc


def select_model_provider(identity: str) -> ExecutionProvider:
    """Select one enabled, active model provider by its governed identity."""
    try:
        entry = ExecutionProvider.objects.get(provider_id=identity)
    except ExecutionProvider.DoesNotExist as exc:
        raise ValueError("MODEL_PROVIDER_UNAVAILABLE") from exc
    if (
        not entry.enabled
        or entry.status != ExecutionProvider.Status.ACTIVE
        or entry.role != ExecutionProvider.Role.MODEL_API
        or "MODEL_INFERENCE" not in entry.capabilities
    ):
        raise ValueError("MODEL_PROVIDER_UNAVAILABLE")
    return entry


def structured_model_response(
    entry: ExecutionProvider, response: dict[str, object]
) -> dict[str, object]:
    """Decode one JSON-object response inside the provider-platform boundary."""
    text: object
    if entry.kind == ExecutionProvider.Kind.OPENAI:
        output = response.get("output")
        if not isinstance(output, list) or not output:
            raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID")
        message = output[0]
        if not isinstance(message, dict):
            raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID")
        content = message.get("content")
        if not isinstance(content, list) or not content:
            raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID")
        item = content[0]
        text = item.get("text") if isinstance(item, dict) else None
    elif entry.kind == ExecutionProvider.Kind.CLAUDE:
        content = response.get("content")
        if not isinstance(content, list) or not content:
            raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID")
        item = content[0]
        text = item.get("text") if isinstance(item, dict) else None
    else:
        raise ValueError("MODEL_PROVIDER_ADAPTER_UNAVAILABLE")
    if not isinstance(text, str):
        raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID") from exc
    if not isinstance(decoded, dict):
        raise ValueError("MODEL_PROVIDER_RESPONSE_INVALID")
    return decoded


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

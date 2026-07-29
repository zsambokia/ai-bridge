"""Redacted, bounded projections of Codex CLI JSONL provider events."""

from __future__ import annotations

import json
import re
from typing import Any

MAX_OUTPUT_CHARS = 4096
_SECRET_PATTERNS = (
    re.compile(r"(?i)(?:api[_-]?key|password|secret|token)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]+"),
    re.compile(r"(?i)authorization\s*[:=]\s*[^\r\n]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
)


def redact_text(value: str) -> str:
    """Remove credential-shaped text before it can enter a durable projection."""
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def bounded_text(value: object, limit: int = MAX_OUTPUT_CHARS) -> str:
    """Keep useful start/end context without retaining unbounded provider output."""
    text = redact_text(str(value))
    if len(text) <= limit:
        return text
    kept = max(1, (limit - 80) // 2)
    omitted = len(text) - (kept * 2)
    return f"{text[:kept]}\n... [truncated {omitted} characters] ...\n{text[-kept:]}"


def redact_value(value: object) -> object:
    if isinstance(value, str):
        return bounded_text(value)
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]" if _is_secret_key(str(key)) else redact_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    return value


def _redacted_event(event: dict[str, object]) -> dict[str, object]:
    redacted = redact_value(event)
    return redacted if isinstance(redacted, dict) else {}


def _is_secret_key(key: str) -> bool:
    return any(
        marker in key.lower()
        for marker in ("api_key", "password", "secret", "token", "authorization")
    )


def _text(mapping: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _item(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = payload.get("item")
    return candidate if isinstance(candidate, dict) else {}


def project_codex_event(
    payload: dict[str, Any], *, source_stream: str = "stdout"
) -> dict[str, object]:
    """Map Codex JSONL to the canonical event taxonomy, retaining real fields."""
    item = _item(payload)
    raw_type = _text(payload, "type", "event_type") or "unknown"
    item_type = _text(item, "type")
    command = _text(item, "command") or _text(payload, "command")
    message = _text(item, "text", "message", "content", "summary") or _text(
        payload, "message", "text"
    )
    stdout = _text(item, "stdout", "aggregated_output", "output") or _text(
        payload, "stdout"
    )
    stderr = _text(item, "stderr") or _text(payload, "stderr")
    file_path = _text(item, "path", "file_path") or _text(payload, "file_path")
    exit_code = item.get("exit_code", payload.get("exit_code"))
    event_type = "PROVIDER_MESSAGE"
    if raw_type in {"thread.started", "turn.started"}:
        event_type = "PROVIDER_STARTED"
    elif raw_type in {"turn.completed", "thread.completed"}:
        event_type = "PROVIDER_COMPLETED"
    elif raw_type in {"error", "turn.failed"}:
        event_type = "PROVIDER_ERROR"
    elif raw_type == "warning":
        event_type = "PROVIDER_WARNING"
    elif item_type == "reasoning":
        event_type = "PROVIDER_REASONING_SUMMARY"
    elif item_type in {"command_execution", "command"}:
        if raw_type == "item.started":
            event_type = (
                "TEST_STARTED" if _is_test_command(command) else "COMMAND_STARTED"
            )
        elif raw_type in {"item.updated", "command.output"}:
            event_type = "COMMAND_OUTPUT"
        else:
            event_type = (
                "TEST_RESULT" if _is_test_command(command) else "COMMAND_COMPLETED"
            )
    elif item_type in {"file_change", "file_changed"} or file_path:
        event_type = "FILE_CHANGED"
    if not message:
        message = (
            stdout or stderr or (command if command else f"Codex reported {raw_type}")
        )
    identifier = _text(item, "id", "item_id") or _text(payload, "item_id")
    provider_event_id = _text(payload, "id", "event_id")
    if (
        not provider_event_id
        and identifier
        and raw_type in {"item.started", "item.completed"}
    ):
        provider_event_id = f"{raw_type}:{identifier}"
    return _redacted_event(
        {
            "event_type": event_type,
            "provider": "codex-cli",
            "provider_event_type": raw_type,
            "provider_timestamp": _text(payload, "timestamp", "created_at"),
            "provider_event_id": provider_event_id,
            "item_identifier": identifier,
            "message": message,
            "command": command,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "file_path": file_path,
            "source_stream": source_stream,
            "raw_event": payload,
        }
    )


def project_provider_line(
    line: bytes | str, *, source_stream: str
) -> dict[str, object]:
    text = line.decode("utf-8", errors="replace") if isinstance(line, bytes) else line
    text = text.strip()
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        decoded = None
    if isinstance(decoded, dict):
        return project_codex_event(decoded, source_stream=source_stream)
    if decoded is not None:
        text = decoded if isinstance(decoded, str) else str(decoded)
    return _redacted_event(
        {
            "event_type": "PROVIDER_WARNING"
            if source_stream == "stderr"
            else "PROVIDER_MESSAGE",
            "provider": "codex-cli",
            "provider_event_type": "plain_text",
            "provider_timestamp": "",
            "provider_event_id": "",
            "item_identifier": "",
            "message": text or "Codex emitted an empty output line",
            "command": "",
            "exit_code": None,
            "stdout": text if source_stream == "stdout" else "",
            "stderr": text if source_stream == "stderr" else "",
            "file_path": "",
            "source_stream": source_stream,
            "raw_event": {"raw_text": text},
        }
    )


def _is_test_command(command: str) -> bool:
    lowered = command.lower()
    return any(
        token in lowered
        for token in ("pytest", "manage.py test", "ruff", "mypy", "validate_scopes")
    )

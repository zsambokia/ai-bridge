"""Safe, derived execution activity views shared by MCP and operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from django.conf import settings
from django.utils import timezone

from .models import ExecutionProgressEvent, ExecutionRun

_EVENTS = {
    "PREFLIGHT_COMPLETED": ("PREFLIGHT", "AI Bridge", "INFO", "Preflight completed"),
    "EXECUTOR_STARTED": ("EXECUTING", "Codex", "INFO", "Codex execution started"),
    "EXECUTION_ACTIVITY_STARTED": (
        "EXECUTING",
        "AI Bridge",
        "INFO",
        "Live activity monitoring started",
    ),
    "PROVIDER_OUTPUT": ("EXECUTING", "Codex", "INFO", "Codex activity received"),
    "PROVIDER_STARTED": ("EXECUTING", "Codex", "INFO", "Codex"),
    "PROVIDER_MESSAGE": ("EXECUTING", "Codex", "INFO", "Codex"),
    "PROVIDER_REASONING_SUMMARY": ("EXECUTING", "Codex", "INFO", "Codex reasoning"),
    "COMMAND_STARTED": ("EXECUTING", "Codex", "INFO", "Command started"),
    "COMMAND_OUTPUT": ("EXECUTING", "Codex", "INFO", "Command output"),
    "COMMAND_COMPLETED": ("EXECUTING", "Codex", "INFO", "Command completed"),
    "FILE_CHANGED": ("EXECUTING", "Codex", "INFO", "File changed"),
    "TEST_STARTED": ("VALIDATING", "Codex", "INFO", "Test started"),
    "TEST_RESULT": ("VALIDATING", "Codex", "INFO", "Test result"),
    "PROVIDER_WARNING": ("EXECUTING", "Codex", "WARNING", "Codex warning"),
    "PROVIDER_ERROR": ("EXECUTING", "Codex", "ERROR", "Codex error"),
    "PROVIDER_COMPLETED": ("EXECUTING", "Codex", "INFO", "Codex completed"),
    "PROVIDER_START_RETRYING": (
        "REPAIRING",
        "AI Bridge",
        "WARNING",
        "Provider start retrying",
    ),
    "ROOT_CAUSE_IDENTIFIED": (
        "REPAIRING",
        "AI Bridge",
        "WARNING",
        "Root cause identified",
    ),
    "REPAIR_APPLIED": ("REPAIRING", "Codex", "INFO", "Repair applied"),
    "GATE_RERUN_STARTED": ("VALIDATING", "AI Bridge", "INFO", "Gate rerun started"),
    "GATE_RERUN_FAILED": ("REPAIRING", "AI Bridge", "WARNING", "Gate rerun failed"),
    "GATE_RERUN_PASSED": ("VALIDATING", "AI Bridge", "INFO", "Gate rerun passed"),
    "REPAIR_VERIFIED": ("REPAIRING", "AI Bridge", "INFO", "Repair verified"),
    "PROVIDER_FAILURE": ("BLOCKED", "AI Bridge", "ERROR", "Provider unavailable"),
    "EXECUTION_COMPLETED": ("CLOSING", "AI Bridge", "INFO", "Execution completed"),
}

_STAGES = (
    ("contract", "Contract verified"),
    ("preflight", "Preflight"),
    ("provider", "Provider started"),
    ("execution", "Implementation"),
    ("validation", "Validation"),
    ("repair", "Repair"),
    ("documentation", "Documentation and evidence"),
    ("closure", "Closure"),
)


def heartbeat_projection(
    run: ExecutionRun, *, observed_at: datetime | None = None
) -> dict[str, Any]:
    """Derive a non-mutating heartbeat from persisted events and run timestamps."""
    observed_at = observed_at or timezone.now()
    latest = run.events.order_by("-sequence").first()
    last_activity_at = (
        latest.created_at if latest else (run.started_at or run.created_at)
    )
    age_seconds = max(0, int((observed_at - last_activity_at).total_seconds()))
    terminal = run.lifecycle in {
        ExecutionRun.Lifecycle.COMPLETED,
        ExecutionRun.Lifecycle.CANCELLED,
        ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION,
        ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
    }
    if terminal:
        classification = "TERMINAL"
    elif age_seconds <= settings.AI_BRIDGE_HEARTBEAT_ACTIVE_SECONDS:
        classification = "ACTIVE"
    elif age_seconds <= settings.AI_BRIDGE_HEARTBEAT_WAITING_SECONDS:
        classification = "QUIET"
    elif age_seconds <= settings.AI_BRIDGE_HEARTBEAT_STALLED_SECONDS:
        classification = "WAITING_FOR_PROVIDER"
    else:
        classification = "POSSIBLY_STALLED"
    return {
        "last_activity_at": last_activity_at.isoformat(),
        "activity_age_seconds": age_seconds,
        "heartbeat_status": classification,
        "heartbeat_observed_at": observed_at.isoformat(),
        "latest_event_type": latest.event_type if latest else None,
        "derived_only": True,
    }


def event_view(event: ExecutionProgressEvent) -> dict[str, Any]:
    """Render one persisted event without inventing activity or actors."""
    phase, actor, severity, title = _EVENTS.get(
        event.event_type,
        ("EXECUTING", "AI Bridge", "INFO", event.event_type.replace("_", " ").title()),
    )
    details = event.details if isinstance(event.details, dict) else {}
    message = _activity_message(event.event_type, details, title)
    return {
        "sequence": event.sequence,
        "type": event.event_type,
        "phase": phase,
        "actor": actor,
        "severity": severity,
        "title": title,
        "message": message,
        "details": details,
        "created_at": event.created_at.isoformat(),
    }


def console_line(event: ExecutionProgressEvent) -> str:
    """Produce a brief, human-readable DEV activity line from persisted state."""
    view = event_view(event)
    return f"[{view['sequence']}] {view['title']}: {view['message']}"


def _activity_message(event_type: str, details: dict[str, Any], fallback: str) -> str:
    message = str(details.get("message") or "")
    command = str(details.get("command") or "")
    if event_type == "COMMAND_STARTED" and command:
        return command[:500]
    if event_type == "COMMAND_COMPLETED" and command:
        exit_code = details.get("exit_code")
        prefix = (
            "successfully: "
            if exit_code in (0, "0", None)
            else f"with exit code {exit_code}: "
        )
        return (prefix + command)[:500]
    if event_type == "FILE_CHANGED" and details.get("file_path"):
        return str(details["file_path"])[:500]
    return (message or str(details.get("reason") or fallback))[:500]


def provider_output_view(event: ExecutionProgressEvent) -> dict[str, Any]:
    details = event.details if isinstance(event.details, dict) else {}
    return {
        "sequence": event.sequence,
        "type": event.event_type,
        "timestamp": details.get("provider_timestamp") or event.created_at.isoformat(),
        "provider": details.get("provider", "codex-cli"),
        "item_identifier": details.get("item_identifier", ""),
        "message": details.get("message", ""),
        "command": details.get("command", ""),
        "exit_code": details.get("exit_code"),
        "stdout": details.get("stdout", ""),
        "stderr": details.get("stderr", ""),
        "file_path": details.get("file_path", ""),
        "created_at": event.created_at.isoformat(),
    }


def raw_event_view(event: ExecutionProgressEvent) -> dict[str, Any]:
    details = event.details if isinstance(event.details, dict) else {}
    return {
        "sequence": event.sequence,
        "type": event.event_type,
        "provider_event_type": details.get("provider_event_type", ""),
        "provider_event_id": event.provider_event_id,
        "timestamp": details.get("provider_timestamp") or event.created_at.isoformat(),
        "raw_event": details.get("raw_event", details),
        "created_at": event.created_at.isoformat(),
    }


def events_for_view(
    run: ExecutionRun,
    view: str = "ACTIVITY",
    *,
    after_sequence: int = 0,
    limit: int = 100,
) -> list[dict[str, Any]]:
    events = run.events.filter(sequence__gt=after_sequence).order_by("sequence")[:limit]
    if view == "PROVIDER_OUTPUT":
        return [provider_output_view(event) for event in events]
    if view == "RAW_EVENTS":
        return [raw_event_view(event) for event in events]
    return [event_view(event) for event in events]


def activity_summary(run: ExecutionRun) -> dict[str, Any]:
    """Compute a checklist solely from canonical run state and persisted events."""
    events = list(run.events.order_by("sequence"))
    types = {event.event_type for event in events}
    lifecycle = run.lifecycle
    blocked = lifecycle in {
        ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION,
        ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
    }
    completed = lifecycle == ExecutionRun.Lifecycle.COMPLETED
    done = {
        "contract": bool(run.contract_id),
        "preflight": "PREFLIGHT_COMPLETED" in types,
        "provider": bool({"EXECUTOR_STARTED", "PROVIDER_STARTED"} & types),
        "execution": completed,
        "validation": completed,
        "repair": "REPAIR_VERIFIED" in types,
        "documentation": completed,
        "closure": completed,
    }
    active = {
        "STARTING": "provider",
        "EXECUTING": "execution",
        "VALIDATING": "validation",
        "REPAIRING": "repair",
        "DOCUMENTING": "documentation",
        "CLOSING": "closure",
    }.get(run.current_phase)
    checklist = []
    for key, label in _STAGES:
        status = "COMPLETED" if done[key] else "PENDING"
        if blocked and key == active:
            status = "BLOCKED"
        elif lifecycle == ExecutionRun.Lifecycle.REPAIRING and key == "repair":
            status = "FAILED_REPAIRING"
        elif key == active:
            status = "IN_PROGRESS"
        checklist.append({"id": key, "label": label, "status": status})
    return {
        "execution_token": str(run.token),
        "status": lifecycle,
        "phase": run.current_phase,
        "current_blocker": run.current_blocker,
        "checklist": checklist,
        "current_activity": event_view(events[-1]) if events else None,
        "latest_events": [event_view(event) for event in events[-100:]],
        "events": [event_view(event) for event in events[:100]],
        "provider_output": [provider_output_view(event) for event in events[:100]],
        "raw_events": [raw_event_view(event) for event in events[:100]],
        "heartbeat": heartbeat_projection(run),
    }

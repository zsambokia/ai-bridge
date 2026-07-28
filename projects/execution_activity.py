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
    "FACTORY_DEVELOPMENT_APPROVED": (
        "PREFLIGHT",
        "Product Owner",
        "INFO",
        "Factory Development Mode approved",
    ),
    "PROVIDER_FINISHED": ("VALIDATING", "Codex", "INFO", "Codex provider finished"),
    "VALIDATION_CONTINUATION_READY": (
        "VALIDATING",
        "AI Bridge",
        "INFO",
        "Validation continuation ready",
    ),
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
    "WATCHDOG_STALE_BLOCKED": (
        "BLOCKED",
        "AI Bridge",
        "ERROR",
        "Watchdog blocked a stale execution",
    ),
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

_ICONS = {"INFO": "info", "WARNING": "warning", "ERROR": "error"}


def terminal_outcome(run: ExecutionRun) -> str | None:
    """Return the one Product Owner terminal category for a durable run."""
    if run.lifecycle == ExecutionRun.Lifecycle.COMPLETED:
        return "PASS"
    if run.lifecycle in {
        ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION,
        ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
    }:
        return "BLOCKED"
    if run.lifecycle == ExecutionRun.Lifecycle.FAILED_GOVERNANCE:
        return "FAIL"
    if run.lifecycle == ExecutionRun.Lifecycle.CANCELLED:
        return "CANCELLED"
    return None


def _next_expected_step(run: ExecutionRun) -> str:
    if terminal_outcome(run):
        return "No further execution action is expected."
    return {
        "PREFLIGHT": "Complete preflight and start the approved provider.",
        "STARTING": "Record provider startup or an actionable blocker.",
        "EXECUTING": "Wait for provider completion, then reconcile validation.",
        "VALIDATING": "Run validation, evidence, and closure checks.",
        "REPAIRING": "Repair the diagnosed failure and rerun the failed gate.",
        "DOCUMENTING": "Synchronize documentation and execution evidence.",
        "CLOSING": "Record the deterministic terminal result.",
    }.get(run.current_phase, "Reconcile the canonical execution lifecycle.")


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
        ExecutionRun.Lifecycle.FAILED_GOVERNANCE,
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
    message = str(details.get("message", details.get("reason", title)))[:500]
    return {
        "sequence": event.sequence,
        "type": event.event_type,
        "phase": phase,
        "actor": actor,
        "severity": severity,
        "icon": _ICONS.get(severity, "info"),
        "title": title,
        "message": message,
        "details": details,
        "created_at": event.created_at.isoformat(),
        "source_event": {"type": event.event_type, "sequence": event.sequence},
    }


def console_line(event: ExecutionProgressEvent) -> str:
    """Produce a brief, human-readable DEV activity line from persisted state."""
    view = event_view(event)
    label = {"INFO": "INFO", "WARNING": "WARNING", "ERROR": "ERROR"}.get(
        view["severity"], "EVENT"
    )
    return f"[{label}] [{view['sequence']}] {view['title']}: {view['message']}"


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
    outcome = terminal_outcome(run)
    done = {
        "contract": bool(run.contract_id)
        or run.execution_profile == ExecutionRun.Profile.FACTORY_DEVELOPMENT,
        "preflight": "PREFLIGHT_COMPLETED" in types,
        "provider": "EXECUTOR_STARTED" in types,
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
        "terminal_outcome": outcome,
        "current_blocker": run.current_blocker,
        "checklist": checklist,
        "current_activity": event_view(events[-1]) if events else None,
        "latest_events": [event_view(event) for event in events[-100:]],
        "events": [event_view(event) for event in events[:100]],
        "heartbeat": heartbeat_projection(run),
        "product_owner_progress": {
            "mode": run.execution_profile,
            "approval_reference": run.authority_reference or None,
            "summary": (
                f"{run.current_phase.replace('_', ' ').title()} — "
                f"{lifecycle.replace('_', ' ').title()}"
            ),
            "provider_status": (
                "FINISHED" if "PROVIDER_FINISHED" in types else lifecycle
            ),
            "blocker": run.current_blocker or None,
            "next_expected_step": _next_expected_step(run),
            "confidence": ("HIGH" if events else "LOW"),
            "activity_stream": [event_view(event) for event in events[-100:]],
            "derived_from": "canonical execution run and persisted progress events",
        },
    }

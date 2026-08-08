"""Read-only Coding Mode projection over canonical execution state.

The Factory Chat must not grow a second execution lifecycle or a browser-side
provider path.  This module translates the existing safe lifecycle and activity
projections into concise Hungarian Product Owner information.
"""

from __future__ import annotations

from typing import Any, cast

from .execution import lifecycle_status_projection
from .execution_activity import activity_summary
from .models import ExecutionRun

_CLASSIFICATIONS: dict[str, tuple[str, str]] = {
    ExecutionRun.Lifecycle.REQUESTED: (
        "Végrehajtásra vár",
        "A kanonikus végrehajtási kérés rögzítve van; a tartós worker átveheti.",
    ),
    ExecutionRun.Lifecycle.STARTING: (
        "Indítás és előkészítés",
        "A Bridge ellenőrzi és előkészíti a kanonikus végrehajtási környezetet.",
    ),
    ExecutionRun.Lifecycle.RUNNING: (
        "Megvalósítás folyamatban",
        "A jóváhagyott munka végrehajtása folyamatban van.",
    ),
    ExecutionRun.Lifecycle.REPAIRING: (
        "Automatikus műszaki javítás",
        "Műszaki hiba javítása és az érintett ellenőrzés újrafuttatása "
        "folyamatban van.",
    ),
    ExecutionRun.Lifecycle.VALIDATING: (
        "Ellenőrzés folyamatban",
        "A Bridge a kanonikus ellenőrzéseket és bizonyítékokat vizsgálja.",
    ),
    ExecutionRun.Lifecycle.DOCUMENTING: (
        "Dokumentálás folyamatban",
        "A végrehajtás bizonyítékainak és dokumentációjának rögzítése folyamatban van.",
    ),
    ExecutionRun.Lifecycle.CLOSING: (
        "Lezárás folyamatban",
        "A végrehajtás lezárási feltételeinek ellenőrzése folyamatban van.",
    ),
    ExecutionRun.Lifecycle.COMPLETED: (
        "Ellenőrzött lezárás",
        "A kanonikus végrehajtás lezárt állapotban van.",
    ),
    ExecutionRun.Lifecycle.CANCELLING: (
        "Leállítás folyamatban",
        "A korábban megerősített leállítás végrehajtása folyamatban van.",
    ),
    ExecutionRun.Lifecycle.CANCELLED: (
        "Leállítva",
        "A kanonikus végrehajtás leállított, terminális állapotban van.",
    ),
    ExecutionRun.Lifecycle.FAILED_GOVERNANCE: (
        "Governance megállítás",
        (
            "A végrehajtás governance okból megállt; a kanonikus rekord "
            "részletezi az okot."
        ),
    ),
    ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT: (
        "Külső bemenet hiányzik",
        "A végrehajtás külső, biztonságosan nem pótolható bemenetre vár.",
    ),
}


def _action(run: ExecutionRun) -> dict[str, object]:
    if run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION:
        blocker = run.current_blocker if isinstance(run.current_blocker, dict) else {}
        question = (
            blocker.get("question")
            or blocker.get("reason")
            or "A kanonikus blokkoló részletei szükségesek."
        )
        return {
            "required": True,
            "title": "Termék Tulajdonos döntése szükséges",
            "detail": str(question),
        }
    if run.lifecycle == ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT:
        return {
            "required": False,
            "title": "Nincs böngészős tulajdonosi teendő",
            "detail": (
                "A Bridge külső bemenetre vár; ez a képernyő nem helyettesíti azt."
            ),
        }
    return {
        "required": False,
        "title": "Nincs teendő",
        "detail": (
            "A kanonikus végrehajtás állapota automatikusan frissül. "
            "A böngésző nem indít szolgáltatót."
        ),
    }


def _progress(checklist: list[dict[str, Any]]) -> dict[str, object]:
    total = len(checklist)
    completed = sum(item.get("status") == "COMPLETED" for item in checklist)
    return {
        "completed": completed,
        "total": total,
        "percent": int((completed / total) * 100) if total else 0,
    }


def _epic_progress(run: ExecutionRun, epic_reference: str) -> dict[str, object]:
    """Aggregate only durable executions explicitly bound to this Epic."""
    runs = []
    candidates = ExecutionRun.objects.filter(contract__project=run.contract.project)
    for candidate in candidates:
        payload = candidate.contract.payload
        scope = payload.get("scope", {}) if isinstance(payload, dict) else {}
        if scope.get("epic_reference") == epic_reference:
            runs.append(candidate)
    completed = sum(
        candidate.lifecycle == ExecutionRun.Lifecycle.COMPLETED for candidate in runs
    )
    total = len(runs)
    return {
        "reference": epic_reference,
        "available": bool(total),
        "completed": completed,
        "total": total,
        "percent": int((completed / total) * 100) if total else 0,
    }


def coding_projection(run: ExecutionRun | None) -> dict[str, object]:
    """Return a UI-only view calculated from the two canonical projections."""
    if run is None:
        return {
            "available": False,
            "title": "Nincs kanonikus végrehajtás",
            "detail": (
                "Kódolási előrehaladás akkor jelenik meg, amikor a projekthez "
                "ExecutionRun tartozik."
            ),
        }

    lifecycle = cast(dict[str, Any], lifecycle_status_projection(run))
    activity = activity_summary(run)
    title, detail = _CLASSIFICATIONS.get(
        run.lifecycle,
        (
            "Termék Tulajdonos döntése szükséges",
            "A kanonikus futás üzleti döntésre vár.",
        ),
    )
    checklist = cast(list[dict[str, Any]], activity["checklist"])
    payload = run.contract.payload
    scope = payload.get("scope", {}) if isinstance(payload, dict) else {}
    sprint_reference = scope.get("identifier") or run.contract.approved_sprint_path
    return {
        "available": True,
        "classification": {"title": title, "detail": detail},
        "action": _action(run),
        "sprint": {"reference": sprint_reference, **_progress(checklist)},
        "epic": _epic_progress(run, scope["epic_reference"])
        if scope.get("epic_reference")
        else {"reference": "", "available": False},
        "checklist": checklist,
        "events": cast(list[dict[str, Any]], activity["latest_events"])[:8],
        "verification": {
            "evidence_root": lifecycle["evidence"]["evidence_root"],
            "final_commit_sha": lifecycle["evidence"]["final_commit_sha"],
            "terminal_state": lifecycle["evidence"]["terminal_state"],
            "instruction": (
                "Az ellenőrzés a kanonikus Release Gate-ek és az evidence root "
                "alapján történik; a felület csak ezt mutatja."
            ),
        },
        "diagnostics": {
            "lifecycle": lifecycle["status"],
            "phase": lifecycle["phase"],
            "heartbeat": lifecycle["heartbeat"],
            "queue_status": lifecycle["queue"]["status"],
            "workspace_status": lifecycle["workspace"]["status"],
        },
    }

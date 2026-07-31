"""Verify a deployed runtime using its public health surface and local supervisors."""

from __future__ import annotations

import json
import subprocess
import sys
from argparse import ArgumentParser
from typing import Any
from urllib.request import urlopen

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


def _status(callable_: Any) -> dict[str, str]:
    try:
        callable_()
    except Exception as exc:  # pragma: no cover - command integration boundary
        return {"status": "FAIL", "detail": str(exc)}
    return {"status": "PASS"}


class Command(BaseCommand):
    """Produce a deterministic runtime verification receipt without claiming deploy."""

    help = "Verify SHA, migrations, dependencies, worker and scheduler for one runtime."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--url", required=True)
        parser.add_argument("--expected-sha", required=True)

    def handle(self, *args: object, **options: Any) -> None:
        expected_sha = str(options["expected_sha"]).lower()
        if len(expected_sha) != 40 or any(
            char not in "0123456789abcdef" for char in expected_sha
        ):
            raise CommandError("--expected-sha must be a 40-character lowercase SHA.")

        url = str(options["url"]).rstrip("/") + "/health/"
        health: dict[str, Any] = {}

        def check_health() -> None:
            nonlocal health
            with urlopen(url, timeout=10) as response:  # noqa: S310 - caller-owned target
                health = json.loads(response.read().decode("utf-8"))
            if health.get("status") != "ok":
                raise RuntimeError("HEALTH_STATUS_NOT_OK")
            if health.get("build_sha", "").lower() != expected_sha:
                raise RuntimeError("RUNTIME_BUILD_SHA_MISMATCH")

        results = {
            "health": _status(check_health),
            "migrations": _status(lambda: call_command("migrate", plan=True)),
            "dependencies": _status(
                lambda: subprocess.run(
                    [sys.executable, "-m", "pip", "check"],
                    check=True,
                    capture_output=True,
                )
            ),
            "worker": _status(
                lambda: call_command(
                    "run_execution_worker", once=True, worker_id="runtime-smoke"
                )
            ),
            "scheduler": _status(
                lambda: call_command("run_execution_scheduler", once=True)
            ),
        }
        passed = all(result["status"] == "PASS" for result in results.values())
        receipt = {
            "status": "PASS" if passed else "FAIL",
            "expected_sha": expected_sha,
            "health": health,
            "checks": results,
        }
        self.stdout.write(json.dumps(receipt, sort_keys=True))
        if not passed:
            raise CommandError("RUNTIME_DEPLOYMENT_VERIFICATION_FAILED")

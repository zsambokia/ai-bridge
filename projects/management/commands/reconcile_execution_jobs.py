"""Run the durable execution reconciliation controller once or continuously."""

from __future__ import annotations

from argparse import ArgumentParser
from time import sleep
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from projects.execution import provider
from projects.execution_recovery import reconcile_execution_jobs


class Command(BaseCommand):
    help = "Reconcile stale execution leases and durable provider attempts."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--once", action="store_true")
        parser.add_argument("--poll-seconds", type=float, default=10.0)

    def handle(self, *args: object, **options: Any) -> None:
        poll_seconds = float(options["poll_seconds"])
        if poll_seconds <= 0:
            raise CommandError("--poll-seconds must be positive.")
        while True:
            decisions = reconcile_execution_jobs(
                provider_status=lambda name, execution_id: provider(name).status(
                    execution_id
                )
            )
            self.stdout.write(f"Reconciled {len(decisions)} execution job(s).")
            if options["once"]:
                return
            sleep(poll_seconds)

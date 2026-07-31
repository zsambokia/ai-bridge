"""Run one canonical supervision tick for the managed execution runtime."""

from __future__ import annotations

from argparse import ArgumentParser
from time import sleep
from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Supervise recovery and workspace retention without duplicating their logic."""

    help = "Run execution recovery and workspace cleanup once or continuously."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--once", action="store_true")
        parser.add_argument("--poll-seconds", type=float, default=10.0)

    def handle(self, *args: object, **options: Any) -> None:
        poll_seconds = float(options["poll_seconds"])
        if poll_seconds <= 0:
            raise CommandError("--poll-seconds must be positive.")
        while True:
            call_command("reconcile_execution_jobs", once=True)
            call_command("reconcile_execution_workspaces")
            self.stdout.write(self.style.SUCCESS("Execution scheduler tick completed."))
            if options["once"]:
                return
            sleep(poll_seconds)

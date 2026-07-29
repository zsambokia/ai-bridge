"""Independently claim and dispatch durable execution jobs."""

from __future__ import annotations

import socket
from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from projects.execution import claim_next_job, execute_claimed_job, heartbeat_job


class Command(BaseCommand):
    help = "Claim durable execution jobs and start their configured provider."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--once", action="store_true")
        parser.add_argument("--worker-id", default=f"worker:{socket.gethostname()}")
        parser.add_argument("--lease-seconds", type=int, default=120)
        parser.add_argument("--poll-seconds", type=float, default=2.0)

    def handle(self, *args: object, **options: Any) -> None:
        worker_id = str(options["worker_id"])
        lease_seconds = int(options["lease_seconds"])
        poll_seconds = float(options["poll_seconds"])
        once = bool(options["once"])
        if lease_seconds <= 0 or poll_seconds <= 0:
            raise CommandError("--lease-seconds and --poll-seconds must be positive.")

        while True:
            try:
                job = claim_next_job(worker_id, lease_seconds)
            except ValueError as exc:
                raise CommandError(str(exc)) from exc
            if job is None:
                if once:
                    self.stdout.write("No queued execution job.")
                    return
                sleep(poll_seconds)
                continue
            try:
                heartbeat_job(job, worker_id, lease_seconds)
                run = execute_claimed_job(job, worker_id, Path(settings.BASE_DIR))
            except ValueError as exc:
                raise CommandError(str(exc)) from exc
            self.stdout.write(self.style.SUCCESS(f"Started execution {run.token}."))
            if once:
                return

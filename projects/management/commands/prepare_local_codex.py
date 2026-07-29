"""Prepare a governed local Codex handoff without starting a provider."""

from __future__ import annotations

import json
import socket
from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from projects.local_codex import prepare_local_codex


class Command(BaseCommand):
    help = "Lease an existing, approved execution for a local Codex worker."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--execution-token", required=True)
        parser.add_argument(
            "--worker-id", default=f"local-codex:{socket.gethostname()}"
        )
        parser.add_argument("--lease-seconds", type=int, default=120)

    def handle(self, *args: object, **options: Any) -> None:
        try:
            job = prepare_local_codex(
                execution_token=str(options["execution_token"]),
                worker_id=str(options["worker_id"]),
                lease_seconds=int(options["lease_seconds"]),
                platform_root=settings.BASE_DIR,
            )
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            json.dumps(
                {
                    "job_token": str(job.token),
                    "execution_token": str(job.run.token),
                    "status": job.status,
                }
            )
        )

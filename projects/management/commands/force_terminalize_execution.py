"""Product Owner-authorized local break-glass terminalization command."""

from __future__ import annotations

import json
from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError

from projects.force_terminalization import (
    ForceTerminalizationRefused,
    force_terminalize_execution,
)


class Command(BaseCommand):
    help = "Safely terminalize one verified stuck execution without provider recovery."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("execution_token")
        parser.add_argument("--reason", required=True)
        parser.add_argument("--operator", required=True)
        parser.add_argument("--preserve-workspace", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--idempotency-key")

    def handle(self, *args: object, **options: object) -> None:
        try:
            result = force_terminalize_execution(
                str(options["execution_token"]),
                reason=str(options["reason"]),
                operator=str(options["operator"]),
                preserve_workspace=bool(options["preserve_workspace"]),
                dry_run=bool(options["dry_run"]),
                idempotency_key=(
                    str(options["idempotency_key"])
                    if options.get("idempotency_key")
                    else None
                ),
            )
        except ForceTerminalizationRefused as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(json.dumps(result.as_dict(), sort_keys=True))

"""Bootstrap the first canonical Registry record and Project Context."""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError, CommandParser

from projects.services import bootstrap_project


class Command(BaseCommand):
    """Run the constrained BOOTSTRAP operation for one repository."""

    help = "Register a Project Definition and create its first Project Context."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--definition", default=".bridge/project.yaml")
        parser.add_argument("--sprint-path", required=True)
        parser.add_argument("--repository-root", default=".")
        parser.add_argument("--contract-mode", default="BOOTSTRAP")

    def handle(self, *args: object, **options: object) -> str:
        repository_root = Path(str(options["repository_root"])).resolve()
        result = bootstrap_project(
            repository_root / str(options["definition"]),
            str(options["sprint_path"]),
            repository_root,
            str(options["contract_mode"]),
        )
        self.stdout.write(result.as_json())
        if not result.success:
            raise CommandError("bootstrap_project failed")
        return ""

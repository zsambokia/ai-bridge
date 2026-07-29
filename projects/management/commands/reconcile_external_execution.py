"""Reconcile evidence-backed Factory or external execution without a provider run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from projects.lifecycle_reconciliation import reconcile_external_execution
from projects.models import Project


class Command(BaseCommand):
    help = "Verify evidence and reconcile completed external governed execution."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument("--project-id", required=True)
        parser.add_argument("--scope", required=True)
        parser.add_argument("--final-commit", required=True)
        parser.add_argument("--evidence-manifest", required=True)
        parser.add_argument("--engineering-audit", required=True)
        parser.add_argument("--acceptance-evidence", required=True)
        parser.add_argument("--acceptance-reference", required=True)
        parser.add_argument("--source-kind", default="FACTORY_DEVELOPMENT")
        parser.add_argument("--reconciled-by", default="factory-development-mode")
        parser.add_argument(
            "--repository-root",
            help=(
                "Optional clean worktree for verification in the registered repository."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            manifest = json.loads(options["evidence_manifest"])
            project = Project.objects.get(project_id=options["project_id"])
            result, replay = reconcile_external_execution(
                project=project,
                scope_identifier=options["scope"],
                final_commit_sha=options["final_commit"],
                evidence_manifest=manifest,
                engineering_audit_path=options["engineering_audit"],
                acceptance_evidence_path=options["acceptance_evidence"],
                acceptance_reference=options["acceptance_reference"],
                source_kind=options["source_kind"],
                reconciled_by=options["reconciled_by"],
                repository_root=(
                    Path(options["repository_root"])
                    if options["repository_root"]
                    else None
                ),
            )
        except (ValueError, Project.DoesNotExist, json.JSONDecodeError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            json.dumps(
                {
                    "status": "PASS_ACCEPTED",
                    "scope": result.scope.identifier,
                    "final_commit_sha": result.final_commit_sha,
                    "idempotent_replay": replay,
                },
                sort_keys=True,
            )
        )

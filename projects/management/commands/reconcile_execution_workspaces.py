"""Safely retain and clean expired isolated execution workspaces."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from projects.workspace import WorkspaceManager


class Command(BaseCommand):
    help = "Reconcile and safely clean expired execution workspaces."

    def handle(self, *args: object, **options: object) -> None:
        cleaned = WorkspaceManager().reconcile_cleanup()
        self.stdout.write(
            self.style.SUCCESS(f"Cleaned {len(cleaned)} execution workspace(s).")
        )

"""Reconcile provider processes that have finished outside an MCP request."""

from django.core.management.base import BaseCommand

from projects.execution import watchdog_recover_runs


class Command(BaseCommand):
    help = "Reconcile finished providers and close stale active execution runs."

    def handle(self, *args: object, **options: object) -> None:
        reconciled = watchdog_recover_runs()
        self.stdout.write(
            self.style.SUCCESS(f"Reconciled {reconciled} provider run(s).")
        )

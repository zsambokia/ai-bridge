"""Tests for the canonical runtime verification and scheduler entry points."""

from __future__ import annotations

from unittest.mock import call, patch

from django.core.management import call_command


def test_scheduler_runs_existing_recovery_and_cleanup_services_once() -> None:
    """The scheduler composes, rather than forks, canonical supervision logic."""
    command_path = "projects.management.commands.run_execution_scheduler.call_command"
    with patch(command_path) as run:
        call_command("run_execution_scheduler", once=True)
    assert run.call_args_list == [
        call("reconcile_execution_jobs", once=True),
        call("reconcile_execution_workspaces"),
    ]

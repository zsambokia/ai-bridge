"""Independently claim and dispatch durable execution jobs."""

from __future__ import annotations

import socket
from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from projects.execution import (
    claim_next_job,
    defer_claimed_job_for_active_branch,
    execute_claimed_job,
    fail_claimed_job,
    heartbeat_job,
    is_non_retryable_execution_failure,
    reject_claimed_job,
    requeue_provider_start_failure,
)


class Command(BaseCommand):
    help = "Claim durable execution jobs and start their configured provider."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--once", action="store_true")
        parser.add_argument("--worker-id", default=f"worker:{socket.gethostname()}")
        parser.add_argument("--lease-seconds", type=int, default=120)
        parser.add_argument("--poll-seconds", type=float, default=2.0)
        parser.add_argument(
            "--max-jobs",
            type=int,
            default=0,
            help="Exit after this many claimed jobs; 0 keeps the worker supervised.",
        )

    def handle(self, *args: object, **options: Any) -> None:
        worker_id = str(options["worker_id"])
        lease_seconds = int(options["lease_seconds"])
        poll_seconds = float(options["poll_seconds"])
        once = bool(options["once"])
        max_jobs = int(options["max_jobs"])
        if lease_seconds <= 0 or poll_seconds <= 0 or max_jobs < 0:
            raise CommandError(
                "--lease-seconds and --poll-seconds must be positive; "
                "--max-jobs cannot be negative."
            )
        processed_jobs = 0

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
                if str(exc) in {"WORKER_LEASE_NOT_OWNED", "WORKER_FENCING_TOKEN_STALE"}:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Lease superseded for {job.token}; continuing worker."
                        )
                    )
                    processed_jobs += 1
                    if once or (max_jobs and processed_jobs >= max_jobs):
                        return
                    continue
                if is_non_retryable_execution_failure(exc):
                    rejected = reject_claimed_job(job, worker_id, exc)
                    self.stdout.write(
                        self.style.WARNING(
                            "Rejected execution "
                            f"{rejected.run.token}: {exc}. Continuing worker."
                        )
                    )
                    processed_jobs += 1
                    if once or (max_jobs and processed_jobs >= max_jobs):
                        return
                    continue
                if str(exc) == "WORKSPACE_PROVISIONING_FAILED":
                    failed = fail_claimed_job(job, worker_id, str(exc))
                    self.stdout.write(
                        self.style.WARNING(
                            "Execution "
                            f"{failed.run.token} workspace failed; continuing worker."
                        )
                    )
                    processed_jobs += 1
                    if once or (max_jobs and processed_jobs >= max_jobs):
                        return
                    continue
                if str(exc) == "EXECUTOR_START_FAILED":
                    recovered = requeue_provider_start_failure(job, worker_id)
                    message = f"Execution {recovered.run.token} provider start " + (
                        "retry budget exhausted; continuing worker."
                        if recovered.status == "FAILED"
                        else "queued for bounded recovery; continuing worker."
                    )
                    self.stdout.write(self.style.WARNING(message))
                    processed_jobs += 1
                    if once or (max_jobs and processed_jobs >= max_jobs):
                        return
                    continue
                if str(exc) == "CONFLICTING_ACTIVE_EXECUTION":
                    deferred = defer_claimed_job_for_active_branch(job, worker_id)
                    self.stdout.write(
                        self.style.WARNING(
                            "Execution "
                            f"{deferred.run.token} deferred until the active branch "
                            "execution releases its authority; continuing worker."
                        )
                    )
                    processed_jobs += 1
                    if once or (max_jobs and processed_jobs >= max_jobs):
                        return
                    continue
                raise CommandError(str(exc)) from exc
            self.stdout.write(self.style.SUCCESS(f"Started execution {run.token}."))
            processed_jobs += 1
            if once or (max_jobs and processed_jobs >= max_jobs):
                return

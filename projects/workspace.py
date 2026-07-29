"""Canonical isolated execution workspace lifecycle and safe reconciliation."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import ExecutionRun, ExecutionWorkspace
from .runtime_bootstrap import BootstrapProfileError, resolve_profile


class WorkspaceError(ValueError):
    """A provisioning failure that must prevent provider startup."""


def _run(
    command: list[str],
    cwd: Path | None = None,
    environment: dict[str, str] | None = None,
) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env={**os.environ, **(environment or {})},
        check=False,
        capture_output=True,
        text=True,
        timeout=settings.BRIDGE_WORKSPACE_PROVISION_TIMEOUT,
        shell=False,
    )  # noqa: S603
    if completed.returncode:
        raise WorkspaceError("WORKSPACE_COMMAND_FAILED")
    return completed.stdout.strip()


def _under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _settings() -> tuple[Path, Path]:
    root = Path(settings.BRIDGE_WORKSPACE_ROOT).resolve()
    cache = Path(settings.BRIDGE_REPOSITORY_CACHE_ROOT).resolve()
    if (
        root == cache
        or root == Path(settings.BASE_DIR).resolve()
        or cache == Path(settings.BASE_DIR).resolve()
    ):
        raise WorkspaceError("WORKSPACE_ROOT_UNSAFE")
    if settings.BRIDGE_WORKSPACE_DATABASE_MODE != "sqlite":
        raise WorkspaceError("WORKSPACE_DATABASE_MODE_UNSUPPORTED")
    if (
        settings.BRIDGE_WORKSPACE_MAX_DISK_USAGE <= 0
        or settings.BRIDGE_WORKSPACE_PROVISION_TIMEOUT <= 0
    ):
        raise WorkspaceError("WORKSPACE_SETTINGS_INVALID")
    return root, cache


def _retention(run: ExecutionRun) -> datetime | None:
    if run.current_phase in {"RECOVERING", "RECOVERY_REVIEW_REQUIRED"}:
        return None
    if run.lifecycle == ExecutionRun.Lifecycle.COMPLETED:
        return timezone.now() + timedelta(hours=3)
    if run.lifecycle in {
        ExecutionRun.Lifecycle.BLOCKED_BUSINESS_DECISION,
        ExecutionRun.Lifecycle.BLOCKED_EXTERNAL_INPUT,
    }:
        return None
    return timezone.now() + timedelta(hours=settings.BRIDGE_WORKSPACE_RETENTION_HOURS)


def _fingerprint(repository: Path) -> str:
    digest = hashlib.sha256()
    for name in ("pyproject.toml", "requirements.txt", "uv.lock", "poetry.lock"):
        candidate = repository / name
        if candidate.is_file():
            digest.update(name.encode())
            digest.update(candidate.read_bytes())
    return digest.hexdigest()


class WorkspaceManager:
    """The sole idempotent provisioning and cleanup path for execution work."""

    def provision(self, run: ExecutionRun) -> ExecutionWorkspace:
        root, cache_root = _settings()
        try:
            profile = resolve_profile(run)
        except BootstrapProfileError as exc:
            raise WorkspaceError(str(exc)) from exc
        with transaction.atomic():
            workspace, _ = ExecutionWorkspace.objects.select_for_update().get_or_create(
                run=run
            )
            if workspace.status in {
                ExecutionWorkspace.Status.READY,
                ExecutionWorkspace.Status.IN_USE,
                ExecutionWorkspace.Status.RETAINED,
            }:
                if self.verify(workspace):
                    setattr(workspace, "_was_reused", True)
                    if workspace.status == ExecutionWorkspace.Status.RETAINED:
                        workspace.status = ExecutionWorkspace.Status.READY
                        workspace.save(update_fields=["status", "updated_at"])
                    return workspace
                workspace.status = ExecutionWorkspace.Status.FAILED
                workspace.failure_code = "WORKSPACE_VERIFICATION_FAILED"
                workspace.save(update_fields=["status", "failure_code", "updated_at"])
                raise WorkspaceError("WORKSPACE_VERIFICATION_FAILED")
            if workspace.status == ExecutionWorkspace.Status.CLEANED:
                raise WorkspaceError("WORKSPACE_ALREADY_CLEANED")
            workspace.status = ExecutionWorkspace.Status.PROVISIONING
            workspace.failure_code = ""
            workspace.failure_details = {}
            workspace.save(
                update_fields=[
                    "status",
                    "failure_code",
                    "failure_details",
                    "updated_at",
                ]
            )
        try:
            root.mkdir(parents=True, exist_ok=True)
            cache_root.mkdir(parents=True, exist_ok=True)
            workspace_root = root / str(run.token)
            repo_path = workspace_root / "repository"
            if not _under(workspace_root, root) or workspace_root == root:
                raise WorkspaceError("WORKSPACE_PATH_UNSAFE")
            repository_url = _run(
                ["git", "-C", str(settings.BASE_DIR), "remote", "get-url", "origin"]
            )
            cache_key = hashlib.sha256(repository_url.encode()).hexdigest()[:24]
            mirror = cache_root / f"{cache_key}.git"
            if not mirror.exists():
                _run(["git", "clone", "--mirror", repository_url, str(mirror)])
            else:
                _run(["git", "-C", str(mirror), "fetch", "--prune", "origin"])
            if not repo_path.exists():
                workspace_root.mkdir(parents=True, exist_ok=True)
                _run(["git", "clone", "--no-checkout", str(mirror), str(repo_path)])
            _run(
                [
                    "git",
                    "-C",
                    str(repo_path),
                    "checkout",
                    "--detach",
                    run.baseline_commit,
                ]
            )
            observed = _run(["git", "-C", str(repo_path), "rev-parse", "HEAD"])
            if observed != run.baseline_commit:
                raise WorkspaceError("WORKSPACE_BASELINE_MISMATCH")
            python = Path(settings.BRIDGE_EXECUTION_PYTHON or sys.executable).resolve()
            if not python.is_file():
                raise WorkspaceError("WORKSPACE_PYTHON_UNAVAILABLE")
            venv = workspace_root / ".venv"
            _run([str(python), "-m", "venv", str(venv)])
            workspace_python = venv / (
                "Scripts/python.exe" if os.name == "nt" else "bin/python"
            )
            if not workspace_python.is_file():
                raise WorkspaceError("WORKSPACE_VENV_UNAVAILABLE")
            fingerprint = _fingerprint(repo_path)
            requirements = repo_path / "requirements.txt"
            if requirements.is_file():
                _run(
                    [
                        str(workspace_python),
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(requirements),
                    ],
                    repo_path,
                )
            db_path = workspace_root / "runtime.sqlite3"
            environment = {
                "DJANGO_SETTINGS_MODULE": "bridge.settings.local",
                "AI_BRIDGE_RUNTIME_DB": str(db_path),
                **profile.environment,
            }
            _run([str(workspace_python), "-m", "pip", "install", "."], repo_path)
            _run(
                [str(workspace_python), "manage.py", "migrate", "--noinput"],
                repo_path,
                environment,
            )
            _run(
                [str(workspace_python), "manage.py", "migrate", "--check"],
                repo_path,
                environment,
            )
            seed_state: dict[str, object] = {"status": "SKIPPED"}
            if profile.seed_command:
                _run(profile.seed_command, repo_path, environment)
                seed_state = {"status": "APPLIED", "command": profile.seed_command}
            services = self._start_services(profile.services, repo_path, environment)
            with transaction.atomic():
                workspace = ExecutionWorkspace.objects.select_for_update().get(
                    pk=workspace.pk
                )
                workspace.root_path = str(workspace_root)
                workspace.repository_path = str(repo_path)
                workspace.repository_url = repository_url
                workspace.base_branch = run.branch
                workspace.base_commit_sha = observed
                workspace.base_ref = run.baseline_commit
                workspace.venv_path = str(venv)
                workspace.python_executable = str(workspace_python)
                workspace.environment = environment
                workspace.database_profile = {
                    **profile.database,
                    "mode": "sqlite",
                    "path": str(db_path),
                    "created": True,
                }
                workspace.runtime_profile = {
                    "database": profile.database,
                    "seed_configured": bool(profile.seed_command),
                    "service_count": len(profile.services),
                }
                workspace.migration_state = {"status": "APPLIED", "verified": True}
                workspace.seed_state = seed_state
                workspace.runtime_services = services
                workspace.dependency_fingerprint = fingerprint
                workspace.provisioned_at = timezone.now()
                workspace.verified_at = timezone.now()
                workspace.status = ExecutionWorkspace.Status.READY
                workspace.retention_until = _retention(run)
                workspace.save()
            return workspace
        except (OSError, subprocess.SubprocessError, WorkspaceError) as exc:
            with transaction.atomic():
                workspace = ExecutionWorkspace.objects.select_for_update().get(
                    pk=workspace.pk
                )
                workspace.status = ExecutionWorkspace.Status.FAILED
                workspace.failure_code = str(exc)[:128]
                workspace.failure_details = {"stage": "provisioning"}
                workspace.retention_until = _retention(run)
                workspace.save()
            raise WorkspaceError("WORKSPACE_PROVISIONING_FAILED") from exc

    def _start_services(
        self,
        services: list[dict[str, object]],
        repository: Path,
        environment: dict[str, str],
    ) -> list[dict[str, object]]:
        """Start only declared profile services; their PIDs remain runtime evidence."""
        started: list[dict[str, object]] = []
        for service in services:
            command_value = service["command"]
            if not isinstance(command_value, list):
                raise WorkspaceError("RUNTIME_SERVICE_COMMAND_INVALID")
            command = [str(item) for item in command_value]
            try:
                process = subprocess.Popen(  # noqa: S603
                    command,
                    cwd=repository,
                    env={**os.environ, **environment},
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=False,
                )
            except OSError as exc:
                raise WorkspaceError("RUNTIME_SERVICE_START_FAILED") from exc
            healthcheck = service.get("healthcheck")
            if healthcheck:
                if not isinstance(healthcheck, list) or not all(
                    isinstance(item, str) and item for item in healthcheck
                ):
                    process.terminate()
                    raise WorkspaceError("RUNTIME_SERVICE_HEALTHCHECK_INVALID")
                _run([str(item) for item in healthcheck], repository, environment)
            started.append(
                {
                    "name": str(service["name"]),
                    "pid": process.pid,
                    "status": "HEALTHY",
                    "shutdown_command": service.get("shutdown_command", []),
                }
            )
        return started

    def shutdown_services(self, workspace: ExecutionWorkspace) -> None:
        """Gracefully stop profile-owned processes before workspace retention."""
        for service in workspace.runtime_services:
            if not isinstance(service, dict):
                continue
            shutdown = service.get("shutdown_command")
            if isinstance(shutdown, list) and shutdown:
                _run(
                    [str(item) for item in shutdown],
                    Path(workspace.repository_path),
                    workspace.environment,
                )
            elif isinstance(service.get("pid"), int):
                try:
                    os.kill(service["pid"], 15)
                except OSError:
                    pass
            service["status"] = "STOPPED"
        workspace.save(update_fields=["runtime_services", "updated_at"])

    def verify(self, workspace: ExecutionWorkspace) -> bool:
        root, _ = _settings()
        path = Path(workspace.root_path)
        repo = Path(workspace.repository_path)
        python = Path(workspace.python_executable)
        return bool(
            workspace.status
            in {
                ExecutionWorkspace.Status.READY,
                ExecutionWorkspace.Status.IN_USE,
                ExecutionWorkspace.Status.RETAINED,
            }
            and _under(path, root)
            and repo.is_dir()
            and python.is_file()
            and _run(["git", "-C", str(repo), "rev-parse", "HEAD"])
            == workspace.base_commit_sha
        )

    def descriptor(
        self, workspace: ExecutionWorkspace, run: ExecutionRun
    ) -> dict[str, object]:
        if not self.verify(workspace):
            raise WorkspaceError("WORKSPACE_NOT_READY")
        return {
            "cwd": workspace.repository_path,
            "repository_root": workspace.repository_path,
            "base_commit_sha": workspace.base_commit_sha,
            "repository_url": workspace.repository_url,
            "python_executable": workspace.python_executable,
            "virtual_environment": workspace.venv_path,
            "environment": workspace.environment,
            "database_profile": workspace.database_profile,
            "application_database": workspace.database_profile,
            "migration_state": workspace.migration_state,
            "seed_state": workspace.seed_state,
            "runtime_services": workspace.runtime_services,
            "provider_environment": workspace.environment,
            "health_state": "HEALTHY",
            "workspace_id": str(workspace.token),
            "execution_token": str(run.token),
        }

    def mark_in_use(
        self, workspace: ExecutionWorkspace, provider_pid: int | None = None
    ) -> None:
        workspace.status = ExecutionWorkspace.Status.IN_USE
        workspace.provider_pid = provider_pid
        workspace.save(update_fields=["status", "provider_pid", "updated_at"])

    def mark_validating(self, workspace: ExecutionWorkspace) -> None:
        workspace.status = ExecutionWorkspace.Status.VALIDATING
        workspace.save(update_fields=["status", "updated_at"])

    def retain(self, workspace: ExecutionWorkspace, run: ExecutionRun) -> None:
        workspace.status = ExecutionWorkspace.Status.RETAINED
        workspace.retention_until = _retention(run)
        workspace.save(update_fields=["status", "retention_until", "updated_at"])

    def reconcile_cleanup(
        self, now: datetime | None = None
    ) -> list[ExecutionWorkspace]:
        observed = now or timezone.now()
        cleaned: list[ExecutionWorkspace] = []
        for candidate in ExecutionWorkspace.objects.exclude(
            status=ExecutionWorkspace.Status.CLEANED
        ).filter(retention_until__lte=observed):
            with transaction.atomic():
                workspace = ExecutionWorkspace.objects.select_for_update().get(
                    pk=candidate.pk
                )
                if workspace.status == ExecutionWorkspace.Status.CLEANED or (
                    workspace.retention_until is not None
                    and workspace.retention_until > observed
                ):
                    continue
                root, _ = _settings()
                path = Path(workspace.root_path)
                if not workspace.root_path or not _under(path, root) or path == root:
                    workspace.status = ExecutionWorkspace.Status.FAILED
                    workspace.failure_code = "WORKSPACE_CLEANUP_PATH_UNSAFE"
                    workspace.save(
                        update_fields=["status", "failure_code", "updated_at"]
                    )
                    continue
                workspace.status = ExecutionWorkspace.Status.CLEANUP_PENDING
                workspace.cleanup_started_at = observed
                workspace.save(
                    update_fields=["status", "cleanup_started_at", "updated_at"]
                )
                from .execution import add_event

                add_event(
                    workspace.run,
                    "WORKSPACE_RECONCILED",
                    workspace_id=str(workspace.token),
                )
                add_event(
                    workspace.run,
                    "WORKSPACE_CLEANUP_STARTED",
                    workspace_id=str(workspace.token),
                )
                manifest = {
                    "workspace_id": str(workspace.token),
                    "root": str(path),
                    "cleaned_at": observed.isoformat(),
                }
                if path.exists():
                    shutil.rmtree(path)
                workspace.status = ExecutionWorkspace.Status.CLEANED
                workspace.cleaned_at = observed
                workspace.cleanup_manifest = manifest
                workspace.save(
                    update_fields=[
                        "status",
                        "cleaned_at",
                        "cleanup_manifest",
                        "updated_at",
                    ]
                )
                add_event(
                    workspace.run,
                    "WORKSPACE_CLEANED",
                    workspace_id=str(workspace.token),
                )
                cleaned.append(workspace)
        return cleaned

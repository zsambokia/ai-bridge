"""Server-owned, retry-safe repository bootstrap for an approved COO plan."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.db import transaction

from .models import FactoryMission, Project


class RepositoryRemediationRequired(RuntimeError):
    """A non-destructive repository problem that Orki can retry or remediate."""


@dataclass(frozen=True)
class RepositoryResult:
    full_name: str
    remote_url: str
    workspace: Path
    initial_commit: str
    default_branch: str
    created: bool


def _run(*args: str, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip().splitlines()[-1:]
        raise RepositoryRemediationRequired(
            detail[0] if detail else "repository command failed"
        )
    return completed.stdout.strip()


def _proposal(mission: FactoryMission) -> dict[str, object]:
    value = mission.repository_proposal
    if not isinstance(value, dict):
        raise RepositoryRemediationRequired("missing repository proposal")
    return value


def _require_new_repository(proposal: dict[str, object]) -> tuple[str, str, str]:
    owner = str(proposal.get("owner", "")).strip()
    name = str(proposal.get("name", "")).strip()
    visibility = str(proposal.get("visibility", "private")).lower()
    if not owner or not name or visibility not in {"private", "public"}:
        raise RepositoryRemediationRequired("incomplete repository proposal")
    if any(part in name for part in ("/", "\\", "..")):
        raise RepositoryRemediationRequired("unsafe repository name")
    return owner, name, visibility


def _github_identity() -> str:
    return _run("gh", "api", "user", "--jq", ".login")


def _workspace_for(project: Project, name: str) -> Path:
    base = Path(
        os.environ.get(
            "AI_BRIDGE_FACTORY_WORKSPACE",
            settings.BASE_DIR / "var" / "factory-projects",
        )
    )
    return base.resolve() / project.project_id / name


def _bootstrap_git(workspace: Path, branch: str, remote_url: str) -> str:
    workspace.mkdir(parents=True, exist_ok=True)
    if not (workspace / ".git").exists():
        _run("git", "init", "-b", branch, cwd=workspace)
    if not (workspace / "README.md").exists():
        (workspace / "README.md").write_text("# Managed by Orki\n", encoding="utf-8")
    if not (workspace / ".gitignore").exists():
        (workspace / ".gitignore").write_text(
            ".venv/\n__pycache__/\n.env\n", encoding="utf-8"
        )
    _run("git", "add", "README.md", ".gitignore", cwd=workspace)
    has_commit = (
        subprocess.run(
            ("git", "rev-parse", "--verify", "HEAD"), cwd=workspace, capture_output=True
        ).returncode
        == 0
    )
    if not has_commit:
        _run(
            "git",
            "-c",
            "user.name=Orki",
            "-c",
            "user.email=orki@ai-bridge.local",
            "commit",
            "-m",
            "chore: initialize Orki workspace",
            cwd=workspace,
        )
    remotes = _run("git", "remote", cwd=workspace).splitlines()
    if "origin" not in remotes:
        _run("git", "remote", "add", "origin", remote_url, cwd=workspace)
    existing = _run("git", "remote", "get-url", "origin", cwd=workspace)
    if existing != remote_url:
        raise RepositoryRemediationRequired(
            "workspace origin conflicts with approved repository"
        )
    _run("git", "push", "-u", "origin", branch, cwd=workspace)
    return _run("git", "rev-parse", "HEAD", cwd=workspace)


def ensure_repository(mission: FactoryMission) -> RepositoryResult:
    """Create/connect exactly the approved repository and register it on Project.

    The browser never provides identity.  Creation is authorised by the approved
    Plan, constrained to the authenticated ``gh`` identity, and is idempotent.
    """
    project = mission.session.project
    if project is None:
        raise RepositoryRemediationRequired("mission has no Project Registry record")
    proposal = _proposal(mission)
    mode = str(proposal.get("mode", "create")).lower()
    branch = str(proposal.get("default_branch", "main")).strip() or "main"
    registered_name = project.repository_full_name
    if registered_name and registered_name != f"pending/{project.project_id}":
        proposed_name = str(proposal.get("full_name", "")).strip()
        if mode == "create":
            owner, name, _visibility = _require_new_repository(proposal)
            proposed_name = f"{owner}/{name}"
        if registered_name != proposed_name:
            raise RepositoryRemediationRequired(
                "Project Registry already points at another repository"
            )
    if mode == "existing":
        full_name = str(proposal.get("full_name", "")).strip()
        remote_url = str(proposal.get("remote_url", "")).strip()
        if not full_name or not remote_url:
            raise RepositoryRemediationRequired(
                "incomplete existing repository proposal"
            )
        name = full_name.rsplit("/", 1)[-1]
        created = False
    elif mode == "create":
        owner, name, visibility = _require_new_repository(proposal)
        identity = _github_identity()
        if owner != identity:
            raise RepositoryRemediationRequired(
                "approved repository owner is not the authenticated GitHub identity"
            )
        full_name = f"{owner}/{name}"
        remote_url = f"https://github.com/{full_name}.git"
        # `gh repo view` is the idempotency and conflict check: never overwrite.
        exists = (
            subprocess.run(
                ("gh", "repo", "view", full_name, "--json", "nameWithOwner"),
                capture_output=True,
                text=True,
            ).returncode
            == 0
        )
        if not exists:
            _run(
                "gh",
                "repo",
                "create",
                full_name,
                "--" + visibility,
                "--description",
                str(proposal.get("description", "Created by Orki")),
            )
        created = not exists
    else:
        raise RepositoryRemediationRequired("unknown repository proposal mode")

    workspace = _workspace_for(project, name)
    initial_commit = _bootstrap_git(workspace, branch, remote_url)
    with transaction.atomic():
        project.repository_full_name = full_name
        project.repository_root = str(workspace)
        project.onboarding_status = Project.OnboardingStatus.READY
        project.save(
            update_fields=[
                "repository_full_name",
                "repository_root",
                "onboarding_status",
                "updated_at",
            ]
        )
        mission.delivery_status = {
            "state": "repository_ready",
            "next": "A repository elkészült; Orki elindítja a megvalósítást.",
            "repository": full_name,
            "initial_commit": initial_commit,
            "default_branch": branch,
        }
        mission.save(update_fields=["delivery_status", "updated_at"])
    return RepositoryResult(
        full_name, remote_url, workspace, initial_commit, branch, created
    )

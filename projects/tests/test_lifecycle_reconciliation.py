"""Coverage for evidence-backed external execution reconciliation."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TypedDict

import pytest

from projects.lifecycle_reconciliation import reconcile_external_execution
from projects.models import ExecutableScope, McpAuditEvent, Project
from projects.scopes import propose_scope


class ReconciliationInputs(TypedDict):
    scope_identifier: str
    final_commit_sha: str
    evidence_manifest: dict[str, str]
    engineering_audit_path: str
    acceptance_evidence_path: str
    acceptance_reference: str
    source_kind: str
    reconciled_by: str


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, text=True, capture_output=True
    ).stdout.strip()


@pytest.fixture
def reconciled_project(tmp_path: Path) -> tuple[Project, Path, str]:
    (tmp_path / ".bridge").mkdir()
    (tmp_path / ".bridge" / "project.yaml").write_text(
        "project: {}\n", encoding="utf-8"
    )
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "baseline")
    commit = _git(tmp_path, "rev-parse", "HEAD")
    project = Project.objects.create(
        project_id="reconcile-project",
        display_name="Reconcile",
        repository_full_name="example/reconcile",
        definition_path=".bridge/project.yaml",
        repository_root=str(tmp_path),
        onboarding_status=Project.OnboardingStatus.READY,
    )
    return project, tmp_path, commit


def _inputs(root: Path, scope: ExecutableScope, commit: str) -> ReconciliationInputs:
    evidence = root / "docs" / "evidence" / "reconcile"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "audit.md").write_text(
        f"PASS\n{scope.identifier}\n{commit}\n", encoding="utf-8"
    )
    (evidence / "acceptance.md").write_text(
        f"PASS — ACCEPTED\nPO-acceptance\n{scope.identifier}\n{commit}\n",
        encoding="utf-8",
    )
    (evidence / "gates.md").write_text(
        f"PASS\n{scope.identifier}\n{commit}\n", encoding="utf-8"
    )
    return {
        "scope_identifier": scope.identifier,
        "final_commit_sha": commit,
        "evidence_manifest": {"gates": "docs/evidence/reconcile/gates.md"},
        "engineering_audit_path": "docs/evidence/reconcile/audit.md",
        "acceptance_evidence_path": "docs/evidence/reconcile/acceptance.md",
        "acceptance_reference": "PO-acceptance",
        "source_kind": "FACTORY_DEVELOPMENT",
        "reconciled_by": "factory-test",
    }


@pytest.mark.django_db
def test_reconciliation_accepts_verified_factory_execution(
    reconciled_project: tuple[Project, Path, str],
) -> None:
    project, root, commit = reconciled_project
    scope = propose_scope(project, "External completed work", kind="SPRINT")
    record, replay = reconcile_external_execution(
        project=project, **_inputs(root, scope, commit)
    )
    scope.refresh_from_db()
    assert replay is False
    assert record.status == "ACCEPTED"
    assert scope.status == "ACCEPTED"
    assert [entry["status"] for entry in record.transition_log] == [
        "RECONCILING",
        "PASS",
        "ACCEPTED",
    ]
    assert scope.record["lifecycle_reconciliation"]["final_commit_sha"] == commit
    event = McpAuditEvent.objects.get(tool_name="scope.reconcile_external_execution")
    assert event.details["historic_runtime_events_created"] is False


@pytest.mark.django_db
def test_reconciliation_rejects_wrong_commit(
    reconciled_project: tuple[Project, Path, str],
) -> None:
    project, root, commit = reconciled_project
    scope = propose_scope(project, "External completed work", kind="SPRINT")
    values = _inputs(root, scope, commit)
    values["final_commit_sha"] = "0" * 40
    with pytest.raises(ValueError, match="COMMIT_NOT_FOUND"):
        reconcile_external_execution(project=project, **values)


@pytest.mark.django_db
def test_reconciliation_rejects_scope_or_missing_evidence(
    reconciled_project: tuple[Project, Path, str],
) -> None:
    project, root, commit = reconciled_project
    scope = propose_scope(project, "External completed work", kind="SPRINT")
    values = _inputs(root, scope, commit)
    values["evidence_manifest"] = {"missing": "docs/evidence/nope.md"}
    with pytest.raises(ValueError, match="EVIDENCE_MISSING"):
        reconcile_external_execution(project=project, **values)
    values = _inputs(root, scope, commit)
    values["scope_identifier"] = (
        "bridge:wrong:sprint:00000000-0000-0000-0000-000000000000"
    )
    with pytest.raises(ValueError, match="EVIDENCE_SCOPE_OR_COMMIT_MISMATCH"):
        reconcile_external_execution(project=project, **values)


@pytest.mark.django_db
def test_reconciliation_is_idempotent_and_rejects_changed_input(
    reconciled_project: tuple[Project, Path, str],
) -> None:
    project, root, commit = reconciled_project
    scope = propose_scope(project, "External completed work", kind="SPRINT")
    values = _inputs(root, scope, commit)
    first, replay = reconcile_external_execution(project=project, **values)
    second, replay = reconcile_external_execution(project=project, **values)
    assert first.pk == second.pk and replay is True
    (root / "docs" / "evidence" / "reconcile" / "additional.md").write_text(
        f"PASS\n{scope.identifier}\n{commit}\n", encoding="utf-8"
    )
    values["evidence_manifest"] = {
        "gates": "docs/evidence/reconcile/gates.md",
        "additional": "docs/evidence/reconcile/additional.md",
    }
    with pytest.raises(ValueError, match="ALREADY_ACCEPTED_DIFFERENT_INPUT"):
        reconcile_external_execution(project=project, **values)


@pytest.mark.django_db
def test_reconciliation_rejects_different_repository(
    reconciled_project: tuple[Project, Path, str], tmp_path: Path
) -> None:
    project, root, commit = reconciled_project
    scope = propose_scope(project, "External completed work", kind="SPRINT")
    other_root = tmp_path / "other-repository"
    other_root.mkdir()
    _git(other_root, "init")
    with pytest.raises(ValueError, match="REPOSITORY_MISMATCH"):
        reconcile_external_execution(
            project=project,
            **_inputs(root, scope, commit),
            repository_root=other_root,
        )

"""Sprint 4 repository-delivery policy tests using real local Git remotes."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import cast

import pytest
from django.contrib import admin
from django.test import RequestFactory

from projects.delivery import DeliveryVerificationError, verify_and_publish_delivery
from projects.execution import complete_run, lifecycle_status_projection, start_run
from projects.models import (
    ExecutionContract,
    ExecutionDelivery,
    ExecutionRun,
    ExecutionStartRequest,
)
from projects.tests.test_execution import StubProvider
from projects.tests.test_execution import (
    consumed_contract as consumed_contract_fixture,  # noqa: F401
)


@pytest.fixture
def delivery_contract(
    request: pytest.FixtureRequest,
) -> tuple[Path, ExecutionContract, ExecutionStartRequest]:
    """Adapt the lifecycle fixture without coupling to its fixture name."""
    return cast(
        tuple[Path, ExecutionContract, ExecutionStartRequest],
        request.getfixturevalue("consumed_contract_fixture"),
    )


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def configure_delivery(
    root: Path, run: ExecutionRun, contract: ExecutionContract
) -> tuple[str, Path]:
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "delivery@example.test")
    git(root, "config", "user.name", "Delivery Test")
    (root / "projects").mkdir(exist_ok=True)
    (root / "projects" / "base.txt").write_text("base\n", encoding="utf-8")
    # The consumed-contract fixture deliberately supplies a small realistic
    # repository tree.  Its complete initial state is the immutable baseline.
    git(root, "add", "--all")
    git(root, "commit", "-m", "base")
    baseline = git(root, "rev-parse", "HEAD")
    remote = root.parent / f"{root.name}-remote.git"
    subprocess.run(
        ["git", "init", "--bare", str(remote)], check=True, capture_output=True
    )
    git(root, "remote", "add", "origin", str(remote))
    git(root, "push", "origin", "HEAD:refs/heads/main")
    run.baseline_commit = baseline
    run.workspace_identifier = str(root)
    run.save(update_fields=["baseline_commit", "workspace_identifier", "updated_at"])
    contract.payload["delivery"] = {
        "mode": "GOVERNED_MAIN",
        "remote_name": "origin",
        "target_ref": "refs/heads/main",
        "force_push_allowed": False,
        "remote_verification_required": True,
        "review_required": False,
        "allowed_path_prefixes": ["projects/", "docs/"],
        "independent_verifier": "AI_BRIDGE_DELIVERY_VERIFIER",
    }
    contract.save(update_fields=["payload"])
    return baseline, remote


def change_and_evidence(root: Path) -> tuple[str, dict[str, object]]:
    (root / "projects" / "delivery.txt").write_text("delivery\n", encoding="utf-8")
    git(root, "add", "projects/delivery.txt")
    git(root, "commit", "-m", "delivery")
    sha = git(root, "rev-parse", "HEAD")
    evidence = root / "docs" / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "CLOSURE_REPORT.md").write_text(
        f"final_commit_sha: {sha}\n", encoding="utf-8"
    )
    (evidence / "acceptance-results.json").write_text(
        '{"result":"PASS"}\n', encoding="utf-8"
    )
    return sha, {
        "execution_result": "PASS",
        "gate_results": {"pytest": "PASS", "ruff": "PASS"},
        "evidence_manifest": {
            "closure_report": "docs/evidence/CLOSURE_REPORT.md",
            "machine_results": "docs/evidence/acceptance-results.json",
        },
        "changed_files": ["projects/delivery.txt"],
        "failure_classification": None,
    }


@pytest.mark.django_db
def test_delivery_publishes_clean_final_commit_and_projects_status(
    delivery_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = delivery_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    _, remote = configure_delivery(root, run, contract)
    sha, completion = change_and_evidence(root)

    complete_run(run, sha, completion)

    run.refresh_from_db()
    assert run.delivery.status == "VERIFIED"
    assert run.delivery.remote_commit_sha == sha
    assert (
        git(root, "ls-remote", "--heads", str(remote), "refs/heads/main").split()[0]
        == sha
    )
    assert lifecycle_status_projection(run)["delivery"] == {
        "status": "VERIFIED",
        "target_ref": "refs/heads/main",
        "final_commit_sha": sha,
        "remote_commit_sha": sha,
        "changed_files": ["projects/delivery.txt"],
        "failure_code": None,
        "verifier": "AI_BRIDGE_DELIVERY_VERIFIER",
        "verified_at": run.delivery.verified_at.isoformat(),  # type: ignore[union-attr]
    }


@pytest.mark.django_db
def test_delivery_rejects_dirty_workspace_without_terminalizing_run(
    delivery_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = delivery_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    configure_delivery(root, run, contract)
    sha, completion = change_and_evidence(root)
    (root / "projects" / "dirty.txt").write_text("not committed\n", encoding="utf-8")

    with pytest.raises(DeliveryVerificationError, match="DELIVERY_DIRTY_WORKTREE"):
        complete_run(run, sha, completion)

    run.refresh_from_db()
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING
    assert run.delivery.failure_code == "DELIVERY_DIRTY_WORKTREE"


@pytest.mark.django_db
def test_delivery_detects_remote_move_and_unrelated_change(
    delivery_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = delivery_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    _, remote = configure_delivery(root, run, contract)
    sha, completion = change_and_evidence(root)
    other = root.parent / f"{root.name}-other"
    git(root, "clone", "--branch", "main", str(remote), str(other))
    git(other, "config", "user.email", "other@example.test")
    git(other, "config", "user.name", "Other")
    (other / "projects" / "other.txt").write_text("other\n", encoding="utf-8")
    git(other, "add", "projects/other.txt")
    git(other, "commit", "-m", "remote move")
    git(other, "push", "origin", "HEAD:main")

    with pytest.raises(DeliveryVerificationError, match="DELIVERY_REMOTE_MOVED"):
        complete_run(run, sha, completion)
    run.refresh_from_db()
    assert run.delivery.status == "RECONCILIATION_REQUIRED"
    assert run.lifecycle == ExecutionRun.Lifecycle.RUNNING

    # A separate clean run proves the immutable path allow-list detects a file
    # outside canonical publication roots before any push is attempted.
    run.delivery.delete()
    git(root, "fetch", "origin")
    git(root, "reset", "--hard", run.baseline_commit)
    (root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
    git(root, "add", "unrelated.txt")
    git(root, "commit", "-m", "unrelated")
    bad_sha = git(root, "rev-parse", "HEAD")
    completion["changed_files"] = ["unrelated.txt"]
    evidence_manifest = cast(dict[str, object], completion["evidence_manifest"])
    evidence_manifest["closure_report"] = "docs/evidence/CLOSURE_REPORT.md"
    (root / "docs" / "evidence" / "CLOSURE_REPORT.md").write_text(
        f"final_commit_sha: {bad_sha}\n", encoding="utf-8"
    )
    with pytest.raises(DeliveryVerificationError, match="DELIVERY_UNRELATED_CHANGE"):
        verify_and_publish_delivery(run, bad_sha, completion)


@pytest.mark.django_db
def test_delivery_rejects_force_policy_and_evidence_sha_mismatch(
    delivery_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = delivery_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    configure_delivery(root, run, contract)
    sha, completion = change_and_evidence(root)
    contract.payload["delivery"]["force_push_allowed"] = True
    contract.save(update_fields=["payload"])
    with pytest.raises(DeliveryVerificationError, match="FORCE_PUSH_POLICY_INVALID"):
        verify_and_publish_delivery(run, sha, completion)
    run.delivery.delete()
    contract.payload["delivery"]["force_push_allowed"] = False
    contract.save(update_fields=["payload"])
    (root / "docs" / "evidence" / "CLOSURE_REPORT.md").write_text(
        "wrong sha\n", encoding="utf-8"
    )
    with pytest.raises(
        DeliveryVerificationError, match="DELIVERY_EVIDENCE_FINAL_SHA_MISMATCH"
    ):
        verify_and_publish_delivery(run, sha, completion)


@pytest.mark.django_db
def test_delivery_persists_provider_self_approval_rejection(
    delivery_contract: tuple[Path, ExecutionContract, ExecutionStartRequest],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, contract, request = delivery_contract
    monkeypatch.setattr(
        "projects.execution.provider", lambda identity=None: StubProvider()
    )
    run = start_run(contract, request, root)
    configure_delivery(root, run, contract)
    sha, completion = change_and_evidence(root)
    run.provider_name = "AI_BRIDGE_DELIVERY_VERIFIER"
    run.save(update_fields=["provider_name", "updated_at"])

    with pytest.raises(
        DeliveryVerificationError, match="PROVIDER_SELF_APPROVAL_REJECTED"
    ):
        verify_and_publish_delivery(run, sha, completion)

    assert run.delivery.status == ExecutionDelivery.Status.REJECTED
    assert run.delivery.failure_code == "PROVIDER_SELF_APPROVAL_REJECTED"


def test_delivery_admin_is_read_only_projection() -> None:
    """Admin exposes the same durable delivery record without write actions."""
    delivery_admin = admin.site._registry[ExecutionDelivery]
    request = RequestFactory().get("/admin/projects/executiondelivery/")

    assert delivery_admin.has_add_permission(request) is False
    assert delivery_admin.has_change_permission(request) is False
    assert delivery_admin.has_delete_permission(request) is False
    assert "remote_commit_sha" in delivery_admin.list_display

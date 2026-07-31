"""Contract-bound repository delivery and independent remote verification."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Never

from django.utils import timezone

from .models import ExecutionDelivery, ExecutionRun


class DeliveryVerificationError(ValueError):
    """A delivery policy failure which leaves the worker/run recoverable."""


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=root, check=False, capture_output=True, text=True
    )
    if result.returncode:
        raise DeliveryVerificationError(
            "DELIVERY_GIT_FAILURE:" + (result.stderr.strip() or "unknown")
        )
    return result.stdout.strip()


def _record(run: ExecutionRun, policy: dict[str, Any]) -> ExecutionDelivery:
    delivery, _ = ExecutionDelivery.objects.get_or_create(
        run=run,
        defaults={
            "policy": policy,
            "remote_name": str(policy["remote_name"]),
            "target_ref": str(policy["target_ref"]),
            "verifier_identity": str(policy["independent_verifier"]),
        },
    )
    return delivery


def _reject(delivery: ExecutionDelivery, code: str, **detail: object) -> Never:
    delivery.status = ExecutionDelivery.Status.REJECTED
    delivery.failure_code = code
    delivery.failure_detail = detail
    delivery.save(
        update_fields=["status", "failure_code", "failure_detail", "updated_at"]
    )
    raise DeliveryVerificationError(code)


def delivery_projection(run: ExecutionRun) -> dict[str, object] | None:
    delivery = ExecutionDelivery.objects.filter(run=run).first()
    if delivery is None:
        return None
    return {
        "status": delivery.status,
        "target_ref": delivery.target_ref,
        "final_commit_sha": delivery.final_commit_sha,
        "remote_commit_sha": delivery.remote_commit_sha,
        "changed_files": delivery.changed_files,
        "failure_code": delivery.failure_code or None,
        "verifier": delivery.verifier_identity,
        "verified_at": delivery.verified_at.isoformat()
        if delivery.verified_at
        else None,
    }


def verify_and_publish_delivery(
    run: ExecutionRun, final_commit_sha: str, completion_data: dict[str, object]
) -> ExecutionDelivery | None:
    """Publish only a clean, scope-valid final commit and prove it remotely.

    This function is intentionally not provider-owned.  It is called from the
    canonical completion boundary after release-gate evidence is supplied.
    """
    policy = run.contract.payload.get("delivery")
    if not policy:
        return None
    if not isinstance(policy, dict):
        raise DeliveryVerificationError("DELIVERY_POLICY_INVALID")
    if not all(
        isinstance(policy.get(key), str)
        for key in ("remote_name", "target_ref", "independent_verifier")
    ):
        raise DeliveryVerificationError("DELIVERY_POLICY_INVALID")
    delivery = _record(run, policy)
    if run.provider_name == policy.get("independent_verifier"):
        _reject(delivery, "PROVIDER_SELF_APPROVAL_REJECTED")
    if not re.fullmatch(r"[0-9a-f]{40}", final_commit_sha):
        _reject(delivery, "DELIVERY_FINAL_SHA_INVALID")
    root = Path(run.workspace_identifier)
    if policy.get("force_push_allowed") is not False:
        _reject(delivery, "FORCE_PUSH_POLICY_INVALID")
    raw_manifest = completion_data.get("evidence_manifest")
    if not isinstance(raw_manifest, dict) or not raw_manifest:
        _reject(delivery, "DELIVERY_EVIDENCE_REQUIRED")
    manifest: dict[str, str] = {}
    for key, value in raw_manifest.items():
        if not isinstance(key, str) or not isinstance(value, str):
            _reject(delivery, "DELIVERY_EVIDENCE_REQUIRED")
        manifest[key] = value
    manifest_paths = set(manifest.values())
    # Porcelain compresses an untracked directory into (for example)
    # ``?? docs/evidence/``.  Inspect individual paths instead, so a declared
    # evidence file is permitted but a sibling untracked file is never hidden.
    dirty = (
        _git(root, "diff", "--name-only").splitlines()
        + _git(root, "diff", "--cached", "--name-only").splitlines()
        + _git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    )
    non_evidence_dirty = [path for path in dirty if path not in manifest_paths]
    if non_evidence_dirty:
        _reject(delivery, "DELIVERY_DIRTY_WORKTREE", status=non_evidence_dirty)
    actual_head = _git(root, "rev-parse", "HEAD")
    if actual_head != final_commit_sha:
        _reject(delivery, "DELIVERY_FINAL_SHA_MISMATCH", observed=actual_head)
    changed = [
        p
        for p in _git(
            root, "diff", "--name-only", f"{run.baseline_commit}..{final_commit_sha}"
        ).splitlines()
        if p
    ]
    if not changed:
        _reject(delivery, "DELIVERY_CHANGED_FILES_REQUIRED")
    allowed = policy.get("allowed_path_prefixes", [])
    unrelated = [
        path
        for path in changed
        if not any(path.startswith(prefix) for prefix in allowed)
    ]
    if unrelated:
        _reject(delivery, "DELIVERY_UNRELATED_CHANGE", files=unrelated)
    declared = completion_data.get("changed_files")
    if not isinstance(declared, list) or sorted(declared) != sorted(changed):
        _reject(delivery, "DELIVERY_CHANGED_FILES_MISMATCH", actual=changed)
    gates = completion_data.get("gate_results")
    if not isinstance(gates, dict) or not gates or set(gates.values()) != {"PASS"}:
        _reject(delivery, "DELIVERY_GATES_NOT_PASSED")
    evidence_root = Path(run.workspace_identifier)
    missing = [
        value for value in manifest.values() if not (evidence_root / value).is_file()
    ]
    if missing:
        _reject(delivery, "DELIVERY_EVIDENCE_MISSING", files=missing)
    closure = manifest.get("closure_report")
    if not isinstance(closure, str) or final_commit_sha not in (
        evidence_root / closure
    ).read_text(encoding="utf-8"):
        _reject(delivery, "DELIVERY_EVIDENCE_FINAL_SHA_MISMATCH")
    remote = str(policy["remote_name"])
    target = str(policy["target_ref"])
    remote_before = _git(root, "ls-remote", "--heads", remote, target).split()
    remote_before_sha = remote_before[0] if remote_before else ""
    expected_baseline = run.baseline_commit
    if remote_before_sha and remote_before_sha != expected_baseline:
        delivery.status = ExecutionDelivery.Status.RECONCILIATION_REQUIRED
        delivery.baseline_remote_sha = remote_before_sha
        delivery.failure_code = "DELIVERY_REMOTE_MOVED"
        delivery.failure_detail = {
            "expected": expected_baseline,
            "observed": remote_before_sha,
        }
        delivery.save(
            update_fields=[
                "status",
                "baseline_remote_sha",
                "failure_code",
                "failure_detail",
                "updated_at",
            ]
        )
        raise DeliveryVerificationError("DELIVERY_REMOTE_MOVED")
    push = subprocess.run(
        ["git", "push", remote, f"{final_commit_sha}:{target}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if push.returncode:
        _reject(delivery, "DELIVERY_PUSH_REJECTED", stderr=push.stderr.strip())
    remote_after = _git(root, "ls-remote", "--heads", remote, target).split()
    remote_sha = remote_after[0] if remote_after else ""
    if remote_sha != final_commit_sha:
        _reject(delivery, "DELIVERY_REMOTE_SHA_MISMATCH", observed=remote_sha)
    delivery.status = ExecutionDelivery.Status.VERIFIED
    delivery.baseline_remote_sha = remote_before_sha or expected_baseline
    delivery.final_commit_sha = final_commit_sha
    delivery.remote_commit_sha = remote_sha
    delivery.changed_files = changed
    delivery.evidence_manifest = manifest
    delivery.failure_code = ""
    delivery.failure_detail = {}
    delivery.verified_at = timezone.now()
    delivery.save()
    return delivery

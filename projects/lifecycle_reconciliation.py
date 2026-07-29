"""Evidence-first reconciliation for completed external governed work."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from .models import (
    ExecutableScope,
    ExternalExecutionReconciliation,
    GovernanceApproval,
    McpAuditEvent,
    Project,
)
from .scopes import canonical_hash, validate_scope_record
from .services import project_repository_root


def _evidence_file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not relative or root.resolve() not in path.parents or not path.is_file():
        raise ValueError("RECONCILIATION_EVIDENCE_MISSING")
    if not path.read_text(encoding="utf-8").strip():
        raise ValueError("RECONCILIATION_EVIDENCE_EMPTY")
    return path


def _git_common_dir(root: Path) -> Path:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError("RECONCILIATION_REPOSITORY_INVALID")
    return Path(result.stdout.strip()).resolve()


def _verification_root(registered_root: Path, requested_root: Path | None) -> Path:
    if requested_root is None:
        return registered_root
    requested_root = requested_root.resolve()
    if _git_common_dir(registered_root) != _git_common_dir(requested_root):
        raise ValueError("RECONCILIATION_REPOSITORY_MISMATCH")
    return requested_root


def _verify_commit(root: Path, commit: str) -> None:
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("RECONCILIATION_COMMIT_INVALID")
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"{commit}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode or result.stdout.strip() != commit:
        raise ValueError("RECONCILIATION_COMMIT_NOT_FOUND")


def reconcile_external_execution(
    *,
    project: Project,
    scope_identifier: str,
    final_commit_sha: str,
    evidence_manifest: dict[str, str],
    engineering_audit_path: str,
    acceptance_evidence_path: str,
    acceptance_reference: str,
    source_kind: str,
    reconciled_by: str,
    repository_root: Path | None = None,
) -> tuple[ExternalExecutionReconciliation, bool]:
    """Verify and admit completed work without creating a contract or run.

    Returns the durable record plus whether this was an idempotent replay.
    """
    if source_kind not in {"FACTORY_DEVELOPMENT", "EXTERNAL_GOVERNED_EXECUTION"}:
        raise ValueError("RECONCILIATION_SOURCE_INVALID")
    if not evidence_manifest or not all(
        isinstance(value, str) for value in evidence_manifest.values()
    ):
        raise ValueError("RECONCILIATION_EVIDENCE_INVALID")
    root = _verification_root(
        project_repository_root(project, Path.cwd()), repository_root
    )
    _verify_commit(root, final_commit_sha)
    files = {
        name: _evidence_file(root, path) for name, path in evidence_manifest.items()
    }
    audit = _evidence_file(root, engineering_audit_path)
    acceptance = _evidence_file(root, acceptance_evidence_path)
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [*files.values(), audit, acceptance]
    )
    if scope_identifier not in combined or final_commit_sha not in combined:
        raise ValueError("RECONCILIATION_EVIDENCE_SCOPE_OR_COMMIT_MISMATCH")
    if "PASS" not in audit.read_text(encoding="utf-8"):
        raise ValueError("RECONCILIATION_AUDIT_NOT_PASS")
    acceptance_text = acceptance.read_text(encoding="utf-8")
    if "ACCEPTED" not in acceptance_text or acceptance_reference not in acceptance_text:
        raise ValueError("RECONCILIATION_ACCEPTANCE_NOT_VERIFIABLE")
    digest = hashlib.sha256(
        json.dumps(
            {
                "commit": final_commit_sha,
                "manifest": evidence_manifest,
                "audit": engineering_audit_path,
                "acceptance": acceptance_evidence_path,
                "reference": acceptance_reference,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    with transaction.atomic():
        scope = ExecutableScope.objects.select_for_update().get(
            identifier=scope_identifier, project=project
        )
        validate_scope_record(scope.record, project)
        existing = (
            ExternalExecutionReconciliation.objects.select_for_update()
            .filter(scope=scope)
            .first()
        )
        if existing:
            if existing.evidence_digest != digest:
                raise ValueError("RECONCILIATION_ALREADY_ACCEPTED_DIFFERENT_INPUT")
            return existing, True
        approval, created = GovernanceApproval.objects.get_or_create(
            reference=acceptance_reference,
            defaults={
                "project": project,
                "scope": scope,
                "approved_action": "ACCEPT_EXTERNAL_EXECUTION",
                "approved_by": reconciled_by,
            },
        )
        if (
            approval.project_id != project.id
            or approval.scope_id != scope.id
            or approval.revoked_at is not None
            or approval.approved_action != "ACCEPT_EXTERNAL_EXECUTION"
        ):
            raise ValueError("RECONCILIATION_ACCEPTANCE_INVALID")
        record = ExternalExecutionReconciliation.objects.create(
            scope=scope,
            status=ExternalExecutionReconciliation.Status.RECONCILING,
            source_kind=source_kind,
            final_commit_sha=final_commit_sha,
            evidence_manifest=evidence_manifest,
            evidence_digest=digest,
            engineering_audit_path=engineering_audit_path,
            acceptance_evidence_path=acceptance_evidence_path,
            acceptance_reference=acceptance_reference,
            transition_log=[
                {
                    "status": ExternalExecutionReconciliation.Status.RECONCILING,
                    "recorded_at": timezone.now().isoformat(),
                }
            ],
            verification={
                "commit_verified": True,
                "evidence_verified": True,
                "audit_verified": True,
                "acceptance_verified": True,
                "approval_created_by_reconciliation": created,
            },
            reconciled_by=reconciled_by,
        )
        # Only the reconciliation transition changes the scope; no approval,
        # publication, provider event, contract, or ExecutionRun is fabricated.
        scope_record = dict(scope.record)
        scope_record.update(
            {
                "status": "ACCEPTED",
                "execution_authorization": "NONE",
                "updated_at": timezone.now().isoformat(),
                "lifecycle_reconciliation": {
                    "status": "PASS_ACCEPTED",
                    "final_commit_sha": final_commit_sha,
                    "evidence_digest": digest,
                    "acceptance_reference": acceptance_reference,
                },
            }
        )
        scope_record["content_hash"] = canonical_hash(scope_record)
        scope.status = ExecutableScope.Status.ACCEPTED
        scope.record, scope.content_hash = scope_record, scope_record["content_hash"]
        scope.save(update_fields=["status", "record", "content_hash", "updated_at"])
        record.status = ExternalExecutionReconciliation.Status.PASS
        record.transition_log.append(
            {
                "status": ExternalExecutionReconciliation.Status.PASS,
                "recorded_at": timezone.now().isoformat(),
            }
        )
        record.status = ExternalExecutionReconciliation.Status.ACCEPTED
        record.transition_log.append(
            {
                "status": ExternalExecutionReconciliation.Status.ACCEPTED,
                "recorded_at": timezone.now().isoformat(),
            }
        )
        record.save(update_fields=["status", "transition_log", "updated_at"])
        McpAuditEvent.objects.create(
            caller=reconciled_by,
            tool_name="scope.reconcile_external_execution",
            project=project,
            outcome="PASS_ACCEPTED",
            details={
                "scope_identifier": scope.identifier,
                "final_commit_sha": final_commit_sha,
                "evidence_digest": digest,
                "source_kind": source_kind,
                "historic_runtime_events_created": False,
            },
        )
    return record, False

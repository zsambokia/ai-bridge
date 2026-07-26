"""Canonical execution-contract generation and immutable issuance."""
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

from django.db import transaction
from django.utils import timezone

from .contract_policy import resolve_policy
from .execution_context import build_execution_context
from .models import ExecutionContract, Project
from .services import _current_branch, _head_sha, _repository_identity


def _normalized_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _baseline_exists(repository_root: Path, baseline: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _is_descendant_of(repository_root: Path, ancestor: str, head: str) -> bool:
    """Return whether ``head`` contains ``ancestor`` without trusting refs."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, head],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _sprint_project_matches(document: str, project: Project) -> bool:
    match = re.search(r"^\*\*Project:\*\*\s*(.+?)\s*$", document, re.MULTILINE)
    if match is None:
        return True
    declared = match.group(1).strip(" `").casefold()
    return declared in {project.project_id.casefold(), project.display_name.casefold()}


def _binding_document_hashes(
    repository_root: Path, paths: dict[str, str]
) -> dict[str, dict[str, str]]:
    resolved: dict[str, dict[str, str]] = {}
    for name, relative_path in paths.items():
        path = repository_root / relative_path
        if not path.is_file():
            raise ValueError(f"BINDING_DOCUMENT_MISSING:{relative_path}")
        resolved[name] = {
            "path": relative_path,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    return resolved


def _sprint_specific_gates(sprint_document: str) -> list[dict[str, str]]:
    section = re.search(
        r"## 9\. Required release gates\s*(.*?)(?=\n## |\Z)",
        sprint_document,
        re.IGNORECASE | re.DOTALL,
    )
    if section is None:
        return []
    commands = re.findall(
        r"^\s*(?:python|pytest|ruff|mypy)[^\r\n`]*$", section.group(1), re.MULTILINE
    )
    return [
        {"id": f"sprint-{index + 1}", "command": command.strip()}
        for index, command in enumerate(commands)
    ]


def _payload_for(
    project: Project,
    approved_sprint_path: str,
    task_type: str,
    intent: str,
    repository_root: Path,
    handoff_identifier: str,
    execution_level: str = "SPRINT",
    risk_modifiers: list[str] | None = None,
    child_contract_identifiers: list[str] | None = None,
) -> dict[str, Any]:
    if not task_type.strip() or not intent.strip():
        raise ValueError("TASK_TYPE_AND_INTENT_REQUIRED")
    if _repository_identity(repository_root) != project.repository_full_name:
        raise ValueError("REPOSITORY_IDENTITY_MISMATCH")
    context = build_execution_context(project, approved_sprint_path, repository_root)
    sprint_document = (repository_root / approved_sprint_path).read_text(
        encoding="utf-8"
    )
    if not _sprint_project_matches(sprint_document, project):
        raise ValueError("PROJECT_SPRINT_MISMATCH")
    baseline = _head_sha(repository_root)
    if not _baseline_exists(repository_root, baseline):
        raise ValueError("BASELINE_COMMIT_NOT_FOUND")
    binding_paths = {
        **{key: value for key, value in context.binding_documents.items()},
        "approved_sprint_path": approved_sprint_path,
    }
    task_type = task_type.strip().upper()
    execution_level = execution_level.strip().upper()
    risks = sorted({risk.strip().upper() for risk in risk_modifiers or []})
    policy = resolve_policy(execution_level, task_type, risks)
    policy["required_release_gates"] = sorted(
        {
            "sprint-specific",
            *[gate["id"] for gate in context.release_gates],
        }
    )
    children = sorted(set(child_contract_identifiers or []))
    if policy["child_contract_required"] and not children:
        raise ValueError("EPIC_CHILD_CONTRACT_IDENTIFIERS_REQUIRED")
    evidence_root = context.evidence_root
    if execution_level != "SPRINT":
        evidence_root = f"{evidence_root}/{execution_level.lower()}-{task_type.lower()}"
    return {
        "schema_version": "1.1",
        "handoff_identifier": handoff_identifier,
        "project": {
            "id": project.project_id,
            "repository": context.target_repository,
            "definition_source": project.definition_path,
        },
        "execution": {
            "execution_level": execution_level,
            "task_type": task_type,
            "risk_modifiers": risks,
            "child_contract_identifiers": children,
            "intent": intent.strip(),
            "approved_sprint_path": approved_sprint_path,
            "target_branch": context.target_branch,
            "baseline_commit": baseline,
            # An issued repository artifact necessarily creates a commit after
            # this baseline.  DESCENDANT_OF keeps that immutable issuance
            # publishable while still rejecting an unrelated history.
            "baseline_rule": "DESCENDANT_OF",
        },
        "binding_documents": _binding_document_hashes(repository_root, binding_paths),
        "release_gates": {
            "repository_wide": context.release_gates,
            "sprint_specific": _sprint_specific_gates(sprint_document),
        },
        "policy": policy,
        "evidence": {
            "root": evidence_root,
            "closure_report": f"{evidence_root}/CLOSURE_REPORT.md",
            "machine_results": f"{evidence_root}/acceptance-results.json",
        },
        "allowed_terminal_states": context.allowed_terminal_states,
    }


def generate_execution_contract(
    project: Project,
    approved_sprint_path: str,
    task_type: str,
    intent: str,
    repository_root: Path,
    execution_level: str = "SPRINT",
    risk_modifiers: list[str] | None = None,
    child_contract_identifiers: list[str] | None = None,
) -> ExecutionContract:
    """Create one explicit draft after resolving every binding input."""
    sprint_slug = Path(approved_sprint_path).stem.lower()
    handoff_identifier = f"bridge:{project.project_id}:{sprint_slug}:{uuid4()}"
    payload = _payload_for(
        project,
        approved_sprint_path,
        task_type,
        intent,
        repository_root,
        handoff_identifier,
        execution_level,
        risk_modifiers,
        child_contract_identifiers,
    )
    return ExecutionContract.objects.create(
        project=project,
        handoff_identifier=handoff_identifier,
        approved_sprint_path=approved_sprint_path,
        payload=payload,
        contract_hash=_normalized_hash(payload),
    )


def validate_execution_contract(
    contract: ExecutionContract, repository_root: Path
) -> ExecutionContract:
    """Re-resolve a draft and make validation explicit before issuance."""
    if contract.lifecycle not in {
        ExecutionContract.Lifecycle.DRAFT,
        ExecutionContract.Lifecycle.VALIDATED,
    }:
        raise ValueError("CONTRACT_NOT_VALIDATABLE")
    execution = contract.payload["execution"]
    payload = _payload_for(
        contract.project,
        contract.approved_sprint_path,
        execution["task_type"],
        execution["intent"],
        repository_root,
        contract.handoff_identifier,
        execution.get("execution_level", "SPRINT"),
        execution.get("risk_modifiers", []),
        execution.get("child_contract_identifiers", []),
    )
    contract.payload = payload
    contract.contract_hash = _normalized_hash(payload)
    contract.validation_errors = []
    contract.lifecycle = ExecutionContract.Lifecycle.VALIDATED
    contract.validated_at = timezone.now()
    contract.save()
    return contract


def issue_execution_contract(contract: ExecutionContract) -> ExecutionContract:
    """Issue exactly one validated, collision-free immutable contract."""
    if contract.lifecycle != ExecutionContract.Lifecycle.VALIDATED:
        raise ValueError("CONTRACT_NOT_VALIDATED")
    evidence_root = contract.payload["evidence"]["root"]
    if (
        ExecutionContract.objects.filter(
            lifecycle=ExecutionContract.Lifecycle.ISSUED,
            payload__evidence__root=evidence_root,
        )
        .exclude(pk=contract.pk)
        .exists()
    ):
        raise ValueError("EVIDENCE_PATH_COLLISION")
    with transaction.atomic():
        contract.lifecycle = ExecutionContract.Lifecycle.ISSUED
        contract.issued_at = timezone.now()
        contract.save(update_fields=["lifecycle", "issued_at"])
    return contract


def validate_issued_execution_contract(
    contract: ExecutionContract, repository_root: Path
) -> None:
    """Validate immutable issued inputs immediately before execution starts."""
    if contract.contract_hash != _normalized_hash(contract.payload):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:HASH_MISMATCH")
    execution = contract.payload["execution"]
    if (
        _repository_identity(repository_root)
        != contract.payload["project"]["repository"]
    ):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:REPOSITORY_MISMATCH")
    current_branch = _current_branch(repository_root)
    if current_branch != execution["target_branch"]:
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BRANCH_MISMATCH")
    expected_bindings = contract.payload["binding_documents"]
    binding_paths = {name: item["path"] for name, item in expected_bindings.items()}
    if _binding_document_hashes(repository_root, binding_paths) != expected_bindings:
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BINDING_HASH_MISMATCH")
    baseline = execution["baseline_commit"]
    if not _baseline_exists(repository_root, baseline):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BASELINE_NOT_FOUND")
    head = _head_sha(repository_root)
    rule = execution.get("baseline_rule")
    if rule == "EXACT" and head != baseline:
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BASELINE_EXACT_MISMATCH")
    if rule == "DESCENDANT_OF" and not _is_descendant_of(
        repository_root, baseline, head
    ):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BASELINE_NOT_ANCESTOR")
    if rule not in {"EXACT", "DESCENDANT_OF"}:
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BASELINE_RULE_INVALID")


def consume_execution_contract(
    contract: ExecutionContract, repository_root: Path
) -> ExecutionContract:
    """Acknowledge one issued contract before mutation; an Epic is not code authority."""
    if contract.lifecycle != ExecutionContract.Lifecycle.ISSUED:
        raise ValueError("CONTRACT_NOT_ISSUED")
    if contract.payload["policy"]["child_contract_required"]:
        raise ValueError("EPIC_CHILD_CONTRACT_REQUIRED")
    validate_issued_execution_contract(contract, repository_root)
    contract.lifecycle = ExecutionContract.Lifecycle.CONSUMED
    contract.consumed_at = timezone.now()
    contract.save(update_fields=["lifecycle", "consumed_at"])
    return contract


def complete_execution_contract(
    contract: ExecutionContract, final_commit_sha: str, closure_state: str
) -> ExecutionContract:
    """Bind a consumed execution to its terminal evidence state."""
    if contract.lifecycle != ExecutionContract.Lifecycle.CONSUMED:
        raise ValueError("CONTRACT_NOT_CONSUMED")
    if closure_state not in contract.payload["allowed_terminal_states"]:
        raise ValueError("CLOSURE_STATE_INVALID")
    if not re.fullmatch(r"[0-9a-f]{40}", final_commit_sha):
        raise ValueError("FINAL_COMMIT_INVALID")
    contract.lifecycle = ExecutionContract.Lifecycle.COMPLETED
    contract.completed_at = timezone.now()
    contract.final_commit_sha = final_commit_sha
    contract.closure_state = closure_state
    contract.save(
        update_fields=["lifecycle", "completed_at", "final_commit_sha", "closure_state"]
    )
    return contract


def supersede_execution_contract(
    contract: ExecutionContract, replacement: ExecutionContract
) -> ExecutionContract:
    if contract.lifecycle not in {
        ExecutionContract.Lifecycle.ISSUED,
        ExecutionContract.Lifecycle.VALIDATED,
    }:
        raise ValueError("CONTRACT_NOT_SUPERSEDABLE")
    if replacement.project_id != contract.project_id:
        raise ValueError("CONTRACT_PROJECT_MISMATCH")
    contract.lifecycle = ExecutionContract.Lifecycle.SUPERSEDED
    contract.superseded_by = replacement
    contract.save(update_fields=["lifecycle", "superseded_by"])
    return contract


def revoke_execution_contract(contract: ExecutionContract) -> ExecutionContract:
    if contract.lifecycle not in {
        ExecutionContract.Lifecycle.DRAFT,
        ExecutionContract.Lifecycle.VALIDATED,
        ExecutionContract.Lifecycle.ISSUED,
    }:
        raise ValueError("CONTRACT_NOT_REVOKABLE")
    contract.lifecycle = ExecutionContract.Lifecycle.REVOKED
    contract.save(update_fields=["lifecycle"])
    return contract


def render_execution_handoff(contract: ExecutionContract) -> str:
    """Render only persisted machine data, never request-time inputs."""
    payload = contract.payload
    execution = payload["execution"]
    return "\n".join(
        (
            f"# Execution Contract — {payload['handoff_identifier']}",
            "",
            f"**Lifecycle:** {contract.lifecycle}",
            f"**Project:** {payload['project']['id']}",
            f"**Repository:** {payload['project']['repository']}",
            f"**Sprint:** `{execution['approved_sprint_path']}`",
            f"**Task type:** {execution['task_type']}",
            f"**Execution level:** {execution.get('execution_level', 'SPRINT')}",
            f"**Target branch:** {execution['target_branch']}",
            f"**Baseline:** `{execution['baseline_commit']}`",
            f"**Contract SHA-256:** `{contract.contract_hash}`",
            "",
            "## Intent",
            execution["intent"],
            "",
            "## Evidence",
            payload["evidence"]["root"],
        )
    )

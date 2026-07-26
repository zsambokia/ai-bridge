"""Canonical execution-contract generation and immutable issuance."""

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

from .execution_context import build_execution_context
from .models import ExecutionContract, Project
from .services import _head_sha, _repository_identity


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
    evidence_root = context.evidence_root
    return {
        "schema_version": "1.0",
        "handoff_identifier": handoff_identifier,
        "project": {
            "id": project.project_id,
            "repository": context.target_repository,
            "definition_source": project.definition_path,
        },
        "execution": {
            "task_type": task_type.strip(),
            "intent": intent.strip(),
            "approved_sprint_path": approved_sprint_path,
            "target_branch": context.target_branch,
            "baseline_commit": baseline,
            "baseline_rule": "EXACT",
        },
        "binding_documents": _binding_document_hashes(repository_root, binding_paths),
        "release_gates": {
            "repository_wide": context.release_gates,
            "sprint_specific": _sprint_specific_gates(sprint_document),
        },
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

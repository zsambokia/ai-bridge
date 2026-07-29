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

from .execution import provider
from .execution_context import build_execution_context
from .models import (
    ContractConsumption,
    ExecutableScope,
    ExecutionContract,
    ExecutionRun,
    Project,
)
from .scopes import approved_scope, render_scope
from .services import (
    _current_branch,
    _head_sha,
    _repository_identity,
    project_repository_root,
)


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
    """Deprecated compatibility boundary: Markdown can no longer issue work."""
    raise ValueError("LEGACY_CONTRACT_GENERATION_DISABLED")


def _scope_for_contract(contract: ExecutionContract) -> ExecutableScope:
    if contract.payload.get("schema_version") != "2.0":
        raise ValueError("LEGACY_CONTRACT_NOT_EXECUTABLE")
    declared = contract.payload.get("approved_scope", {})
    try:
        scope = ExecutableScope.objects.get(
            identifier=declared["identifier"], project=contract.project
        )
    except (ExecutableScope.DoesNotExist, KeyError) as exc:
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:SCOPE_AUTHORITY_MISSING") from exc
    authorized = {
        **approved_scope(scope),
        # The projection itself is published in the Bridge repository, while a
        # provider executes in the registered project workspace.  Persist the
        # exact projection inside the hash-bound contract so the provider can
        # verify and execute the approved authority without assuming the two
        # repositories share a filesystem.
        "content": render_scope(scope),
    }
    for key in (
        "identifier",
        "path",
        "content_hash",
        "proposal_hash",
        "approval_reference",
    ):
        if declared.get(key) != authorized.get(key):
            raise ValueError("CONTRACT_INTEGRITY_FAILURE:SCOPE_BINDING_MISMATCH")
    if declared.get("content") != render_scope(scope):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:SCOPE_CONTENT_MISMATCH")
    return scope


def _assert_scope_publication(scope: ExecutableScope, repository_root: Path) -> None:
    path = repository_root / scope.published_path
    if not path.is_file() or path.read_text(encoding="utf-8") != render_scope(scope):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:SCOPE_PUBLICATION_MISMATCH")


def generate_scope_execution_contract(
    scope: ExecutableScope, platform_root: Path, *, issuer: str = "AI_BRIDGE"
) -> ExecutionContract:
    """Generate a provider-neutral contract from Bridge-managed scope authority."""
    if issuer != "AI_BRIDGE":
        raise ValueError("CONTRACT_AUTHORITY_REQUIRED")
    authorized = {
        **approved_scope(scope),
        "content": render_scope(scope),
    }
    if not authorized["path"]:
        raise ValueError("SCOPE_NOT_PUBLISHED")
    handoff_identifier = f"bridge:{scope.project.project_id}:contract:{uuid4()}"
    context = build_execution_context(scope.project, authorized["path"], platform_root)
    repository_root = project_repository_root(scope.project, platform_root)
    baseline = _head_sha(repository_root)
    record = scope.record
    selected_provider = provider().name
    payload = {
        "schema_version": "2.0",
        "contract_id": handoff_identifier,
        "handoff_identifier": handoff_identifier,
        "issuer": {
            "system": "AI_BRIDGE",
            "authority_instance": "default",
            "issued_by": issuer,
        },
        "project": {
            "id": scope.project.project_id,
            "repository": context.target_repository,
        },
        "approved_scope": authorized,
        "approval_reference": authorized["approval_reference"],
        "execution": {
            "execution_level": record["execution_level"],
            "task_type": record["task_type"],
            "work_type": record.get("work_type", record["task_type"]),
            "intent": record["intent"],
            "target_branch": context.target_branch,
            "baseline_commit": baseline,
            "baseline_rule": "DESCENDANT_OF",
        },
        "provider_policy": {
            "selected_provider_identity": selected_provider,
            "eligible_provider_identities": [selected_provider],
            "provider_may_issue": False,
            "provider_may_consume_own_issue": False,
            "supported_schema_versions": ["2.0"],
        },
        "policy": record["policy"],
        "release_gates": {"repository_wide": context.release_gates},
        "evidence": {
            "root": f"docs/evidence/{scope.identifier.replace(':', '-')}",
            "closure_report": f"docs/evidence/{scope.identifier.replace(':', '-')}/CLOSURE_REPORT.md",
            "machine_results": f"docs/evidence/{scope.identifier.replace(':', '-')}/acceptance-results.json",
        },
        "allowed_terminal_states": context.allowed_terminal_states,
    }
    if "audit" in record:
        payload["execution"]["audit"] = record["audit"]
    return ExecutionContract.objects.create(
        project=scope.project,
        handoff_identifier=handoff_identifier,
        approved_sprint_path=authorized["path"],
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
    if contract.payload.get("schema_version") == "2.0":
        if contract.payload.get("issuer", {}).get("system") != "AI_BRIDGE":
            raise ValueError("CONTRACT_AUTHORITY_REQUIRED")
        _assert_scope_publication(_scope_for_contract(contract), repository_root)
        contract.validation_errors = []
        contract.lifecycle = ExecutionContract.Lifecycle.VALIDATED
        contract.validated_at = timezone.now()
        contract.save(update_fields=["validation_errors", "lifecycle", "validated_at"])
        return contract
    raise ValueError("LEGACY_CONTRACT_NOT_EXECUTABLE")


def issue_execution_contract(
    contract: ExecutionContract, repository_root: Path
) -> ExecutionContract:
    """Issue exactly one validated, collision-free immutable contract."""
    if contract.lifecycle != ExecutionContract.Lifecycle.VALIDATED:
        raise ValueError("CONTRACT_NOT_VALIDATED")
    _assert_scope_publication(_scope_for_contract(contract), repository_root)
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
    contract: ExecutionContract, platform_root: Path
) -> None:
    """Validate immutable issued inputs immediately before execution starts."""
    if contract.payload.get("schema_version") != "2.0":
        raise ValueError("CONTRACT_AUTHORITY_REQUIRED")
    if contract.contract_hash != _normalized_hash(contract.payload):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:HASH_MISMATCH")
    execution = contract.payload["execution"]
    repository_root = project_repository_root(contract.project, platform_root)
    if (
        _repository_identity(repository_root)
        != contract.payload["project"]["repository"]
    ):
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:REPOSITORY_MISMATCH")
    current_branch = _current_branch(repository_root)
    if current_branch != execution["target_branch"]:
        raise ValueError("CONTRACT_INTEGRITY_FAILURE:BRANCH_MISMATCH")
    _assert_scope_publication(_scope_for_contract(contract), platform_root)
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
    contract: ExecutionContract,
    repository_root: Path,
    *,
    expected_hash: str,
    provider_identity: str,
    observed_baseline: str,
    schema_version: str,
    idempotency_key: str,
) -> ExecutionContract:
    """Acknowledge one issued contract before mutation; an Epic is not code authority."""
    if not all(
        (
            expected_hash,
            provider_identity,
            observed_baseline,
            schema_version,
            idempotency_key,
        )
    ):
        raise ValueError("CONSUMPTION_INPUTS_REQUIRED")
    if expected_hash != contract.contract_hash:
        raise ValueError("CONTRACT_HASH_MISMATCH")
    if observed_baseline != contract.payload.get("execution", {}).get(
        "baseline_commit"
    ):
        raise ValueError("CONSUMPTION_BASELINE_MISMATCH")
    if provider_identity == contract.payload.get("issuer", {}).get("issued_by"):
        raise ValueError("PROVIDER_SELF_AUTHORIZATION_REJECTED")
    provider_policy = contract.payload.get("provider_policy", {})
    if provider_identity not in provider_policy.get(
        "eligible_provider_identities", []
    ) or provider_identity != provider_policy.get("selected_provider_identity"):
        raise ValueError("PROVIDER_NOT_ELIGIBLE")
    if schema_version not in provider_policy.get(
        "supported_schema_versions", [schema_version]
    ):
        raise ValueError("CONTRACT_SCHEMA_UNSUPPORTED")
    if contract.payload["policy"]["child_contract_required"]:
        raise ValueError("EPIC_CHILD_CONTRACT_REQUIRED")
    with transaction.atomic():
        contract = ExecutionContract.objects.select_for_update().get(pk=contract.pk)
        if contract.lifecycle != ExecutionContract.Lifecycle.ISSUED:
            raise ValueError("CONTRACT_NOT_ISSUED")
        if (
            contract.payload.get("schema_version") != "2.0"
            or contract.payload.get("issuer", {}).get("system") != "AI_BRIDGE"
        ):
            raise ValueError("CONTRACT_AUTHORITY_REQUIRED")
        validate_issued_execution_contract(contract, repository_root)
        if ContractConsumption.objects.filter(contract=contract).exists():
            raise ValueError("CONTRACT_ALREADY_CONSUMED")
        contract.lifecycle = ExecutionContract.Lifecycle.CONSUMED
        contract.consumed_at = timezone.now()
        contract.save(update_fields=["lifecycle", "consumed_at"])
        ContractConsumption.objects.create(
            contract=contract,
            provider_identity=provider_identity,
            expected_contract_hash=expected_hash,
            observed_baseline=observed_baseline,
            schema_version=schema_version,
            idempotency_key=idempotency_key,
        )
    return contract


def complete_execution_contract(
    contract: ExecutionContract,
    final_commit_sha: str,
    closure_state: str,
    completion_data: dict[str, Any] | None = None,
) -> ExecutionContract:
    """Bind a consumed execution to its terminal evidence state."""
    if contract.lifecycle != ExecutionContract.Lifecycle.RUNNING:
        raise ValueError("CONTRACT_NOT_RUNNING")
    if closure_state not in contract.payload["allowed_terminal_states"]:
        raise ValueError("CLOSURE_STATE_INVALID")
    if not re.fullmatch(r"[0-9a-f]{40}", final_commit_sha):
        raise ValueError("FINAL_COMMIT_INVALID")
    completion_data = completion_data or {}
    if contract.payload.get("schema_version") == "2.0":
        required = {
            "gate_results",
            "evidence_manifest",
            "changed_files",
            "execution_result",
            "failure_classification",
        }
        missing = sorted(required - set(completion_data))
        if missing:
            raise ValueError("COMPLETION_EVIDENCE_REQUIRED:" + ",".join(missing))
        run = (
            ExecutionRun.objects.filter(
                contract=contract, lifecycle=ExecutionRun.Lifecycle.COMPLETED
            )
            .order_by("-ended_at")
            .first()
        )
        if (
            run is None
            or run.final_commit_sha != final_commit_sha
            or run.completion_data != completion_data
        ):
            raise ValueError("RUN_COMPLETION_NOT_VERIFIED")
    contract.lifecycle = ExecutionContract.Lifecycle.COMPLETED
    contract.completed_at = timezone.now()
    contract.final_commit_sha = final_commit_sha
    contract.closure_state = closure_state
    contract.completion_data = completion_data
    contract.save(
        update_fields=[
            "lifecycle",
            "completed_at",
            "final_commit_sha",
            "closure_state",
            "completion_data",
        ]
    )
    return contract


def supersede_execution_contract(
    contract: ExecutionContract,
    replacement: ExecutionContract,
    *,
    allow_running_binding_repair: bool = False,
) -> ExecutionContract:
    allowed_lifecycles = {
        ExecutionContract.Lifecycle.ISSUED,
        ExecutionContract.Lifecycle.VALIDATED,
    }
    if allow_running_binding_repair:
        allowed_lifecycles.add(ExecutionContract.Lifecycle.RUNNING)
    if contract.lifecycle not in allowed_lifecycles:
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
            f"**Scope:** `{payload['approved_scope']['path']}`",
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

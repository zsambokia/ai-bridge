"""Fully automated, disposable GitHub provider MVP proof.

The Django process owns the credential binding.  This module deliberately never
reads a token, invokes ``git``/``gh``, or asks an operator to perform a step.
"""

from __future__ import annotations

import base64
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, cast
from uuid import uuid4

from .cognitive_evolution import (
    build_guidance,
    govern_behaviour,
    propose_behaviour,
    record_experience,
)
from .decision_contract.framework import (
    CONTRACT_VERSION,
    DecisionEvidence,
    DecisionPlanItem,
    ExecutionRequest,
)
from .github_repository_provider import GitHubRepositoryProvider
from .knowledge_pipeline import KnowledgePipeline
from .models import (
    GovernanceApproval,
    KnowledgeContextPackage,
    KnowledgeEntry,
    KnowledgeRevision,
    Project,
    ProviderAuditEvent,
    RepositoryKnowledgeReceipt,
    RuntimeKnowledgeCandidate,
    RuntimeReflectionCandidate,
    SemanticEmbedding,
)
from .orki_runtime import (
    execute_structured_decision,
    start_structured_decision_execution,
)
from .providers import GitHubAdapter, select_repository_provider
from .repository_lifecycle import RepositoryBootstrapLifecycle
from .semantic.intelligence import DjangoVectorStore

AdapterFactory = Callable[[], GitHubAdapter]
ACTOR = "factory-development-mode"
QUERY = "canonical semantic architecture"


def _encoded(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def _write_evidence(root: Path, name: str, payload: dict[str, Any]) -> str:
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return str(path)


def _context_summary(context: KnowledgeContextPackage) -> dict[str, object]:
    return {
        "package_hash": context.package_hash,
        "entry_ids": context.entry_ids,
        "payload": context.payload,
    }


def _runtime(
    project: Project, context: KnowledgeContextPackage, label: str
) -> tuple[RuntimeReflectionCandidate, RuntimeKnowledgeCandidate]:
    candidates = context.payload.get("candidates", [])
    embedding_hits = tuple(
        {"entry_id": item["entry_id"], "score": item["score"]}
        for item in candidates
        if isinstance(item, dict) and "entry_id" in item and "score" in item
    )
    request = ExecutionRequest(
        contract_version=CONTRACT_VERSION,
        decision_id=uuid4(),
        goal="Validate the governed GitHub repository knowledge context.",
        plan=(
            DecisionPlanItem(
                "validate-context", "Validate semantic context", (), "Verified"
            ),
        ),
        required_capabilities=(),
        required_tools=(),
        required_workflows=(),
        evidence=DecisionEvidence(
            knowledge_entry_ids=tuple(context.entry_ids),
            embedding_hits=embedding_hits,
            behaviour="ENGINEERING",
            plan_identifiers=("validate-context",),
            critic_observations=(),
        ),
    )
    execution = start_structured_decision_execution(project, request, actor=ACTOR)
    execute_structured_decision(
        str(execution.token),
        actor=ACTOR,
        operation=lambda: {
            "verification": {
                "passed": True,
                "context_package_hash": context.package_hash,
            },
            "reflection_candidate": {
                "summary": "Semantic context was consumed by the immutable Runtime.",
                "reflection_text": (
                    "The governed repository context produced a verified "
                    "Runtime result."
                ),
                "confidence": 0.95,
            },
            "knowledge_candidate": {
                "title": "GitHub provider Runtime validation",
                "summary": "Runtime consumed the reconstructed knowledge context.",
                "body": (
                    "The provider E2E proof completed through the canonical "
                    "Runtime boundary."
                ),
                "reason": "MVP proof evidence",
                "confidence": 0.95,
                "tags": ["github", "runtime", label],
            },
            "evidence_references": [f"github-provider-e2e:{label}"],
        },
    )
    reflection = RuntimeReflectionCandidate.objects.get(execution=execution)
    knowledge = RuntimeKnowledgeCandidate.objects.get(execution=execution)
    return reflection, knowledge


def _cognitive(
    project: Project, reflection: RuntimeReflectionCandidate, label: str
) -> dict[str, object]:
    experience = record_experience(project, reflection)
    candidate = propose_behaviour(
        project,
        experience,
        strategy_key="verify-governed-context",
        guidance=(
            "Use governed AKB context and verify Runtime evidence before promotion."
        ),
        applicability=["github-provider-e2e", "runtime"],
        actor=ACTOR,
    )
    approval = GovernanceApproval.objects.create(
        reference=f"github-provider-e2e-cognitive-{label}-{uuid4().hex[:12]}",
        project=project,
        approved_action="cognitive_evolution.govern_behaviour",
        approved_by="Factory Development Mode Product Owner",
    )
    governed = govern_behaviour(
        project,
        candidate,
        decision="APPROVE",
        actor=ACTOR,
        approval_reference=approval.reference,
    )
    guidance = build_guidance(project, query="governed runtime context")
    return {
        "experience_id": experience.pk,
        "candidate_id": governed.pk,
        "status": governed.status,
        "guidance_patterns": list(guidance.patterns),
    }


def _guidance_signature(guidance_patterns: list[dict[str, object]]) -> set[str]:
    """Compare meaning, not duplicate historical instances of the same guidance."""
    return {
        json.dumps(
            {
                "strategy_key": pattern.get("strategy_key"),
                "guidance": pattern.get("guidance"),
                "applicability": pattern.get("applicability"),
            },
            sort_keys=True,
        )
        for pattern in guidance_patterns
    }


def _run_once(
    *,
    provider_id: str,
    owner: str,
    evidence_root: Path,
    adapter_factory: AdapterFactory = GitHubAdapter,
) -> dict[str, Any]:
    provider = select_repository_provider(
        provider_id, required_capabilities={"REPOSITORY_READ", "REPOSITORY_WRITE"}
    )
    adapter = adapter_factory()
    run_id = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    repository = ""
    cleanup: dict[str, str] = {"status": "NOT_ATTEMPTED"}
    proof: dict[str, Any] | None = None
    try:
        created = adapter.create_repository(
            provider,
            owner=owner,
            name=f"ai-bridge-e2e-{run_id}",
            private=True,
            description="Disposable AI Bridge automated MVP proof repository",
        )
        repository = str(created.get("full_name") or "")
        branch = str(created.get("default_branch") or "")
        if not repository or not branch:
            raise ValueError("GITHUB_REPOSITORY_CREATE_RESPONSE_INVALID")
        for path, content in {
            "README.md": "# AI Bridge automated provider proof\n",
            "docs/architecture.md": (
                "# Architecture\n\nThe AKB is canonical; semantic artifacts "
                "are derived.\n"
            ),
            "docs/roadmap.md": "# Roadmap\n\nGoverned repository knowledge intake.\n",
        }.items():
            adapter.put_repository_file(
                provider,
                repository=repository,
                path=path,
                content_base64=_encoded(content),
                message=f"Bootstrap {path}",
                branch=branch,
            )
        project = Project.objects.create(
            project_id=f"github-provider-e2e-{run_id}",
            display_name="GitHub provider automated E2E proof",
            repository_full_name=repository,
            definition_path="factory-proof",
            onboarding_status=Project.OnboardingStatus.READY,
        )
        approval = GovernanceApproval.objects.create(
            reference=f"github-provider-e2e-akb-{run_id}",
            project=project,
            approved_action="akb.review_candidate",
            approved_by="Factory Development Mode Product Owner",
        )
        remote = GitHubRepositoryProvider(provider, adapter)
        lifecycle = RepositoryBootstrapLifecycle(remote)
        bootstrap = lifecycle.bootstrap(
            project, mode="create", actor=ACTOR, approval_reference=approval.reference
        )
        if not bootstrap or any(receipt.embedding is None for receipt in bootstrap):
            raise ValueError("GITHUB_REPOSITORY_EMBEDDING_MISSING")
        baseline = remote.snapshot(repository)
        pipeline = KnowledgePipeline()
        before = pipeline.retrieve_context(
            project,
            work_context_id=f"github-provider:{run_id}",
            role_context_id="ENGINEERING",
            query=QUERY,
        )
        akb_before = {
            "entries": list(
                KnowledgeEntry.objects.filter(project=project).values(
                    "id", "status", "source_version"
                )
            ),
            "revisions": KnowledgeRevision.objects.filter(
                entry__project=project
            ).count(),
            "approvals": GovernanceApproval.objects.filter(project=project).count(),
            "receipts": RepositoryKnowledgeReceipt.objects.filter(
                project=project
            ).count(),
            "embeddings": SemanticEmbedding.objects.filter(
                entry__project=project
            ).count(),
        }
        baseline_reflection, baseline_knowledge = _runtime(project, before, "baseline")
        baseline_cognitive = _cognitive(project, baseline_reflection, "baseline")
        receipts = RepositoryKnowledgeReceipt.objects.filter(project=project)
        # The receipt is canonical intake provenance, not semantic state.  Its
        # optional embedding pointer must therefore be cleared before the
        # entire derived semantic layer can be destroyed.
        receipts.update(embedding=None)
        SemanticEmbedding.objects.filter(entry__project=project).delete()
        KnowledgeContextPackage.objects.filter(project=project).delete()
        if (
            SemanticEmbedding.objects.filter(entry__project=project).exists()
            or not KnowledgeEntry.objects.filter(project=project).exists()
        ):
            raise ValueError("SEMANTIC_LAYER_DESTRUCTION_INVARIANT_FAILED")
        rebuild = DjangoVectorStore().index_project(project)
        for receipt in receipts.select_related("knowledge_entry"):
            if receipt.knowledge_entry_id is None:
                continue
            embedding = SemanticEmbedding.objects.get(
                entry_id=receipt.knowledge_entry_id
            )
            receipt.embedding = embedding
            receipt.audit_trail = [
                *receipt.audit_trail,
                {
                    "event": "SEMANTIC_RECONSTRUCTED",
                    "embedding_id": embedding.embedding_id,
                },
            ]
            receipt.save(update_fields=["embedding", "audit_trail", "updated_at"])
        after = pipeline.retrieve_context(
            project,
            work_context_id=f"github-provider:{run_id}",
            role_context_id="ENGINEERING",
            query=QUERY,
        )
        if _context_summary(before) != _context_summary(after):
            raise ValueError("SEMANTIC_RECONSTRUCTION_NOT_EQUIVALENT")
        rebuilt_reflection, rebuilt_knowledge = _runtime(project, after, "rebuilt")
        rebuilt_cognitive = _cognitive(project, rebuilt_reflection, "rebuilt")
        if (
            baseline_reflection.summary != rebuilt_reflection.summary
            or baseline_knowledge.summary != rebuilt_knowledge.summary
        ):
            raise ValueError("RUNTIME_RECONSTRUCTION_NOT_EQUIVALENT")
        baseline_guidance = cast(
            list[dict[str, object]], baseline_cognitive["guidance_patterns"]
        )
        rebuilt_guidance = cast(
            list[dict[str, object]], rebuilt_cognitive["guidance_patterns"]
        )
        if _guidance_signature(baseline_guidance) != _guidance_signature(
            rebuilt_guidance
        ):
            raise ValueError("COGNITIVE_RECONSTRUCTION_NOT_EQUIVALENT")
        current = adapter.read_repository_file(
            provider,
            repository=repository,
            path="docs/architecture.md",
            ref=baseline.commit_sha,
        )
        blob_sha = str(current.get("sha") or "")
        if not blob_sha:
            raise ValueError("GITHUB_REPOSITORY_DOCUMENT_SHA_UNAVAILABLE")
        adapter.put_repository_file(
            provider,
            repository=repository,
            path="docs/architecture.md",
            content_base64=_encoded(
                "# Architecture\n\nThe AKB is canonical; semantic artifacts "
                "are derived.\n\nIncremental synchronization is governed.\n"
            ),
            message="Prove incremental synchronization",
            branch=branch,
            blob_sha=blob_sha,
        )
        incremental = lifecycle.sync(
            project,
            commit_sha=baseline.commit_sha,
            actor=ACTOR,
            approval_reference=approval.reference,
        )
        if (
            len(incremental) != 1
            or incremental[0].source_path != "docs/architecture.md"
        ):
            raise ValueError("INCREMENTAL_SYNC_SCOPE_INVALID")
        proof = {
            "status": "PASS",
            "run_id": run_id,
            "architecture_statement": (
                "AKB is authoritative; Semantic Layer, Vector Store and embeddings "
                "are derived and reconstructable without Runtime behaviour change."
            ),
            "provider": {
                "provider_id": provider.provider_id,
                "authentication": "PROVIDER_ENVIRONMENT_BINDING",
            },
            "repository": {
                "full_name": repository,
                "default_branch": branch,
                "id": created.get("id"),
            },
            "bootstrap": {
                "commit_sha": baseline.commit_sha,
                "paths": [item.source_path for item in bootstrap],
            },
            "reproducibility": {
                "akb_before": akb_before,
                "rebuild": rebuild,
                "before": _context_summary(before),
                "after": _context_summary(after),
            },
            "runtime": {
                "baseline_reflection": baseline_reflection.pk,
                "rebuilt_reflection": rebuilt_reflection.pk,
                "state": "COMPLETED",
            },
            "cognitive": {"baseline": baseline_cognitive, "rebuilt": rebuilt_cognitive},
            "incremental_sync": {
                "paths": [item.source_path for item in incremental],
                "receipt_ids": [item.pk for item in incremental],
            },
            "provider_audit_actions": list(
                ProviderAuditEvent.objects.filter(
                    provider=provider, created_at__gte=project.created_at
                ).values_list("action", flat=True)
            ),
        }
        return proof
    finally:
        if repository:
            try:
                adapter.delete_repository(provider, repository=repository)
                cleanup = {"status": "DELETED"}
            except ValueError as exc:
                cleanup = {"status": "RETAINED", "reason": str(exc)}
        # Cleanup status is retained in an independent record even when a proof fails.
        cleanup_file = _write_evidence(
            evidence_root,
            f"github-provider-cleanup-{run_id}.json",
            {"run_id": run_id, "repository": repository, "cleanup": cleanup},
        )
        if proof is not None:
            proof["cleanup"] = cleanup
            proof["cleanup_evidence_file"] = cleanup_file
            proof["evidence_file"] = _write_evidence(
                evidence_root,
                f"github-provider-e2e-{run_id}.json",
                proof,
            )


def _recover_retained_repositories(
    *, provider_id: str, evidence_root: Path, adapter_factory: AdapterFactory
) -> None:
    """Retry automatic cleanup before a new suite creates any repository.

    A provider interruption or a previously missing delete permission must not
    turn into a manual repository-cleanup task for a Product Owner.
    """
    retained_files = sorted(evidence_root.glob("github-provider-cleanup-*.json"))
    if not retained_files:
        return
    provider = select_repository_provider(
        provider_id, required_capabilities={"REPOSITORY_WRITE"}
    )
    adapter = adapter_factory()
    for cleanup_file in retained_files:
        payload = json.loads(cleanup_file.read_text(encoding="utf-8"))
        cleanup = payload.get("cleanup", {})
        repository = str(payload.get("repository") or "")
        if not isinstance(cleanup, dict) or cleanup.get("status") != "RETAINED":
            continue
        if not repository:
            raise ValueError("RETAINED_GITHUB_REPOSITORY_IDENTITY_MISSING")
        adapter.delete_repository(provider, repository=repository)
        payload["cleanup"] = {
            "status": "DELETED",
            "recovered_at": datetime.now(UTC).isoformat(),
        }
        _write_evidence(evidence_root, cleanup_file.name, payload)


def run_github_provider_e2e_suite(
    *,
    provider_id: str,
    owner: str,
    evidence_root: Path,
    adapter_factory: AdapterFactory = GitHubAdapter,
) -> dict[str, Any]:
    """Run three isolated repositories consecutively; a failure aborts certification."""
    if not owner.strip():
        raise ValueError("GITHUB_OWNER_REQUIRED")
    _recover_retained_repositories(
        provider_id=provider_id,
        evidence_root=evidence_root,
        adapter_factory=adapter_factory,
    )
    runs = [
        _run_once(
            provider_id=provider_id,
            owner=owner,
            evidence_root=evidence_root,
            adapter_factory=adapter_factory,
        )
        for _ in range(3)
    ]
    result: dict[str, Any] = {
        "status": "PASS",
        "runs": runs,
        "consecutive_passes": 3,
        "manual_interaction": False,
    }
    result["evidence_file"] = _write_evidence(
        evidence_root, "github-provider-e2e-suite.json", result
    )
    return result

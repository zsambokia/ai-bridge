"""Independent Sprint 06 pipeline from Runtime candidates to governed AKB knowledge."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from projects.knowledge import (
    ALLOWED_TYPES,
    create_or_upsert_candidate,
    review_candidate,
)
from projects.models import (
    KnowledgeContextPackage,
    KnowledgeEntry,
    KnowledgePipelineReceipt,
    Project,
    RuntimeKnowledgeCandidate,
    SemanticEmbedding,
)
from projects.runtime_contract import RuntimeKnowledgeCandidateValidator
from projects.semantic import DjangoVectorStore

_WHITESPACE = re.compile(r"\s+")
_TYPE_PREFIXES = ("knowledge_type:", "knowledge-type:")


@dataclass(frozen=True)
class KnowledgePipelineOutcome:
    """Structured pipeline evidence; callers choose any subsequent business action."""

    receipt_id: int
    candidate_id: int
    knowledge_entry_id: int | None
    embedding_id: str | None
    status: str
    fingerprint: str
    duplicate: bool
    evidence: tuple[dict[str, Any], ...]


def _text(value: str) -> str:
    return _WHITESPACE.sub(" ", value).strip()


def _normalize(candidate: RuntimeKnowledgeCandidate) -> dict[str, Any]:
    RuntimeKnowledgeCandidateValidator.validate_record(
        {
            "schema_version": candidate.schema_version,
            "title": candidate.title,
            "summary": candidate.summary,
            "body": candidate.body,
            "reason": candidate.reason,
            "confidence": candidate.confidence,
            "tags": candidate.tags,
            "evidence_references": candidate.evidence_references,
        }
    )
    tags = sorted({_text(tag).lower() for tag in candidate.tags})
    return {
        "schema_version": candidate.schema_version,
        "title": _text(candidate.title),
        "summary": _text(candidate.summary),
        "body": _text(candidate.body),
        "reason": _text(candidate.reason),
        "confidence": float(candidate.confidence),
        "tags": tags,
        "evidence_references": sorted(
            {_text(item) for item in candidate.evidence_references}
        ),
    }


def _classify(normalized: dict[str, Any]) -> str:
    """Use only a declared type tag; classification never infers a business meaning."""
    for tag in normalized["tags"]:
        for prefix in _TYPE_PREFIXES:
            if tag.startswith(prefix):
                declared = tag.removeprefix(prefix).upper()
                if declared in ALLOWED_TYPES:
                    return declared
    return "GENERAL"


def _fingerprint(normalized: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _audit(receipt: KnowledgePipelineReceipt, event: str, **details: Any) -> None:
    receipt.audit_trail = [*receipt.audit_trail, {"event": event, **details}]


def _outcome(receipt: KnowledgePipelineReceipt) -> KnowledgePipelineOutcome:
    evidence = tuple(receipt.audit_trail)
    embedding_id = None
    if receipt.embedding_id:
        embedding = receipt.embedding
        if embedding is not None:
            embedding_id = embedding.embedding_id
    return KnowledgePipelineOutcome(
        receipt_id=receipt.pk,
        candidate_id=receipt.candidate_id,
        knowledge_entry_id=receipt.knowledge_entry_id,
        embedding_id=embedding_id,
        status=receipt.status,
        fingerprint=receipt.fingerprint,
        duplicate=receipt.status == KnowledgePipelineReceipt.Status.DUPLICATE,
        evidence=evidence,
    )


class KnowledgePipeline:
    """Consumes immutable Runtime candidates without changing frozen components."""

    def __init__(self, store: DjangoVectorStore | None = None) -> None:
        self.store = store or DjangoVectorStore()

    def process(
        self,
        candidate: RuntimeKnowledgeCandidate,
        *,
        actor: str,
        decision: str = "REQUEST_REVIEW",
        approval_reference: str = "",
    ) -> KnowledgePipelineOutcome:
        if decision not in {"REQUEST_REVIEW", "APPROVE", "REJECT"}:
            raise ValueError("KNOWLEDGE_PIPELINE_DECISION_INVALID")
        project = candidate.execution.plan.goal.project
        normalized = _normalize(candidate)
        classification = _classify(normalized)
        fingerprint = _fingerprint(normalized)
        with transaction.atomic():
            receipt, created = (
                KnowledgePipelineReceipt.objects.select_for_update().get_or_create(
                    candidate=candidate,
                    defaults={
                        "project": project,
                        "fingerprint": fingerprint,
                        "classification": classification,
                        "normalized_payload": normalized,
                        "status": KnowledgePipelineReceipt.Status.VALIDATED,
                        "audit_trail": [
                            {
                                "event": "VALIDATED",
                                "schema_version": candidate.schema_version,
                            }
                        ],
                    },
                )
            )
            if receipt.project_id != project.pk or receipt.fingerprint != fingerprint:
                raise ValueError("KNOWLEDGE_PIPELINE_RECEIPT_CONFLICT")
            if not created and receipt.status in {
                KnowledgePipelineReceipt.Status.DUPLICATE,
                KnowledgePipelineReceipt.Status.PROMOTED,
                KnowledgePipelineReceipt.Status.REJECTED,
            }:
                return _outcome(receipt)
            if (
                not created
                and receipt.status == KnowledgePipelineReceipt.Status.IN_REVIEW
                and decision == "REQUEST_REVIEW"
            ):
                return _outcome(receipt)

            if receipt.knowledge_entry_id is None:
                existing = KnowledgeEntry.objects.filter(
                    project=project,
                    source_type="RUNTIME_KNOWLEDGE_CANDIDATE_V1",
                    source_version=fingerprint,
                ).first()
                if existing is not None:
                    receipt.knowledge_entry = existing
                    receipt.status = KnowledgePipelineReceipt.Status.DUPLICATE
                    _audit(receipt, "DEDUPLICATED", entry_id=existing.pk)
                    receipt.save()
                    return _outcome(receipt)
                title = normalized["title"]
                collision = KnowledgeEntry.objects.filter(
                    project=project,
                    scope=KnowledgeEntry.Scope.PROJECT,
                    knowledge_type=classification,
                    title=title,
                ).exists()
                if collision:
                    title = f"{title[:244]} [{fingerprint[:8]}]"
                entry = create_or_upsert_candidate(
                    project,
                    {
                        "entry_key": (
                            f"runtime-knowledge:{project.pk}:{fingerprint[:32]}"
                        ),
                        "scope": KnowledgeEntry.Scope.PROJECT,
                        "knowledge_type": classification,
                        "title": title,
                        "content": f"{normalized['summary']}\n\n{normalized['body']}",
                        "source_type": "RUNTIME_KNOWLEDGE_CANDIDATE_V1",
                        "source_reference": (
                            f"runtime-knowledge-candidate:{candidate.pk}"
                        ),
                        "source_version": fingerprint,
                        "evidence_references": [
                            *normalized["evidence_references"],
                            f"runtime-candidate:{candidate.pk}",
                            f"runtime-execution:{candidate.execution_id}",
                        ],
                        "role_context": ["ENGINEERING"],
                        "work_context_id": (
                            f"runtime-execution:{candidate.execution_id}"
                        ),
                    },
                    actor,
                )
                receipt.knowledge_entry = entry
                _audit(receipt, "CANDIDATE_CREATED", entry_id=entry.pk)

            knowledge_entry = receipt.knowledge_entry
            assert knowledge_entry is not None
            if decision == "REJECT":
                if knowledge_entry.status in {
                    KnowledgeEntry.Status.CANDIDATE,
                    KnowledgeEntry.Status.IN_REVIEW,
                }:
                    review_candidate(project, knowledge_entry.pk, "REJECT", actor)
                receipt.status = KnowledgePipelineReceipt.Status.REJECTED
                _audit(receipt, "REJECTED", entry_id=knowledge_entry.pk)
            elif decision == "REQUEST_REVIEW":
                if knowledge_entry.status == KnowledgeEntry.Status.CANDIDATE:
                    review_candidate(
                        project, knowledge_entry.pk, "REQUEST_REVIEW", actor
                    )
                receipt.status = KnowledgePipelineReceipt.Status.IN_REVIEW
                _audit(receipt, "REVIEW_REQUESTED", entry_id=knowledge_entry.pk)
            else:
                if knowledge_entry.status in {
                    KnowledgeEntry.Status.CANDIDATE,
                    KnowledgeEntry.Status.IN_REVIEW,
                    KnowledgeEntry.Status.REJECTED,
                }:
                    review_candidate(
                        project,
                        knowledge_entry.pk,
                        "APPROVE",
                        actor,
                        approval_reference,
                    )
                self.store.index_project(project)
                embedding = SemanticEmbedding.objects.filter(
                    entry=knowledge_entry
                ).first()
                if embedding is None:
                    raise ValueError("KNOWLEDGE_PIPELINE_EMBEDDING_MISSING")
                receipt.embedding = embedding
                receipt.status = KnowledgePipelineReceipt.Status.PROMOTED
                _audit(
                    receipt,
                    "PROMOTED",
                    entry_id=knowledge_entry.pk,
                    embedding_id=embedding.embedding_id,
                )
            receipt.save()
            return _outcome(receipt)

    def retrieve_context(
        self,
        project: Project,
        *,
        work_context_id: str,
        role_context_id: str,
        query: str,
        retrieval_intent: str = "knowledge-pipeline",
        top_k: int = 5,
    ) -> KnowledgeContextPackage:
        """Persist semantic retrieval evidence, without formatting LLM context."""
        candidates = self.store.search(project, query, top_k=top_k)
        payload = {
            "retrieval_strategy": "SEMANTIC_VECTOR",
            "candidates": [
                {
                    "entry_id": item.entry_id,
                    "score": item.score,
                    "reason": item.reason,
                    "metadata": item.metadata,
                    "evidence": item.evidence,
                }
                for item in candidates
            ],
        }
        package_hash = hashlib.sha256(
            json.dumps(
                {
                    "project_id": project.pk,
                    "work_context_id": work_context_id,
                    "role_context_id": role_context_id,
                    "retrieval_intent": retrieval_intent,
                    "query": query,
                    "payload": payload,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
        package, _ = KnowledgeContextPackage.objects.get_or_create(
            package_hash=package_hash,
            defaults={
                "project": project,
                "work_context_id": work_context_id,
                "role_context_id": role_context_id,
                "retrieval_intent": retrieval_intent,
                "retrieval_query": query,
                "entry_ids": [item.entry_id for item in candidates],
                "source_versions": {
                    str(item.entry_id): str(item.evidence["source_version"])
                    for item in candidates
                },
                "payload": payload,
            },
        )
        if package.project_id != project.pk:
            raise ValueError("KNOWLEDGE_PIPELINE_CONTEXT_PROJECT_CONFLICT")
        return package

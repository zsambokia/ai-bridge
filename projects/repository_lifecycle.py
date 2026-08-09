"""Canonical provider-driven repository bootstrap and incremental AKB intake.

Repository content is evidence, never runtime authority.  This service unifies
new-repository and import discovery after a provider has supplied a snapshot.
It deliberately has no subprocess or GitHub CLI dependency.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Protocol

from django.db import transaction

from projects.knowledge import (
    create_or_upsert_candidate,
    mark_stale_for_source_revision,
    review_candidate,
)
from projects.models import (
    KnowledgeEntry,
    Project,
    RepositoryKnowledgeReceipt,
    SemanticEmbedding,
)
from projects.semantic import DjangoVectorStore


@dataclass(frozen=True)
class RepositoryDocument:
    path: str
    content: str
    commit_sha: str


@dataclass(frozen=True)
class RepositorySnapshot:
    repository_full_name: str
    commit_sha: str
    default_branch: str
    documents: tuple[RepositoryDocument, ...]


class RepositoryProvider(Protocol):
    """GitHub, a clone, or a test provider supplies repository observations."""

    def prepare(self, mode: str, repository_full_name: str) -> None: ...

    def snapshot(self, repository_full_name: str) -> RepositorySnapshot: ...

    def changes_since(
        self, repository_full_name: str, commit_sha: str
    ) -> tuple[RepositoryDocument, ...]: ...


_SPACE = re.compile(r"\s+")
_MAX_AKB_CONTENT = 12000
_TYPE_SIGNALS = (
    ("CONSTITUTION", ("constitution", "foundational rule", "principle")),
    ("ARCHITECTURE_DECISION", ("adr", "architecture decision", "decision record")),
    ("SYSTEM_DESIGN", ("architecture", "component", "boundary", "runtime")),
    ("ROADMAP", ("roadmap", "milestone", "sprint", "release plan")),
    ("RUNBOOK", ("runbook", "operational procedure", "incident")),
    ("POLICY", ("policy", "governance", "must", "shall")),
)


def _normalise(value: str) -> str:
    return _SPACE.sub(" ", value).strip()


def classify_document(document: RepositoryDocument) -> str:
    """Classify primarily by document content; path only breaks equal evidence."""
    content = document.content.lower()
    scores = {
        kind: sum(content.count(signal) for signal in signals)
        for kind, signals in _TYPE_SIGNALS
    }
    highest = max(scores.values(), default=0)
    if highest:
        candidates = {kind for kind, score in scores.items() if score == highest}
        path = document.path.lower()
        for kind, _ in _TYPE_SIGNALS:
            if kind in candidates and kind.lower().replace("_", "-") in path:
                return kind
        return sorted(candidates)[0]
    return "GENERAL"


def _title(document: RepositoryDocument) -> str:
    for line in document.content.splitlines():
        if line.startswith("#"):
            candidate = line.lstrip("# ").strip()
            if candidate:
                return candidate[:255]
    return document.path.rsplit("/", 1)[-1][:255]


def _fingerprint(document: RepositoryDocument, classification: str) -> str:
    return hashlib.sha256(
        json.dumps(
            {
                "path": document.path,
                "content": _normalise(document.content),
                "type": classification,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


def _segments(document: RepositoryDocument) -> tuple[RepositoryDocument, ...]:
    """Preserve large documents in bounded AKB entries rather than truncate them."""
    content = _normalise(document.content)
    if len(content) <= _MAX_AKB_CONTENT:
        return (RepositoryDocument(document.path, content, document.commit_sha),)
    return tuple(
        RepositoryDocument(
            f"{document.path}#chunk-{index}",
            content[offset : offset + _MAX_AKB_CONTENT],
            document.commit_sha,
        )
        for index, offset in enumerate(range(0, len(content), _MAX_AKB_CONTENT), 1)
    )


class RepositoryBootstrapLifecycle:
    """One repository lifecycle for create and import, with governed AKB intake."""

    def __init__(
        self, provider: RepositoryProvider, store: DjangoVectorStore | None = None
    ) -> None:
        self.provider = provider
        self.store = store or DjangoVectorStore()

    def bootstrap(
        self,
        project: Project,
        *,
        mode: str,
        actor: str,
        approval_reference: str,
    ) -> tuple[RepositoryKnowledgeReceipt, ...]:
        if mode not in {"create", "import"}:
            raise ValueError("REPOSITORY_BOOTSTRAP_MODE_INVALID")
        self.provider.prepare(mode, project.repository_full_name)
        snapshot = self.provider.snapshot(project.repository_full_name)
        if snapshot.repository_full_name != project.repository_full_name:
            raise ValueError("REPOSITORY_PROVIDER_IDENTITY_CONFLICT")
        return self._intake(project, snapshot.documents, actor, approval_reference)

    def sync(
        self, project: Project, *, commit_sha: str, actor: str, approval_reference: str
    ) -> tuple[RepositoryKnowledgeReceipt, ...]:
        """Consume provider-reported diffs only; no full repository rebuild occurs."""
        return self._intake(
            project,
            self.provider.changes_since(project.repository_full_name, commit_sha),
            actor,
            approval_reference,
        )

    def _intake(
        self,
        project: Project,
        documents: tuple[RepositoryDocument, ...],
        actor: str,
        approval_reference: str,
    ) -> tuple[RepositoryKnowledgeReceipt, ...]:
        receipts: list[RepositoryKnowledgeReceipt] = []
        for source_document in documents:
            for document in _segments(source_document):
                classification = classify_document(document)
                fingerprint = _fingerprint(document, classification)
                with transaction.atomic():
                    receipt, created = RepositoryKnowledgeReceipt.objects.get_or_create(
                        project=project,
                        source_path=document.path,
                        source_version=document.commit_sha,
                        defaults={
                            "fingerprint": fingerprint,
                            "classification": classification,
                            "status": RepositoryKnowledgeReceipt.Status.DISCOVERED,
                            "audit_trail": [
                                {"event": "DISCOVERED", "path": document.path}
                            ],
                        },
                    )
                    if not created:
                        receipts.append(receipt)
                        continue
                    stale = KnowledgeEntry.objects.filter(
                        project=project,
                        source_type="REPOSITORY_DOCUMENT_V1",
                        source_reference__startswith=source_document.path,
                        status=KnowledgeEntry.Status.ACTIVE,
                    )
                    for prior in stale:
                        mark_stale_for_source_revision(
                            prior, document.commit_sha, actor
                        )
                    title = _title(document)
                    if KnowledgeEntry.objects.filter(
                        project=project,
                        scope=KnowledgeEntry.Scope.PROJECT,
                        knowledge_type=classification,
                        title=title,
                    ).exists():
                        title = f"{title[:244]} [{fingerprint[:8]}]"
                    entry = create_or_upsert_candidate(
                        project,
                        {
                            "entry_key": (
                                f"repository-document:{project.pk}:{fingerprint[:32]}"
                            ),
                            "scope": KnowledgeEntry.Scope.PROJECT,
                            "knowledge_type": classification,
                            "title": title,
                            "content": document.content,
                            "source_type": "REPOSITORY_DOCUMENT_V1",
                            "source_reference": document.path,
                            "source_version": document.commit_sha,
                            "evidence_references": [
                                f"repository:{source_document.path}",
                                f"commit:{document.commit_sha}",
                            ],
                            "role_context": ["ENGINEERING"],
                            "work_context_id": (
                                f"repository-intake:{document.commit_sha}"
                            ),
                        },
                        actor,
                    )
                    review_candidate(
                        project, entry.pk, "APPROVE", actor, approval_reference
                    )
                    entry.refresh_from_db()
                    self.store.index_entry(project, entry)
                    embedding = SemanticEmbedding.objects.get(entry=entry)
                    receipt.knowledge_entry = entry
                    receipt.embedding = embedding
                    receipt.status = RepositoryKnowledgeReceipt.Status.PROMOTED
                    receipt.audit_trail = [
                        *receipt.audit_trail,
                        {"event": "AKB_CANDIDATE_CREATED", "entry_id": entry.pk},
                        {
                            "event": "GOVERNED_PROMOTION",
                            "approval_reference": approval_reference,
                        },
                        {
                            "event": "SEMANTIC_INDEXED",
                            "embedding_id": embedding.embedding_id,
                        },
                    ]
                    receipt.save()
                    receipts.append(receipt)
        return tuple(receipts)

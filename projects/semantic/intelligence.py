"""Provider-neutral, retrieval-only Semantic Intelligence services."""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Protocol

from django.db import transaction

from projects.models import KnowledgeEntry, Project, SemanticEmbedding

TOKEN_RE = re.compile(r"[a-z0-9_]{2,}")


class EmbeddingProvider(Protocol):
    name: str
    model_version: str

    def embed(self, text: str) -> list[float]: ...


class HashEmbeddingProvider:
    """Deterministic local baseline, replaceable by an external provider."""

    name = "LOCAL_HASH"
    model_version = "v1"
    dimensions = 128

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in TOKEN_RE.findall(text.lower()):
            digest = hashlib.sha256(token.encode()).digest()
            vector[int.from_bytes(digest[:4], "big") % self.dimensions] += (
                -1.0 if digest[4] & 1 else 1.0
            )
        length = math.sqrt(sum(item * item for item in vector))
        return [item / length for item in vector] if length else vector


@dataclass(frozen=True)
class SemanticCandidate:
    entry_id: int
    score: float
    reason: str
    metadata: dict[str, Any]
    evidence: dict[str, Any]
    content: str


def _metadata(entry: KnowledgeEntry) -> dict[str, Any]:
    return {
        "entry_key": entry.entry_key,
        "title": entry.title,
        "scope": entry.scope,
        "knowledge_type": entry.knowledge_type,
        "verification_status": entry.verification_status,
        "freshness_status": entry.freshness_status,
        "source_reference": entry.source_reference,
        "source_version": entry.source_version or str(entry.version),
    }


class DjangoVectorStore:
    """Local JSON-vector store behind a provider-independent boundary."""

    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self.provider = provider or HashEmbeddingProvider()

    def index_project(self, project: Project, *, force: bool = False) -> dict[str, int]:
        entries = KnowledgeEntry.objects.filter(
            status=KnowledgeEntry.Status.ACTIVE, project__in=[project, None]
        )
        indexed = cached = 0
        for entry in entries:
            content = f"{entry.title}\n{entry.content}"
            digest = hashlib.sha256(content.encode()).hexdigest()
            version = entry.source_version or str(entry.version)
            current = SemanticEmbedding.objects.filter(
                entry=entry,
                provider=self.provider.name,
                model_version=self.provider.model_version,
            ).first()
            if not force and current and current.content_hash == digest:
                cached += 1
                continue
            identity = hashlib.sha256(
                f"{project.pk}:{entry.pk}:{version}:{self.provider.name}:{self.provider.model_version}".encode()
            ).hexdigest()
            with transaction.atomic():
                SemanticEmbedding.objects.update_or_create(
                    entry=entry,
                    provider=self.provider.name,
                    model_version=self.provider.model_version,
                    defaults={
                        "embedding_id": identity,
                        "source_version": version,
                        "content_hash": digest,
                        "vector": self.provider.embed(content),
                        "metadata": _metadata(entry),
                    },
                )
            indexed += 1
        return {"indexed": indexed, "cached": cached, "eligible": entries.count()}

    def search(
        self,
        project: Project,
        query: str,
        *,
        top_k: int = 5,
        metadata: dict[str, str] | None = None,
    ) -> tuple[SemanticCandidate, ...]:
        vector = self.provider.embed(query)
        records: list[SemanticCandidate] = []
        rows = SemanticEmbedding.objects.select_related("entry").filter(
            provider=self.provider.name,
            model_version=self.provider.model_version,
            entry__status=KnowledgeEntry.Status.ACTIVE,
            entry__project__in=[project, None],
        )
        for row in rows:
            if metadata and any(
                row.metadata.get(key) != value for key, value in metadata.items()
            ):
                continue
            score = sum(
                float(a) * float(b) for a, b in zip(vector, row.vector, strict=True)
            )
            records.append(
                SemanticCandidate(
                    row.entry_id,
                    round(score, 6),
                    "COSINE_SIMILARITY",
                    row.metadata,
                    {
                        "embedding_id": row.embedding_id,
                        "provider": row.provider,
                        "model_version": row.model_version,
                        "source_version": row.source_version,
                    },
                    row.entry.content,
                )
            )
        return tuple(
            sorted(records, key=lambda value: (-value.score, value.entry_id))[:top_k]
        )


class SemanticCandidateSelector:
    """Ranks candidates only; it never selects a business action."""

    def __init__(self, store: DjangoVectorStore | None = None) -> None:
        self.store = store or DjangoVectorStore()

    def select(
        self, project: Project, query: str, **kwargs: Any
    ) -> tuple[SemanticCandidate, ...]:
        return self.store.search(project, query, **kwargs)


class RetrievalService:
    """RAG retrieval boundary: candidates and evidence only."""

    def __init__(self, selector: SemanticCandidateSelector | None = None) -> None:
        self.selector = selector or SemanticCandidateSelector()

    def retrieve(
        self, project: Project, query: str, *, domain: str | None = None, top_k: int = 5
    ) -> tuple[SemanticCandidate, ...]:
        return self.selector.select(
            project,
            query,
            top_k=top_k,
            metadata={"knowledge_type": domain} if domain else None,
        )


@dataclass(frozen=True)
class SemanticContextV2:
    goal: str
    runtime_state: dict[str, Any]
    candidates: tuple[SemanticCandidate, ...]
    text: str
    evidence: tuple[dict[str, Any], ...]


class SemanticContextBuilder:
    """The sole Semantic component allowed to format bounded LLM context."""

    def __init__(self, retrieval: RetrievalService | None = None) -> None:
        self.retrieval = retrieval or RetrievalService()

    def build(
        self,
        project: Project,
        goal: str,
        *,
        runtime_state: dict[str, Any] | None = None,
        token_budget: int = 800,
        top_k: int = 5,
    ) -> SemanticContextV2:
        chosen: list[SemanticCandidate] = []
        consumed = 0
        for candidate in self.retrieval.retrieve(project, goal, top_k=top_k):
            size = len(candidate.content.split())
            if consumed + size <= token_budget:
                chosen.append(candidate)
                consumed += size
        text = "\n\n".join(
            f"[{item.metadata['title']}]\n{item.content}" for item in chosen
        )
        return SemanticContextV2(
            goal,
            runtime_state or {},
            tuple(chosen),
            text,
            tuple(item.evidence for item in chosen),
        )

# Semantic Layer

## Status

Sprint 01 establishes the Semantic Layer foundation. Its current capability is
**durable, governed context selection**, not semantic retrieval.

## Canonical boundary

```text
Semantic request
    -> Semantic Layer service
    -> governed KnowledgeContextPackage
    -> durable SemanticContext result
```

`projects.semantic.build_semantic_context` is the internal entry point. It
delegates all knowledge selection and persistence to
`projects.knowledge.build_and_record_context_package`; it must not duplicate,
override, or bypass AKB governance.

The result carries the immutable context-package ID and hash, selected source
identifiers and versions, stale-source warnings, conflict warnings, and a
machine-readable explanation of why each source was included. A later
Reasoning, Behaviour, Planning, or Runtime caller consumes this artefact by
reference.

## Current selection capability

The underlying AKB package includes active, project-isolated knowledge from
explicit platform/project must-know, work-context, role-context, and lexical
query-match sources. It applies explicit conflict precedence and records the
result durably.

This is a deterministic retrieval foundation. It is intentionally labelled
`DETERMINISTIC_FOUNDATION`; it is **not** an embedding model, vector index,
similarity search, semantic ranking, or completed RAG implementation. No
provider decides which AKB entries are selected.

## Ownership and invariants

- **AKB/Governance** owns entry lifecycle and activation. The Semantic Layer
  reads active knowledge only.
- **Semantic Layer** owns the stable request/result contract and provenance
  projection, not policy or business decisions.
- **Reasoning and Behaviour** may request context but must produce their own
  structured decisions; a context result grants neither authority nor action.
- **Runtime** records/uses artefact references and executes deterministic
  transitions. It does not rank knowledge or infer intent.
- **Providers** may receive an attributable context package but cannot define
  selection behaviour.

## Sprint 02 Semantic Intelligence implementation

`DjangoVectorStore` indexes only `ACTIVE` AKB entries scoped to the requested
Project or Platform. It persists a versioned `SemanticEmbedding` cache with a
deterministic identity, source version and content hash. The initial
`LOCAL_HASH/v1` provider is deterministic and local; its `EmbeddingProvider`
boundary permits FAISS, pgvector, Qdrant or Pinecone-backed adapters without
Runtime changes.

`SemanticCandidateSelector` returns cosine-ranked candidates only, with score,
reason, metadata and embedding/source evidence. `RetrievalService` is RAG
retrieval only. `SemanticContextBuilder` is the only Semantic component which
formats retrieved text, applies its token budget, and emits evidence. Embedding
generation occurs only via explicit index/reindex after AKB approval; Runtime
execution never generates embeddings.

## Program evolution

1. **Sprint 02 — Embedding Infrastructure:** governed embedding identity,
   versioning, storage, refresh and invalidation.
2. **Sprint 03 — Semantic Retrieval:** query embedding, scoped similarity
   retrieval, deterministic safety filters and rank provenance.
3. **Sprint 04 — Context Builder Evolution:** compose bounded RAG context from
   retrieved candidates while preserving evidence and conflict diagnostics.

The target reusable decision pattern remains:

```text
Embedding -> Semantic Retrieval/RAG -> Reasoning -> Structured Decision -> Runtime
```

Until Sprints 02–04 pass, callers must honestly use the current deterministic
foundation rather than claiming that target pattern is already available.

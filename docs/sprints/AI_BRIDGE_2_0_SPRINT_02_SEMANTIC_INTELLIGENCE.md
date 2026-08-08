# Sprint 02 – Semantic Intelligence

Status: PASS — READY FOR PRODUCT OWNER REVIEW. Product Owner Factory
Development Mode authority is the implementation authority for AI Bridge
self-development on `main`.

## Scope

Embedding infrastructure, persistent local vector storage, semantic search and
candidate ranking, RAG retrieval, Context Builder v2, retrieval evidence and
AKB knowledge retrieval. The implementation is additive and reads only
governed, active AKB knowledge after approval.

## Invariants

The Semantic Layer SHALL return ranked candidates only. It makes no business
decision, owns no Runtime transition, and performs no execution. Runtime never
generates embeddings. The Context Builder is the only Semantic component that
formats LLM context.

## Acceptance

An approved AKB entry indexes with a deterministic, versioned cache identity;
unchanged content is a cache hit. A semantic query returns project-isolated,
metadata-filtered, score-ordered candidates with evidence. Context assembly
honours a supplied token budget and preserves retrieval evidence.

## Required gates

Ruff, repository-wide mypy, Django check, migration plan, scope validation,
unit/integration/factory acceptance, full regression, documentation and fresh
evidence must pass before closure.

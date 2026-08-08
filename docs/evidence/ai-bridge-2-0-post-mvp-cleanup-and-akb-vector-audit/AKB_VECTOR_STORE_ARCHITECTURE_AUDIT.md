# AKB / Vector Store Architecture Audit

## Evidence basis

This report is derived from `projects/models.py`, migrations `0062`/`0063`,
`projects/knowledge_pipeline.py`, and `projects/semantic/intelligence.py`.
The Vector Store is not an external database: `DjangoVectorStore` persists
`SemanticEmbedding` rows in the same Django database as the AKB.

## Canonical data flow

```text
RuntimeKnowledgeCandidate.v1
 -> KnowledgePipeline validation / normalization / deduplication
 -> KnowledgeEntry (candidate or active after approval)
 -> DjangoVectorStore.index_project
 -> SemanticEmbedding
 -> DjangoVectorStore.search (ACTIVE entries only)
 -> KnowledgeContextPackage
```

`KnowledgeEntry` is the canonical source of truth. `SemanticEmbedding` is a
derived, regenerable retrieval index and is never authoritative for knowledge
content, approval, or lifecycle.

## Repository / Django fields

`KnowledgeEntry` persists the content (`title`, `content`), identity
(`entry_key`, `scope`, `knowledge_type`), project relation, source/provenance
(`source_type`, `source_reference`, `source_version`, `evidence_references`),
lifecycle (`status`, verification/freshness, timestamps, owner), governance
(`approval_reference`, precedence/conflict fields), and version number.
`KnowledgeRevision` persists each entry relation, old/new versions, actor,
approval/source references, reason, content snapshot and metadata snapshot.
`GovernanceApproval` persists approval reference, project/scope relations,
action, actor, and revoke state. `KnowledgePipelineReceipt` relates the source
Runtime candidate to its entry, optional embedding/context package, fingerprint,
classification, normalization, status and audit trail.

## Vector Store fields

`SemanticEmbedding` persists `entry` (FK), `embedding_id`, `provider`,
`model`, `source_version`, `content_hash`, numeric `vector`, JSON `metadata`,
and `indexed_at`. It does **not** persist original entry content or text chunks.
Metadata contains entry key, title, scope, knowledge type, verification and
freshness statuses, source reference and source version. It therefore
duplicates retrieval metadata and references the canonical content by entry ID.
There are no chunk IDs because the current implementation embeds one complete
KnowledgeEntry at a time.

## Synchronization lifecycle

On approved promotion, `KnowledgePipeline.process(..., APPROVE)` activates the
entry and calls `DjangoVectorStore.index_project` transactionally. Indexing
hashes `title + content`; unchanged provider/model/content hash rows are cached,
otherwise `update_or_create(entry, provider, model)` regenerates the vector.
Search filters relational entries to `ACTIVE` and project/global scope before
cosine ranking, so inactive entries are never returned.

## Risks and recommendations

1. Deactivation leaves an unused embedding row (search filters it out). Add a
   governed purge/reindex job with retention policy before large-scale use.
2. Entry edits outside KnowledgePipeline need an explicit reindex trigger;
   make all activation/content mutation paths emit an indexing-outbox record.
3. Global-entry vector identities include the indexing project while the unique
   row is `(entry, provider, model)`; define global identity independent of the
   caller project before multi-project scale.
4. Migrate legacy deterministic context consumers to the semantic context
   contract before removing the old context builder.

## Recommended final MVP architecture

Keep PostgreSQL/Django as the sole authoritative AKB and governance store. Keep
the vector representation as a derived index with entry IDs, hashes, provider
version and minimal retrieval metadata. Add an outbox-backed reindex/purge
lifecycle before replacing this local implementation with FAISS, pgvector,
Qdrant or Pinecone; Runtime callers remain unchanged because they use only the
semantic/knowledge public interfaces.

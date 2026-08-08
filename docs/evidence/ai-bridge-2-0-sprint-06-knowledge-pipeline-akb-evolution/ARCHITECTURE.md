# Architecture Evidence

## Canonical flow

```text
RuntimeKnowledgeCandidate.v1
  -> validate / normalize / declared-type classify / fingerprint
  -> deduplicate
  -> KnowledgeEntry(CANDIDATE) -> IN_REVIEW
  -> governed approval -> ACTIVE
  -> SemanticEmbedding -> vector index
  -> semantic retrieval -> KnowledgeContextPackage
```

The implementation is `projects.knowledge_pipeline.KnowledgePipeline` and the
durable processing record is `KnowledgePipelineReceipt` (migration 0062). It
reuses the existing AKB lifecycle, governance action, embedding provider and
`DjangoVectorStore`; it introduces no parallel knowledge lifecycle, vector
store or embedding provider.

## Boundaries verified

- The frozen Runtime produces the existing immutable candidate contract; it was
  not changed.
- Promotion is an explicit pipeline caller instruction and requires the
  existing `akb.review_candidate` approval reference. The Pipeline does not
  infer an approval or make a business decision.
- Embedding and indexing occur only after the AKB entry is active.
- `runtime_knowledge_compat.py` was neither modified nor used as the canonical
  pipeline path.
- Retrieval uses vector-ranked active entries and persists scored evidence in a
  `KnowledgeContextPackage`; it does not assemble LLM context.

See the maintained design and sequence diagram in
[Knowledge Pipeline and AKB Evolution](../../architecture/KNOWLEDGE_PIPELINE.md).

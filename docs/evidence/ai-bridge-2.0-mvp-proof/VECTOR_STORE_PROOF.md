# Vector Store Proof

## Result: PASS

The local vector-store boundary is `DjangoVectorStore`:

```text
ACTIVE KnowledgeEntry → content hash + source version → SemanticEmbedding → search
```

The Phase 10 test first indexes two eligible active entries and receives
`{indexed: 2, cached: 0, eligible: 2}`. It then deletes every project
`SemanticEmbedding`, confirms none remain, and calls `index_project` again.
The rebuild again returns `{indexed: 2, cached: 0, eligible: 2}`.

Regenerated embedding IDs equal baseline IDs because identity derives from the
project, entry, source version, provider and model version. This proves the
vector representation is a derived, replaceable implementation detail.

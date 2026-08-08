# Semantic Layer Proof

## Result: PASS

The semantic layer is provider-neutral and retrieval-only. Its local MVP
provider (`HashEmbeddingProvider`) deterministically tokenizes text into a
128-dimensional normalized vector. `DjangoVectorStore.search` scores active,
project-visible entries by cosine similarity and orders ties by entry ID.

For the fixed query **“How do we calculate shipping containers?”**, Phase 10
records candidate IDs, scores, rank, metadata and embedding evidence in a
baseline `KnowledgeContextPackage`. After deletion and rebuilding, it asserts
equality of `package_hash`, ordered `entry_ids`, complete retrieval payload and
ordered embedding IDs.

This is exact equality for the deterministic MVP provider. A future external
provider may permit numeric tolerance, but must retain equivalent retrieval.

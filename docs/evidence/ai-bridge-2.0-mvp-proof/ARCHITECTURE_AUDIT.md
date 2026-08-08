# Architecture Audit

## Result: PASS

The implementation preserves the required ownership boundaries.

| Concern | Canonical owner | Executable evidence |
| --- | --- | --- |
| Runtime state and immutable candidates | `projects/orki_runtime.py` | `test_structured_decision_runtime.py` |
| AKB lifecycle and revisions | `projects/knowledge.py`, `KnowledgeEntry` | knowledge-pipeline and semantic tests |
| Candidate validation, governance and promotion | `projects/knowledge_pipeline.py` | `test_knowledge_pipeline.py` |
| Embeddings, ranking and retrieval | `projects/semantic/intelligence.py` | `test_semantic_intelligence.py` |
| Cognitive experience and approved guidance | `projects/cognitive_evolution.py` | `test_cognitive_evolution.py` |

`KnowledgeEntry` and `KnowledgeRevision` are canonical governed records.
`SemanticEmbedding` holds an entry reference, content hash, source version,
metadata and vector; it does not own canonical knowledge content. The vector
store only indexes `ACTIVE` entries. The Runtime emits candidates but does not
write AKB, embeddings or vectors.

The Phase 10 test proves this boundary by deleting only derived embeddings and
context packages in an isolated test database, then recreating them solely by
indexing the unchanged active AKB entries.

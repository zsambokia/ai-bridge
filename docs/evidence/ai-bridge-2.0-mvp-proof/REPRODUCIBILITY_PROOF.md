# Reproducibility Proof — Phase 10

## Result: PASS

Executable proof:
`projects/tests/test_semantic_intelligence.py::test_mvp_proof_semantic_layer_can_be_destroyed_and_reconstructed_from_akb`

The test uses an isolated Django test database and performs the prescribed
destructive operation only there.

| Phase | Recorded or asserted result |
| --- | --- |
| Baseline | Two active governed Container Calculator AKB entries indexed; query result, scores, rank, KCP payload and embedding IDs captured. |
| AKB snapshot | Entry ID/key/content/status/version/approval reference, revisions, and approval count captured. |
| Destruction | All project `SemanticEmbedding` and `KnowledgeContextPackage` rows deleted; both confirmed empty. |
| Integrity | AKB snapshot, revision snapshot and approval count exactly unchanged. |
| Cold reconstruction | `DjangoVectorStore.index_project(project)` recreated both embeddings from active AKB entries without Runtime or manual repair. |
| Repeat retrieval | Equal KCP hash, ordered entries, full payload, scores, ranking and embedding identities. |
| Runtime and cognitive validation | Before/after Runtime outputs match; both reflections support approved, identical guidance strategies. |

Reconstruction sequence:

```text
KnowledgeEntry (ACTIVE)
→ HashEmbeddingProvider.embed(title + content)
→ SemanticEmbedding
→ DjangoVectorStore.search
→ KnowledgeContextPackage
→ StructuredDecision DecisionEvidence
→ Runtime
```

> The AI Bridge Knowledge Base (AKB) is the single authoritative source of
> truth. The Semantic Layer, Vector Store and Semantic Embeddings are entirely
> derived artifacts and can be destroyed and reconstructed from the canonical
> Knowledge Base without changing Runtime behaviour.

# Knowledge Pipeline Proof

## Result: PASS

`projects/tests/test_knowledge_pipeline.py` proves:

```text
RuntimeKnowledgeCandidate
→ VALIDATED → IN_REVIEW
→ explicit GovernanceApproval
→ ACTIVE KnowledgeEntry → SemanticEmbedding → PROMOTED receipt
```

The suite verifies that unapproved promotion fails, duplicate intake does not
create a second AKB or vector mutation, the receipt is idempotent, and retrieval
persists a `KnowledgeContextPackage` with strategy `SEMANTIC_VECTOR`.

The MVP proof uses two governed `RUNBOOK` entries for the Container Calculator
scenario: capacity validation and volume/capacity rounding-up calculation.

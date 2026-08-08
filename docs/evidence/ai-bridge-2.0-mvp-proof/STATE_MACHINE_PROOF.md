# State Machine Proof

## Result: PASS

`projects/tests/test_structured_decision_runtime.py` proves the canonical
StructuredDecision Runtime lifecycle:

```text
READY → RUNNING → VERIFYING → REFLECTING → KNOWLEDGE_CANDIDATE → COMPLETED
```

It also proves the recoverable path `FAILED → RETRYING`. A successful execution
records Goal, planning, provider, task, verification, reflection, candidate and
completion events. It produces immutable Runtime candidates and no
`KnowledgeEntry` mutation.

The Phase 10 proof executes this same lifecycle before and after rebuilding the
semantic layer and compares reflection text, verification result and emitted
knowledge-candidate content.

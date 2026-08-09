# Orki Context Package Flow — Discovery Audit

**Status:** canonical lifecycle mapping and target integration rule.

```text
approved active KnowledgeEntry
-> SemanticEmbedding index
-> semantic ranking/filtering/budgeting
-> KnowledgeContextPackage (package ID + hash + provenance)
-> persisted reference supplied at Runtime boundary
-> runtime execution evidence / response
```

## Inputs and selection

| Context source | Current treatment | Target Workspace treatment |
| --- | --- | --- |
| Constitution, architecture, roadmap | Repository/bootstrap knowledge candidates | source/provenance view. |
| Project facts, decisions, workflow knowledge | governed `KnowledgeEntry` after review | package members and freshness/conflict view. |
| Previous decisions, meetings | only when represented as governed knowledge | do not invent transcript memory. |
| Semantic results | active, project-scoped embeddings; rank/filter/budget | show selection evidence and exclusions. |
| Cognitive State | canonical conversation state, separate from transcript | show as working context, not silently merge with AKB. |

## Lifecycle requirements

1. Pipeline validates, normalizes, fingerprints and deduplicates candidates.
2. Governance promotes the candidate; only active entries can be indexed.
3. Semantic retrieval creates/persists a project-bound Context Package.
4. A Runtime consumer receives an explicit persisted package/reference and
   records it in its evidence.
5. Reflection creates a candidate only; the pipeline owns review, activation
   and index refresh.

`KnowledgeContextPackage` is a retrieval artifact, not a general LLM prompt
formatter or a client-side cache. The audit found a future integration gap:
the Workspace needs an explicit package-to-Runtime reference in the canonical
execution request/projection; it must not bridge this by direct AKB queries.

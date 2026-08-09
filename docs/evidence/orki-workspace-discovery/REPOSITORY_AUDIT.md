# Repository Lifecycle Audit

## Observed lifecycle

```text
Project Registry / provider preparation
-> repository snapshot (identity, branch, commit, documents)
-> classified source candidates
-> governed KnowledgeEntry review/activation
-> SemanticEmbedding index
-> semantic retrieval / KnowledgeContextPackage
-> Runtime consumes persisted context through its boundary
```

`RepositoryBootstrapLifecycle` documents a create/import convergence path and
an incremental-sync rule: process changed documents, stale prior source versions,
promote approved replacements and index only changed entries. This is the
correct foundation for Workspace Repository and Knowledge views.

## Current capability and limits

| Need | Result |
| --- | --- |
| Bootstrap/create and import convergence | Present in lifecycle service/tests. |
| GitHub provider proof | Evidence endpoint/test support exists; provider is not a general UI API. |
| Incremental semantic rebuild | Present for changed source entries. |
| Context regeneration | Retrieval creates persisted Context Package. |
| Workspace lifecycle visibility | Missing; only evidence/backend surfaces exist. |
| Clone/history/diff/webhook provider | Not established by the current adapter; explicitly future port work. |

## Required Workspace projection

Expose repository identity, last snapshot, source freshness, candidate/review
counts, embedding/index state, latest package ID/hash and readiness reason.
Never perform Git/subprocess/network work from the browser or Orki Runtime.

**Executable evidence seam:** `projects/tests/test_repository_lifecycle.py`
tests create/import convergence and changed-document-only incremental sync.

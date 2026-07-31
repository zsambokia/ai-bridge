# Sprint 3 engineering acceptance evidence

## Delivered capability

`KnowledgeContextPackage` and `KnowledgeContextUse` make retrieval and actual
consumption durable. Every context-bound Orki execution has a deterministic
package hash and records entry IDs, source versions, retrieval intent/query,
stale warnings, conflict warnings, and session/decision/contract/run consumers.

`RoadmapItem` and `RoadmapUpdateCandidate` establish project-scoped canonical
roadmap state. Evidence arrival produces a candidate; a valid project-bound
approval is required to apply it. A `COMPLETED` change requires both acceptance
statuses to be `PASS` and a 40-character commit SHA.

## Regression coverage

The new focused tests cover:

- Session A product-decision activation and Session B reuse without re-asking;
- cross-project retrieval isolation;
- deterministic conflict selection and stale-source warnings;
- MCP package persistence and consumption bindings;
- candidate-only roadmap updates and approval-gated completion;
- Admin registration; and
- the real remote MCP lifecycle binding through the queued execution run.

Final repository-wide Release Gate output is recorded in
[`RELEASE_GATES.md`](RELEASE_GATES.md).

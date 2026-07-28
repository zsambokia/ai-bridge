# Sprint 1 gap matrix

| Requirement | Result | Evidence / disposition |
| --- | --- | --- |
| Structured, scoped AKB and metadata filtering | PASS | `KnowledgeEntry`, `search` |
| Deterministic context package with source IDs/hash/staleness | PASS | `context_package`, `OrchestrationSession` |
| Candidate → review → approval → active | PASS | `review_candidate` and tests |
| Incident closed → candidate, no auto-activation | PASS | `close_incident` and tests |
| Governed MCP author/retrieve/review operations | PASS | `akb.*` tool handlers |
| Repository/service/dependency graph | GAP | Deferred; no entity/edge model |
| Semantic/vector indexing | GAP | Deferred; bounded lexical scan only |
| Sprint/remediation/validation/test/release/rollback learning | GAP | Deferred; only incident close writer |
| Full engineering lifecycle Orchestrator use | GAP | Current use is prompt/context package only |
| Automatic stale/archive governance | GAP | Metadata/status available; no worker/transition |

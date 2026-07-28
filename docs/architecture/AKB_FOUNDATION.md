# Application Knowledge Base foundation

Sprint 1 establishes the first durable, governed AKB layer for AI Bridge. It
does not introduce vector search, autonomous learning, deployment knowledge,
or a replacement governance lifecycle.

## Data and lifecycle

`KnowledgeEntry` is a Platform or Project scoped knowledge object. It carries
an explicit type, source and evidence references, work and role context,
verification/freshness metadata, owner role, version, timestamps, review date,
and a durable approval reference. `KnowledgeRevision` is append-only history
containing the content and metadata snapshot for every mutation.

Writing creates or updates only a `CANDIDATE`. Review may move it to
`IN_REVIEW` or `REJECTED`; only an unrevoked, project-bound
`GovernanceApproval` for `akb.review_candidate` (or the explicit AKB publish
authority) moves it to `ACTIVE`. An active entry cannot be overwritten through
the candidate upsert route. Stale review dates produce a stale warning in the
context package.

## Retrieval and orchestration

The governed MCP surface exposes `akb.search`, `akb.get_entry`,
`akb.get_context_package`, candidate create/upsert, review, and review-queue
operations. Search is bounded, project-isolated, and metadata-filtered; it is
not semantic/vector retrieval.

The Orchestrator builds a deterministic Context Package for every assessment.
It includes active platform/project must-know entries plus matching work/role
entries, source identifiers, source version/freshness/evidence metadata, and
a SHA-256 hash. The session persists the selected IDs and hash before provider
assessment. Providers therefore receive context that is attributable to a
specific AKB package, while raw repository contents and secrets remain
excluded.

## Event-driven input

Closing an incident creates or revises an `INCIDENT_LESSON` candidate with its
bounded evidence references. It never activates the lesson automatically.
Sprint closure, remediation, validation, test, release, deployment, and
rollback events have no automatic AKB writer in this Sprint.

Every AKB MCP read/write receives the existing append-only `McpAuditEvent`.
Its details include operation, context identifiers, non-content input
reference, approval reference, modified entry ID, package hash where relevant,
and outcome.

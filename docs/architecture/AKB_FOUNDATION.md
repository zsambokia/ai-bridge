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

## Sprint 2 engineering-memory extension

Sprint 2 adds a separate, normalized engineering-memory graph alongside the
generic `KnowledgeEntry` layer. `EngineeringEntity` is project-isolated and
holds a stable entity key, type, state, evidence/source references, structured
attributes, durable approval reference, version, and timestamps.
`EngineeringEntityRevision` is append-only. `EngineeringRelationship` creates
typed, evidenced relations only within the same Project.

The implemented entity types cover application, capability, feature,
component, service, API, integration, roadmap item, Constitution section, UI
plan, system design, architecture decision, Sprint, release, engineering gate,
remediation, incident, known issue, and runbook. The dedicated Roadmap,
Constitution, UI Plan, and System Design adapters require their defined
structured fields before a candidate is accepted. A candidate remains
non-active until a project-bound Product Owner approval activates it; event
ingestion and MCP authoring cannot bypass that boundary.

The governed MCP surface adds `engineering.search`, `engineering.get_entity`,
`engineering.link`, `engineering.impact`, and `engineering.plan`, plus
first-class `roadmap`, `constitution`, `ui_plan`, and `system_design` search
and candidate-authoring adapters. Search is project-isolated; role profiles
only affect result ordering and never authorization. Planning analysis reports
missing capabilities, missing dependencies, and duplicated GitHub references
from active Roadmap objects.

## Event-driven input

Closing an incident creates or revises an `INCIDENT_LESSON` candidate with its
bounded evidence references. It never activates the lesson automatically.
Sprint completion, gate results, remediation completion, incident resolution,
and release completion now also create retry-safe engineering-memory
candidates. The implementation intentionally does not claim deployment or
rollback ingestion because those lifecycle events are not yet emitted by the
current deployment subsystem.

Every AKB MCP read/write receives the existing append-only `McpAuditEvent`.
Its details include operation, context identifiers, non-content input
reference, approval reference, modified entry ID, package hash where relevant,
and outcome.

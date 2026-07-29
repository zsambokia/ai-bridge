# Governed engineering memory

Sprint 2 extends the AKB with a normalized, project-isolated engineering
graph. It is an additive layer: `KnowledgeEntry` remains the generic,
context-package knowledge store, while `EngineeringEntity` stores the
structured objects used for engineering planning and architecture retrieval.

## Model and governance

Each entity has a stable project-local key, kind, version, state, source and
evidence references, structured attributes, and approval reference. Every
create, candidate revision, and activation records an append-only
`EngineeringEntityRevision` snapshot. Active entities cannot be revised by
the candidate route. A candidate can become active only through
`engineering.review_candidate` and a project-bound `GovernanceApproval`.

Typed `EngineeringRelationship` edges are unique per Project/source/target/type
and retain work and evidence references. Cross-project and self-relations are
rejected by the domain service.

## First-class objects

`ROADMAP_ITEM`, `CONSTITUTION_SECTION`, `UI_PLAN`, and `SYSTEM_DESIGN` are
first-class types with dedicated MCP adapters. Their structured attributes are
validated before candidate creation. The Roadmap model includes hierarchy,
group, horizon, status, priority, dependencies, application/feature targets,
outcome, acceptance criteria, risk, and GitHub references. Constitution
sections include identifier, effective date, and status; historical versions
are represented by append-only revisions. `engineering.history` exposes their
provenance metadata and `constitution.diff` compares two immutable section
snapshots. UI plans and system designs carry the bounded fields described in
the Sprint 2 specification.

## Retrieval and lifecycle ingestion

`engineering.search` retrieves active entities only by default; role profiles
may rank entity kinds but cannot alter access. `engineering.impact` returns
the project-isolated one-hop graph. `engineering.plan` calculates missing
capabilities, unresolved roadmap prerequisites, and duplicate GitHub links
from active objects.

Sprint completion, gate result, remediation completion, incident resolution,
and release completion write idempotent candidates. They never automatically
activate knowledge. The current deployment subsystem has no emitted deployment
or rollback event, so those are explicitly not represented as implemented
ingestion paths.

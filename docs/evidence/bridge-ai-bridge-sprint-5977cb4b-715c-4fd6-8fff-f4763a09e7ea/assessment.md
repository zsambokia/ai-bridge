# AKB architecture assessment — Sprint 1

## Executive summary

**Final rating: PARTIALLY READY.** The AKB is now a durable and governed
knowledge foundation for bounded Engineering Orchestrator context. It is not
yet the primary knowledge layer for the complete engineering lifecycle: it has
no repository/component/dependency graph, semantic index, release/deployment
knowledge, or automatic learning from remediation/validation/release events.

Assessment scope: `bridge:ai-bridge:sprint:5977cb4b-715c-4fd6-8fff-f4763a09e7ea`.
Contract: `bridge:ai-bridge:contract:87bcd547-56ab-4e63-a052-30675b1117f1`.
Only implemented code is rated as present.

## Implemented architecture

`KnowledgeEntry` and append-only `KnowledgeRevision` are durable Django
models. `projects.knowledge` owns lifecycle, isolation, filtering, and the
deterministic Context Package. `projects.governed_mcp` exposes bounded AKB
tools and writes the existing append-only `McpAuditEvent`. `projects.orchestrator`
adds the package to provider context and persists its hash/selected entry IDs
on `OrchestrationSession`. `projects.incidents.close_incident` creates an
`INCIDENT_LESSON` candidate, never active knowledge.

Storage is the configured relational Django database. Search is a bounded,
case-insensitive title/content scan with deterministic ordering and metadata
filters; there is no vector/embedding index or background indexing worker.

## Knowledge model

| Element | State | Evidence |
| --- | --- | --- |
| Platform/project knowledge | Implemented | `KnowledgeEntry.scope` |
| Structured types: Constitution, Roadmap, UI Plan, System Design | Implemented | `ALLOWED_TYPES` |
| Incident lesson and evidence references | Implemented | `close_incident`, `evidence_references` |
| Policy, runbook, architecture decision | Implemented as generic typed entries | `ALLOWED_TYPES` |
| Repository, component, service, dependency | Not implemented as AKB entities | no AKB model/edge |
| Issue, sprint, commit, test, release, deployment, rollback | Not implemented as AKB entities | no AKB model/event writer |

## Relationship model

The current graph is shallow and attribute-based:

```text
Platform/Project --owns--> KnowledgeEntry --has--> KnowledgeRevision
KnowledgeEntry --references--> source/evidence/work/role identifiers
FailureIncident --close--> INCIDENT_LESSON candidate --approved review--> Active entry
OrchestrationSession --records--> Context Package hash + selected entry IDs
```

There are no durable edges for Repository→Component→Service→Incident,
Incident→Evidence is relational outside AKB, nor Sprint→Commit→Test→Release
→Deployment→Rollback. Architecture Decision→Component and Policy→Authority
are represented only as typed documents, not graph relationships.

## Context and Orchestrator use

Platform and Project context IDs are stored on entries; Work and Role context
are stored as fields and filter/selectors. `context_package` selects active
platform/project must-know entries plus work/role matches, returns source IDs,
freshness warning, and SHA-256 hash. Orchestrator prompt/context construction:
**PASS**. Repository selection, incident analysis, ownership, remediation,
validation, deployment, release, architecture review, and code review:
**NOT USED** by AKB, except incident closure contributes a candidate (**PARTIAL**).

## Lifecycle, quality, and learning

Version, timestamps, revisions, source/evidence references, verification,
freshness/review-due warning, owner, and approval reference are implemented.
Archiving/superseding status values exist but no transition services automate
them. Duplicate prevention is an entry key plus identity constraint; no
deduplication/merge process exists. Auditability is good for MCP operations
but not for direct internal service calls.

Learning is partial only: closed incidents create candidates. Sprint closure,
RCA beyond incident data, remediation, validation, test result, release, and
rollback ingestion are absent. Missing pieces are event contracts, writers,
entity/edge model, evidence provenance verification, review queues/workflows
for these sources, and freshness/retention automation.

## Risks and evolution

Short term: add lifecycle event adapters for remediation/validation/test/release
and stale/archival jobs; make internal writes auditable. Medium term: introduce
typed repository/component/service/release/deployment entities and explicit
edges, plus evidence provenance and review ownership. Long term: use a
relational source of truth with a graph projection and hybrid lexical/vector
retrieval, revisioned packages, policy-aware authority edges, and governed
event ingestion. No automatic publication should bypass review/approval.

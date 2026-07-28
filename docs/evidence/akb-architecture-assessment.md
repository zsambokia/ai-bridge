# Application Knowledge Base (AKB) architecture assessment

## Executive summary

**Final rating: `PARTIALLY READY`.** As delivered by Sprint 1, AKB is a
durable, approval-governed source of bounded context for the Engineering
Orchestrator. It is not yet capable of acting as the Engineering
Orchestrator's primary knowledge layer across the engineering lifecycle.

This assessment evaluates only implemented behavior in the repository at the
Sprint 1 evidence baseline. It does not credit planned capabilities.

| Assessment area | Result |
| --- | --- |
| Durable knowledge, provenance, and reviewed publication | Implemented |
| Deterministic Platform, Project, Work, and Role context package | Implemented |
| Orchestrator prompt/context construction | PASS |
| Engineering entity graph and lifecycle-event knowledge | Not implemented |
| Semantic/hybrid retrieval and automatic indexing | Not implemented |
| Automatic learning beyond closed-incident candidate creation | Partial |

The detailed test- and source-linked assessment is in
[`assessment.md`](bridge-ai-bridge-sprint-5977cb4b-715c-4fd6-8fff-f4763a09e7ea/assessment.md);
the gap matrix, migration plan, and security review are adjacent evidence.

## Current architecture

The relational Django database stores `KnowledgeEntry` records and append-only
`KnowledgeRevision` snapshots. `projects.knowledge` validates candidates,
enforces isolation, controls review/publication, searches active entries, and
constructs a deterministic Context Package. `projects.governed_mcp` exposes
the governed AKB interface and records MCP audit events. The Orchestrator adds
the package to provider context and persists the package hash and selected
entry IDs on `OrchestrationSession`.

```text
Governed MCP --> projects.knowledge --> KnowledgeEntry --> KnowledgeRevision
                         |                    |
                         |                    +--> source/evidence/work/role IDs
                         v
                 deterministic Context Package --> Orchestrator provider context

FailureIncident --close--> reviewable INCIDENT_LESSON candidate
```

Storage is relational. Search is bounded, case-insensitive lexical matching
over title/content with metadata filters and deterministic ordering. There is
no vector index, embedding generation, queue, or background indexing worker.

## Knowledge model and relationships

| Knowledge element | Status | Implemented representation |
| --- | --- | --- |
| Platform and project knowledge | Implemented | `KnowledgeEntry.scope` |
| Constitution, roadmap, UI plan, system design | Implemented | Typed entries |
| Policy, runbook, ADR | Implemented as documents | Typed entries, no typed edges |
| Incident lesson and evidence references | Implemented | Candidate created by incident close; identifier list |
| Repository/component/service/dependency | Not implemented | No AKB entities or edges |
| Issue/sprint/commit/test | Not implemented | No AKB entities or event writers |
| Release/deployment/rollback | Not implemented | No AKB entities or event writers |

Implemented relationships are entry ownership, revision history, and reference
attributes. The requested Repository -> Component -> Service -> Incident and
Sprint -> Commit -> Test -> Release -> Deployment -> Rollback graphs do not
exist. `Incident -> Evidence` exists in the incident domain, but is only copied
into AKB as evidence-reference strings. ADR -> Component and Policy ->
Authority are documents rather than navigable governance relationships.

## Context and Orchestrator integration

Platform and Project IDs are persisted on entries. Work context and role
context are persisted as an ID and JSON role list. `context_package` selects
active Platform/Project must-know entries plus matching Work/Role entries,
includes freshness warnings, and returns a SHA-256 package hash.

| Orchestrator use | Result |
| --- | --- |
| Prompt/context assembly | PASS |
| Repository selection | NOT USED |
| Incident analysis and ownership | NOT USED |
| Remediation and validation | NOT USED |
| Deployment and release | NOT USED |
| Architecture/code review | NOT USED |
| Incident closure learning input | PARTIAL |

## Lifecycle, quality, and self-learning

Version, timestamps, revision snapshots, source/evidence references,
verification/freshness fields, owner, and approval reference are implemented.
Archive, stale, superseded, and review-due statuses are declared, but no
automation transitions records into those states. Entry keys and an identity
constraint reduce duplicates; no merge/deduplication workflow exists.

Only incident closure has an implemented learning hook, and it produces a
reviewable candidate rather than automatically active knowledge. There are no
event contracts or writers for sprint closure, RCA, remediation, validation,
test results, releases, deployments, or rollbacks. Required missing pieces
include those event adapters, evidence verification, review ownership, typed
entities/edges, lifecycle jobs, and governed publication policies.

## Risks and recommended evolution

Short term: make internal writers auditable; add explicit lifecycle event
adapters for remediation, validation, test, release, deployment, and rollback;
and add stale/archive processing. Medium term: add typed repository, component,
service, dependency, release, deployment, and evidence models with explicit
relations and review ownership. Long term: retain relational source-of-truth,
project a governed graph, and add hybrid lexical/vector retrieval with
revisioned, policy-aware context packages.

No recommendation in this assessment asserts that a capability already exists.
The evidence contains the exact sources and verification commands supporting
each conclusion.

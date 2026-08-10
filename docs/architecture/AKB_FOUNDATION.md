---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Application Knowledge Base foundation

## Orki Cognitive Operating System integration

The approved Orki Cognitive Operating System Epic establishes evolutionary
knowledge as a governed platform capability. Conversation transcripts are not
Application Knowledge Base entries. Future Cognitive State and memory work must
create attributable, confidence-scored, correctable, reusable knowledge that
remains subject to the existing governance and evidence lifecycle.

The design boundary and phased implementation sequence are recorded in
[`ORKI_COGNITIVE_OPERATING_SYSTEM.md`](ORKI_COGNITIVE_OPERATING_SYSTEM.md) and
the associated ADRs. ORKI-001 implements project-scoped Cognitive State
persistence with provenance, confidence, correction history, and a
deterministic projection. It is working memory, not an accepted AKB entry:
it cannot publish, approve, or overwrite governed knowledge. The completed
ORKI-001 Cognitive State Release Gate additionally proves this boundary across
a 25-turn Factory Chat conversation, including source evidence, state
evolution, and project isolation. Its evidence is recorded in
[`COGNITIVE_STATE_RELEASE_GATE.md`](../evidence/sprint-orki-001-cognitive-state-foundation-20260801/COGNITIVE_STATE_RELEASE_GATE.md).

ORKI-008 and ORKI-009 extend this working-memory boundary with a separate,
project-scoped Product Owner operational working model. Its evidence weighting,
confidence explanation, revision history and cognitive-drift projection are
Cognitive State metadata, not reusable AKB knowledge. They cannot publish,
approve, transfer across projects, or alter the governed AKB lifecycle. The
model exposes only bounded provenance identifiers and never transcript content.

Sprint 1 does not introduce vector search, autonomous learning, deployment
knowledge, cross-project reuse, or a replacement governance lifecycle. Those
capabilities require their own evidence and acceptance in later Sprints.

## Sprint 3 durable feedback loop

Sprint 3 makes a retrieved AKB package a durable, attributable runtime object,
rather than an ephemeral result. `KnowledgeContextPackage` persists its
deterministic hash, selected entry IDs, source versions, query and intent,
stale-source warnings, conflict warnings, and safe payload. `KnowledgeContextUse`
then binds that exact package to the Orki session and decision and, when one is
issued, to the execution contract and run. This distinguishes knowledge that
exists from knowledge actually retrieved and included in a concrete execution.

Retrieval remains project-scoped. Conflicts are selected deterministically by
explicit precedence, then source version, then entry key; non-winning entries
remain visible through conflict warnings. A source revision can mark prior
knowledge stale without erasing its audit trail. The MCP context-package tool
uses the same persistence and returns its durable ID and hash, and Django Admin
exposes read-only package and use projections.

Accepted delivery facts do not silently overwrite active knowledge or roadmap
state. The feedback-loop services create `RoadmapUpdateCandidate` records first;
only a project-bound governance approval can activate a candidate and update the
canonical `RoadmapItem`. Completion additionally requires both engineering and
operational PASS plus a full commit SHA. The resulting AKB fact is itself a
candidate, preserving governed review and an honest distinction between evidence
arrival and accepted project knowledge.

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

## Issue #17 Sprint 5 Factory Chat Memory Mode

Memory Mode is a server-owned projection over the canonical generic AKB
service. A query records the exact bounded context package used for the Factory
Chat work context; its sources, source versions, stale warnings, conflict
diagnostics, repository/roadmap/runtime projection, and package hash are
rendered without exposing a browser-to-provider channel. “LLM-ready” means
attributable context preparation for Orki/LLM work, not a new direct model
call, vector store, or semantic-retrieval claim.

Project-local candidates are moved only through the existing
`CANDIDATE → IN_REVIEW → ACTIVE` service lifecycle. Activation needs a
project-bound `akb.review_candidate` approval reference; rejection stays a
separate append-only revision. The service rejects a foreign project entry
before any state transition.

## External execution reconciliation knowledge

When Factory Development Mode or another external governed path has completed
implementation before Bridge can record a provider lifecycle, the canonical
knowledge is the verified evidence bundle, final commit, engineering audit,
and Product Owner acceptance reference. `ExternalExecutionReconciliation`
stores their digest and the durable `RECONCILING → PASS → ACCEPTED` transition
trail. It does not infer or synthesize provider history. The corresponding MCP
audit event gives later assessments an attributable completion fact while a
changed, missing, or cross-scope evidence input is rejected.

---
status: APPROVED_TARGET
owner: Architecture
supersedes: []
superseded_by: null
version: 0.1.0
canonical_language: en
authority: Architecture Convergence Program – Sprint 2
---

# AKB Architecture Constitution — Knowledge Objects and Knowledge Lifecycle Management

## Authority, status and interpretation

This is an approved target-architecture entry for the future Constitution
Book. It is subordinate to the canonical
[Bridge Constitution](../constitution/BRIDGE_CONSTITUTION.md) and the current
[Architecture Constitution](ARCHITECTURE_CONSTITUTION.md). It does not amend
either document, authorize an implementation, or assert compliance by the
current AKB implementation. Its adoption into the Constitution Book requires
the Book adoption process and the ADRs listed in the associated Sprint.

Normative text is English. Localized renderings are derived representations and
MUST preserve the meaning, identifier, version and provenance of this entry.

## Article I — Knowledge Object

### AKB-101 — Knowledge Object primacy

The Architectural Knowledge Base (AKB) SHALL store **Knowledge Objects**, not
documents as its primary unit. A document, Markdown file, ticket, class, YAML
file, embedding or graph record MAY represent a Knowledge Object, but none is
the object itself.

A Knowledge Object is the smallest independently identifiable, versioned and
referencable unit of governed knowledge in AI Bridge.

### AKB-102 — Uniform Knowledge Model

Every Knowledge Object SHALL conform to one uniform base model, irrespective of
its specialized type. Permitted specialized types include Requirement, ADR,
Decision, Workflow, Capability, Provider, Engine, Persona, Policy, Pattern,
Evidence, Lesson Learned, Glossary Term and Architecture Principle. The type
catalogue is governed; adding or retiring a type requires compatible lifecycle,
provenance and retrieval semantics.

Each object SHALL expose at least:

```yaml
id: knowledge://<type>/<stable-key>
type:
title:
summary:
status:
version:
owner:
created_at:
updated_at:
source:
confidence:
language:
tags:
relationships:
```

The `id` is stable across versions. A published content or metadata change
creates a new immutable version; it MUST NOT replace the prior published
version. The precise version identifier, content-addressing and representation
rules are reserved for ADR-030.

### AKB-103 — Lifecycle, identity and retention

Every Knowledge Object SHALL have an explicit lifecycle:

```text
DRAFT → REVIEW → APPROVED → DEPRECATED → ARCHIVED
```

Lifecycle transitions SHALL be attributable, authorized, versioned and
auditable. Deletion is not a normal lifecycle transition. Historical versions,
relationships and provenance remain retained according to the governed
retention policy.

Operational data is not a Knowledge Object merely because it contains useful
information. Logs, caches, sessions, execution state, temporary context, HTTP
requests, WebSocket messages and runtime variables remain operational records.
They MAY be evidence or inputs to knowledge publication only through the
Knowledge Lifecycle Management boundary.

### AKB-104 — Knowledge Graph

Knowledge Objects SHALL be organized primarily as a typed graph. Relationships
are first-class, typed, version-aware and evidenced. Tree structures, files,
indexes and document views are secondary representations.

For example, a Requirement may be implemented by a Workflow, which uses a
Capability, which is executed by an Engine. That relationship graph MUST be
queryable without treating the implementation representation as the governing
identity.

### AKB-105 — Knowledge Reference and Context Package

The AKB owns the Knowledge Object definition; a Context Package consumes an
immutable **Knowledge Reference**, not an unversioned copy of knowledge.
Every reference SHALL bind at least the stable object identity, selected
immutable version, source/provenance and selection evidence. This preserves
reuse, reproducibility and auditability when one object participates in more
than one Context Package.

Knowledge Reference is not a runtime instance and MUST NOT contain mutable
execution state. Context Package freshness, invalidation and stale-consumption
policy are governed by Article II and ADR-032.

## Article II — Knowledge Lifecycle Management

### AKB-201 — Independent architectural subsystem

Knowledge Lifecycle Management (KLM) SHALL be an independent architectural
subsystem. It is not part of the Runtime Engine, AKB storage domain or Provider
layer. It maintains evolving, searchable and reproducible knowledge through
controlled lifecycle operations rather than direct representation edits.

```text
Planning / Execution / Evidence / Decision / Domain Events
                         │
                         ▼
              Knowledge Lifecycle Management
        detect → plan → synchronize → publish → invalidate
                         │
                         ▼
        AKB graph / representations / searchable versions
```

### AKB-202 — Separated KLM responsibilities

KLM SHALL separate these responsibilities:

| Component | Sole responsibility | Required output/boundary |
| --- | --- | --- |
| Knowledge Change Detector | Detect and classify a knowledge-affecting event. | `KnowledgeChangeEvent`; MUST NOT modify knowledge. |
| Knowledge Update Planner | Determine affected objects, priority and required representations. | `KnowledgeUpdatePlan`. |
| Knowledge Synchronizer | Execute an approved update plan. | MUST NOT decide what needs update. |
| Knowledge Freshness Manager | Measure stale state, freshness and SLA conformance. | Detectable freshness state and synchronization trigger. |
| Knowledge Publisher | Atomically publish a new immutable AKB version. | Version, provenance, timestamp, source references and update evidence. |
| Context Invalidation Manager | Determine whether existing Context Packages remain valid. | Explicit invalidation or continued-validity evidence. |

### AKB-203 — Change classification and declarative policy

Every detected knowledge-affecting change SHALL belong to exactly one declared
category: `STRUCTURE_CHANGED`, `CONTENT_CHANGED`, `RUNTIME_KNOWLEDGE` or
`EXTERNAL_CHANGE`. The policy for graph updates, embeddings, summaries,
reflection, indexes, publication and invalidation SHALL be declarative,
versioned and auditable.

The physical synchronization of representations MAY be asynchronous, but their
logical consistency and their binding to the published Knowledge Object version
MUST remain verifiable.

### AKB-204 — Freshness, drift and synchronization modes

Knowledge freshness SHALL be measurable. Knowledge drift MAY exist temporarily
but SHALL be detectable, attributable and recoverable; it MUST NOT be silent.
Every stale object SHALL have a policy-defined convergence path to its current
source state.

Synchronization policy MAY select `IMMEDIATE`, `BACKGROUND`, `ON_DEMAND` or
`SCHEDULED` mode according to change category, criticality and freshness SLA.
An on-demand Context build that detects stale knowledge MUST either synchronize,
select a permitted immutable version, or fail/continue only under explicit
stale-consumption policy. It MUST NOT silently consume stale knowledge.

### AKB-205 — Publication and traceability

Knowledge becomes queryable as current knowledge only after successful
publication. Publication SHALL create an immutable version with provenance,
publication timestamp, source references and update evidence. Each published
version SHALL be traceable through its originating Knowledge Change Event and
Update Plan.

Direct changes to a published knowledge representation that bypass KLM are
forbidden. A representation repair or rebuild is a lifecycle operation and
MUST preserve the prior historical record.

## Architectural consequences

1. Existing `KnowledgeEntry`, `EngineeringEntity`, `KnowledgeRevision`,
   `KnowledgePipelineReceipt`, `KnowledgeContextPackage` and embedding records
   are not silently relabelled as full Knowledge Object compliance.
2. The existing governed candidate/review/active lifecycle remains authoritative
   until an approved migration maps it to the target lifecycle without losing
   audit history.
3. A VectorDB, document store or graph database is an implementation choice and
   never defines AKB architectural ownership.
4. Runtime can emit evidence-bearing candidates, but it neither publishes AKB
   knowledge nor owns KLM planning, synchronization or freshness decisions.

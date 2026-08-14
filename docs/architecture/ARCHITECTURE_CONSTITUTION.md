---
status: CANONICAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.1.0
---

# AI Bridge Architecture Constitution

> **Terminology status (2026-08-10):** Transitional. This document remains a
> governance source until Constitution Book adoption. The approved target
> terminology is governed by Article I–II (AKB), Article III (AI Kernel),
> Article IV (Conversation to Mission), Article V (Architecture Documentation
> Governance), Article VI (Scope Architecture),
> Article VII (Localization Architecture),
> and the Terminology Convergence Matrix; historical names are not
> implementation rename authority.

## Authority and interpretation

This is the normative architecture constitution for AI Bridge. It is subordinate
to the repository-wide [Bridge Constitution](../constitution/BRIDGE_CONSTITUTION.md)
and governs technical ownership, boundaries, and evolution. The
[Runtime 2.0 Constitution](../runtime/runtime_2_0_constitution.md) refines this
constitution for the Runtime target; neither document weakens the Bridge
Constitution.

Normative terms **SHALL**, **MUST NOT**, **SHOULD**, and **MAY** are binding.
Conflicts require a durable constitutional amendment or ADR; implementation
convenience is not an exception.

The Constitution Book entries linked below are adopted target authority. Older
architecture records and repository behaviour are historical evidence unless
compatible with this Constitution; they cannot silently countermand it.

## Architectural laws

1. Every business domain SHALL have one explicit owner. No component may write
   another domain's state or silently assume its authority.
2. The Mission State Machine (MSM) is the sole Mission lifecycle authority.
   Mission Resolution is the exclusive human-Conversation intake boundary; it
   may originate a Mission creation decision, but only the MSM validates and
   records Mission lifecycle state. The AI Kernel MUST NOT become a Planning,
   Workflow, Repository, Knowledge, or provider engine.
3. An Engine owns one bounded domain concern and its own state. Engines MUST NOT
   directly call one another, a Provider Integration adapter, a Provider, or
   `ExecutionRun`.
4. The Operational Foundation is the sole canonical mechanical handoff and
   delivery boundary. All provider-bound work reaches it only through an MSM
   authorized immutable Operational Work Item.
5. Execution Requests are immutable declarations of intent. Only the MSM may
   reject, defer, merge, transform, or authorize one as an Operational Work
   Item.
6. Domain state machines communicate only through durable, attributable
   requests, results, events, and evidence. Cross-domain writes are forbidden.
7. Provider output is untrusted input and never architecture, governance,
   Mission, or Product Owner authority.
8. Evidence, provenance, idempotency, recovery, and correlation are mandatory
   architectural properties of durable state transitions and work delivery.
9. A projection or UX persona, including Orki, MUST NOT create a second control
   path or authority boundary.
10. Historical terminology and implementations retain their historical meaning;
    migration claims require evidence and MUST NOT be inferred from this target
    constitution.
11. The Conversation State Engine (CSE) exclusively owns Conversation Domain
    progression. It is neither an MSM, an Operational Foundation component,
    nor an AI Kernel component, and it MUST NOT write another domain's state.

## Hierarchy

```text
Bridge Constitution
└── Architecture Constitution (this document)
    ├── Article I–II — AKB Knowledge Objects and Lifecycle
    ├── Article III — AI Kernel Architecture
    ├── Article IV — Conversation to Mission Architecture
    ├── Article V — Architecture Documentation Governance
    ├── Article VI — Scope Architecture
    ├── Article VII — Localization Architecture
    ├── Runtime 2.0 Constitution
    ├── Operational Foundation Constitution
    ├── Engine Constitution
    └── State Machine Constitution
```

The [Architecture Map](ARCHITECTURE_MAP.md) is the sole technical-architecture
entry point. The [Architecture Evolution](ARCHITECTURE_EVOLUTION.md) records
the relationship between current, transitional, and target material.

The approved target entries are [AKB Knowledge Object & Lifecycle
Constitution](AKB_KNOWLEDGE_OBJECT_AND_LIFECYCLE_CONSTITUTION.md), [AI Kernel
Architecture Constitution](AI_KERNEL_ARCHITECTURE_CONSTITUTION.md),
[Conversation to Mission Architecture Constitution](CONVERSATION_TO_MISSION_ARCHITECTURE_CONSTITUTION.md),
[Scope Architecture Constitution](SCOPE_ARCHITECTURE_CONSTITUTION.md), and
[Localization Architecture Constitution](LOCALIZATION_ARCHITECTURE_CONSTITUTION.md).
Together with [Factory Protocol Architecture Constitution](FACTORY_PROTOCOL_ARCHITECTURE_CONSTITUTION.md),
these entries are adopted Constitution Book authority.

## Article V — Architecture Documentation Governance

Architecture diagrams are not optional documentation; they are normative
architecture artifacts.

### ADG-101 — Canonical Diagrams

Canonical architecture diagrams SHALL be considered first-class architecture
artifacts. Architecture diagrams have the same normative authority as their
corresponding Architecture Constitution chapters. They SHALL describe the
approved target architecture rather than the current implementation.

The canonical logical form of an architecture diagram SHALL be Mermaid source
embedded in a version-controlled Markdown document. This logical source is the
reviewable, diffable, and auditable architecture-as-code representation.

### ADG-102 — Diagram Consistency

Every canonical architecture diagram SHALL remain consistent with the
Architecture Constitution. A conflict between a diagram and the Constitution
is an architecture defect and SHALL be corrected through the approved
Architecture Convergence process.

### ADG-103 — Mandatory Diagram Maintenance

An approved architectural change that affects structure, ownership,
responsibilities, boundaries, lifecycle, or interactions SHALL include
maintenance of every affected canonical diagram. The change SHALL NOT be
considered complete until the affected Constitution chapters and canonical
diagrams are updated, cross-references remain valid, and the documentation has
passed consistency review.

### ADG-104 — Diagram Impact Assessment

Every Architecture Decision Record (ADR) and every Architecture Convergence
change SHALL include a Diagram Impact Assessment. The assessment SHALL
identify affected diagrams, required modifications, newly required diagrams,
and obsolete diagrams. No architecture change may be closed without completing
this assessment.

### ADG-105 — Repository Rule

Every canonical diagram SHALL have one canonical source in the repository. For
the canonical diagram set governed by this Article, that source SHALL be the
version-controlled Markdown document containing Mermaid. Mermaid is the
authoritative logical model when any visual representation differs.

An editable `.drawio` file MAY be maintained as a derived visual architecture
artifact for teaching, presentation, or enriched visual explanation. It SHALL
preserve the Mermaid logical model and SHALL NOT independently introduce,
remove, rename, or reconnect logical architecture elements. Generated PNG,
SVG, and PDF files are derived artifacts only; they MAY be regenerated from
Mermaid or Draw.io at a documentation release, by CI, or when a consumer needs
them. Their regeneration is not required for every architecture-documentation
commit.

### ADG-106 — Completion Criteria

An Architecture Convergence task SHALL NOT be marked complete unless the
Constitution and all affected diagrams are updated, the canonical diagram set
is internally consistent, and the architecture documentation reflects the
approved design.

### Architecture Convergence working rule

The responsible executor SHALL identify every affected canonical Mermaid
source, update each impacted source and related `README.md`, assess and update
every affected derived `.drawio` representation, and report the result. If no
diagram source change is necessary, the executor SHALL state that conclusion
explicitly and preserve its justification in the Diagram Impact Assessment.

### ADG-107 — Architecture Status

Every canonical diagram SHALL declare an Architecture Status in its canonical
Mermaid source, repository documentation, and visible derived-diagram metadata
where a derived diagram exists. The allowed values
are `DRAFT`, `ASSESSMENT`, `APPROVED`, `CANONICAL`, `TRANSITIONAL`,
`HISTORICAL`, and `DEPRECATED`.

`CANONICAL` denotes the approved target architecture and has the normative
authority described by ADG-101. `TRANSITIONAL` denotes an explicitly bounded
route from the current implementation to that target. `HISTORICAL` records a
former or current implementation fact and SHALL NOT be interpreted as target
architecture. `DRAFT`, `ASSESSMENT`, and `APPROVED` communicate their review
stage; `DEPRECATED` identifies an artifact retained only until governed
retirement. A status label SHALL NOT be used to silently elevate an unresolved
implementation model to canonical architecture.

### ADG-108 â€” Diagram Governance Metadata

Every canonical Mermaid diagram document SHALL declare its diagram name,
Architecture Status, source type, derived Draw.io path when present,
Constitution reference, last-reviewed date, architecture version, and related
ADRs. This metadata makes source hierarchy, review status, and governance
binding explicit without duplicating the logical model.

## Article VIII — Architecture and Implementation Convergence

The [Architecture and Implementation Convergence
Governance](ARCHITECTURE_IMPLEMENTATION_CONVERGENCE_GOVERNANCE.md) is a
normative Constitution Book governance entry. Architecture Convergence defines
the approved target architecture; Implementation Convergence realizes it in the
repository and runtime. Implementation evidence may raise an Architecture
Challenge, but it MUST NOT silently redefine the canonical architecture.

Until MVP architecture stabilization, compatibility with development-stage
implementation is not a default architectural requirement. Approved target
architecture takes precedence unless the Product Owner explicitly approves a
bounded compatibility exception.

## Change control

Architecture changes SHALL identify the affected owner, boundary, state
machine, evidence obligation, compatibility effect, and migration state.
An ADR records a durable decision; it does not by itself certify that code is
implemented or compliant.

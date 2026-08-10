---
status: APPROVED TARGET
owner: Architecture
classification: CANONICAL ARCHITECTURE GOVERNANCE
language: en
version: 1.0.0
---

# Architecture and Implementation Convergence Governance

## Purpose

AI Bridge maintains two governed, mutually accountable programs. This document
defines their authority boundary. It is the canonical governance source for
convergence-program responsibility; it does not authorize implementation.

## AGC-001 — Program separation

**Architecture Convergence defines and maintains the approved AI Bridge target
architecture. Implementation Convergence aligns the repository and runtime
with that approved architecture. Implementation evidence may challenge
architecture, but implementation work SHALL NOT silently redefine canonical
architecture. Material architectural changes return through the Architecture
Challenge and Product Owner decision process before implementation continues.**

| Program | Question it answers | Owns |
| --- | --- | --- |
| Architecture Convergence Program | What SHALL AI Bridge be? | Constitution Book, canonical concepts, invariants, ownership/responsibility boundaries, target diagrams, ADRs, Architecture Challenges, Product Owner architecture decisions, terminology and architecture evolution. |
| Implementation Convergence Program | How does the repository reach the approved target? | Repository assessments, gaps, migration and dependency plans, implementation contracts and Sprints, implementation, tests, runtime verification, evidence, measurements and closure reports. |

Architecture Convergence SHALL evaluate the correct from-zero design before it
uses repository constraints to plan its realization. Implementation Convergence
is authoritative only for realization choices that do not change an approved
architectural meaning, owner, boundary or invariant.

## AGC-002 — Architecture Challenge Gate

An Implementation Convergence task SHALL open an Architecture Challenge when
evidence shows that an approved concept cannot cleanly meet its responsibility,
ownership boundaries conflict, an invariant has unacceptable consequences,
canonical concepts overlap, a materially simpler design exists, or an approved
architectural assumption is disproved.

Every Challenge SHALL record the approved architecture, repository or runtime
evidence, problem, consequence, alternatives, recommendation and expected
impact. The Architecture Convergence Program assesses it. A material outcome
requires a Product Owner decision and a corresponding canonical Constitution
and/or ADR update before implementation resumes on the changed premise.

Evidence informs Architecture; implementation does not govern Architecture.

## AGC-003 — Pre-MVP compatibility

Until MVP architecture stabilization is expressly declared, compatibility with
development-stage models, APIs, persistence, terminology, data or runtime
abstractions SHALL NOT be an architectural requirement by default. The approved
target architecture takes precedence. A compatibility adapter, alias,
projection, dual-read/write path or strangler route requires an explicit,
bounded Product Owner-approved exception with owner, expiry and removal
evidence. This rule does not authorize destructive operations; those remain
subject to an approved implementation scope.

## AGC-004 — Artifact authority and historical preservation

`CANONICAL ARCHITECTURE` describes the currently approved target. `HISTORICAL
CONVERGENCE EVIDENCE` records a past repository state, assessed gaps, options
or migration plan. Historical material remains auditable but SHALL NOT acquire
authority merely by remaining in the repository.

Phase 2 is an Implementation Convergence assessment snapshot. Phase 2.5 is a
historical mixed decision-preparation record: its Challenge Register, Product
Owner Decision Pack and accepted canonical decisions are Architecture
Convergence artifacts; its current-vs-target evidence, migration strategy and
Phase 3 implementation contract are Implementation Convergence artifacts. The
records remain in place for traceability and point here for authority.

## AGC-005 — ADR and Product Owner governance

ADRs are Architecture Convergence records. A Product Owner decision is required
when an ADR creates, changes or retires a canonical concept, owner,
responsibility boundary, invariant, lifecycle, scope rule, security guarantee
or compatibility exception. Implementation-only realization choices SHALL be
recorded in the applicable implementation contract or Sprint evidence rather
than presented as a canonical ADR change. An ADR may document a non-material
clarification, but it SHALL NOT claim Product Owner approval that was not given.

## AGC-006 — Lifecycle and re-entry rule

```text
Problem / Goal
      ↓
Understanding
      ↓
Architecture Convergence
      ↓
Architecture Challenge (when required)
      ↓
Product Owner Decision
      ↓
Approved Canonical Architecture
      ↓
Implementation Convergence → Assessment → Plan → Approval → Implementation
      ↓
Verification → Evidence → Knowledge Update
```

Architecture Convergence has explicit lifecycle states: `UNDERSTANDING`,
`PROPOSED`, `CHALLENGED`, `PENDING PRODUCT OWNER DECISION`, `APPROVED TARGET`,
and `SUPERSEDED`. It is re-entered only for a material architectural question
or Challenge. Implementation work already governed by an approved target does
not require a new architecture cycle.

## Documentation organization

The current responsibility-oriented directories and explicit canonical pointers
are simpler and safer than a cosmetic directory migration. Future organization
MAY add canonical and decision indexes, but it SHALL preserve stable links and
historical evidence. The [Architecture index](README.md) is the entry point;
the [Architecture Constitution](ARCHITECTURE_CONSTITUTION.md) and its approved
Book entries define the target architecture.

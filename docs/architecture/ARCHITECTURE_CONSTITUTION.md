---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: Constitution Book (planned adoption)
version: 1.0.0
---

# AI Bridge Architecture Constitution

> **Terminology status (2026-08-10):** Transitional. This document remains a
> governance source until Constitution Book adoption. The approved target
> terminology is governed by Article I (AKB), Article III (AI Kernel) and the
> Terminology Convergence Matrix; historical names are not implementation
> rename authority.

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

## Architectural laws

1. Every business domain SHALL have one explicit owner. No component may write
   another domain's state or silently assume its authority.
2. The Mission State Machine (MSM) is the sole Mission lifecycle authority.
   Runtime coordinates Mission intent, authorization, and projections; it MUST
   NOT become a Planning, Workflow, Repository, Knowledge, or provider engine.
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

## Hierarchy

```text
Bridge Constitution
└── Architecture Constitution (this document)
    ├── Runtime 2.0 Constitution
    ├── Operational Foundation Constitution
    ├── Engine Constitution
    └── State Machine Constitution
```

The [Architecture Map](ARCHITECTURE_MAP.md) is the sole technical-architecture
entry point. The [Architecture Evolution](ARCHITECTURE_EVOLUTION.md) records
the relationship between current, transitional, and target material.

## Change control

Architecture changes SHALL identify the affected owner, boundary, state
machine, evidence obligation, compatibility effect, and migration state.
An ADR records a durable decision; it does not by itself certify that code is
implemented or compliant.

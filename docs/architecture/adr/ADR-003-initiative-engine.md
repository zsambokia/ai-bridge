---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-003 - Initiative Engine

**Status:** Implemented — ORKI-007, 2026-08-02.

## Decision

Introduce a bounded Initiative Engine that continuously derives actionable
observations from Cognitive State: risks, opportunities, inconsistencies,
duplication, missing evidence, reusable components, and simplifications.

## Consequences

Initiative is advice and preparation, never silent execution or approval. It
is derived only from project-scoped structured state, is rate-limited to five
active observations, prioritised, explainable, and dismissible by the Product
Owner. ORKI-007 proves deterministic risk, opportunity and missing-evidence
derivation. Semantic inconsistency, duplication, reuse and simplification
detection remain separately gated capability work.

## Maturity decision

Initiative evolves through four evidence-gated behavioural levels: Observation,
Recommendation, Alternative proposal, and Cross-project strategic initiative.
ORKI-007 proves only Observation. Recommendation must demonstrate a safe,
evidence-based operational next action; Alternative proposal must show explicit
trade-offs; Cross-project strategic initiative requires an explicit authorized
aggregation policy and may never weaken project isolation. The canonical
criteria are in [Orki Initiative Maturity](../ORKI_INITIATIVE_MATURITY.md).

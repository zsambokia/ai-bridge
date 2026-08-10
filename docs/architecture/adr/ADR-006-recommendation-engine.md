---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-006 - Recommendation Engine

**Status:** Implemented in ORKI-003; validated by independent Release Gate.

## Decision

Recommendations are platform-owned Cognitive State objects derived from active,
project-scoped evidence, stated facts or inferences, and explicit assumptions.
A provider may propose a structured observation, but it cannot be their source
of authority.

## Consequences

Recommendations require priority, rationale, confidence, impact, dependencies,
next safe action, alternatives, trade-offs, evidence links, assumption links,
and a clear indication of whether a Product Owner decision is needed. A new
observation supersedes the active recommendation rather than rewriting history.
The engine creates neither a decision record nor a plan, governance action, or
execution authority.

## Evidence

The ORKI-003 independent audit and public Factory-boundary scenario are recorded
in [the Recommendation Engine evidence package](../../evidence/sprint-orki-003-recommendation-engine-20260802/ASSESSMENT.md).

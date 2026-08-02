# Sprint ORKI-001 - Cognitive State Foundation

**Status:** Approved for Factory Development Mode implementation
**Epic:** Orki Cognitive Operating System
**Authority:** Product Owner directive, 2026-08-01

## Objective

Create the smallest durable, project-isolated Cognitive State foundation so conversation and other observations can be recorded as attributable state updates rather than treated as memory.

## Scope

- Persistent Cognitive State container and structured entries for Mission, Business Context, Goal, Constraint, Fact, Evidence, Assumption, Risk, Opportunity, Recommendation, and Open Decision.
- Provenance, confidence, lifecycle status, correction/supersession linkage, project isolation, and a deterministic state projection.
- A service boundary that records state without granting approval, execution, AKB publication, or provider authority.
- Focused backend tests and evidence of isolation, correction, and projection.

## Non-goals

No provider redesign, UI redesign, plan replacement, autonomous execution, automatic approval, or cross-project knowledge sharing. Those are later capability Sprints.

## Principles

ORKI Principles 2, 3, 8, 9, 12, 13, 15, 16, 17, and 19 are directly applied.

## Acceptance

- A project can own one durable Cognitive State and state entries cannot cross project boundaries.
- An entry states its type, content, provenance, confidence, status, timestamps, and correction/supersession relation where applicable.
- A deterministic projection separates facts, assumptions, evidence, risks, opportunities, recommendations, and open decisions.
- State writes never create an approved scope, accepted knowledge, execution record, or provider-owned authority.
- Backend tests, applicable operational checks, independent audit, documentation, AKB/roadmap updates, self-critique, and COO Capability Acceptance pass.

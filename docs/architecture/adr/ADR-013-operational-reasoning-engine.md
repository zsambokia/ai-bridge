# ADR-013 - Operational Reasoning Engine

**Status:** Implemented in ORKI-010; full scenario-based behavioural certification remains pending.
**Date:** 2026-08-02

## Context

The previous recommendation capability preserved alternatives, trade-offs,
evidence and confidence, but a conversation-facing provider response could
still propose a recommendation as a primary field. The Product Owner requires
Operational Reasoning: recommendation must be the late, inspectable outcome
of a structured COO reasoning cycle, not an early prompt result.

## Decision

Introduce a project-scoped `OPERATIONAL_REASONING` Cognitive State artefact
and make it the only Factory Chat route that can create a recommendation. The
artefact requires a mission, attributable evidence, explicit assumptions and
unknowns, at least three alternatives, trade-offs and counter-arguments for
each alternative, expected impact, confidence, and a required-decision
boundary. Alternatives also include cost, risk, long-term effect, and a 1-10
simplicity score.

The existing Recommendation Engine remains a lower-level, state-validated
derived record writer. It is not removed because its evidence/provenance and
revision semantics are reused. The public Factory Chat adapter rejects a
direct provider `recommendation` field with
`OPERATIONAL_REASONING_REQUIRED` and records no Cognitive State change.

Product Owner Model influences are optional, project-local and explicitly
stored. They support adaptive operational leadership without becoming hidden
personalization or operational authority.

## Consequences

- The recommendation path has a stronger, testable explanation contract.
- Provider adapters must produce the ORE schema and cannot preserve legacy
  direct-recommendation compatibility at the Factory Chat boundary.
- Reasoning revisions and project isolation are durable and auditable.
- This decision does not make a recommendation accepted, a plan approved, or
  execution authorized; existing governance boundaries remain unchanged.

## Rejected alternatives

1. **Prompt-only reasoning format:** rejected because it cannot enforce state
   provenance, isolation, revisions, or a fail-closed public boundary.
2. **Keep direct recommendations and add optional rationale:** rejected because
   an incomplete rationale could still become canonical state.
3. **Replace the Recommendation Engine entirely:** rejected because it would
   duplicate proven state lifecycle logic and expand ORKI-010 beyond its
   behavioural boundary.

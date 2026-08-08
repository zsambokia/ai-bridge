# AKB — Sprint 04 Structured Decision Framework

## Reusable architectural knowledge

The Runtime-facing cognitive boundary is `StructuredDecision.v1`, not the
private output of any Reasoning implementation. Build it with
`StructuredDecisionBuilder`, validate it with `DecisionValidator`, and only
then use `to_execution_request`. The adapter is intentionally a data projection
without dispatch capability.

## Invariants

- The contract layer must not import Django, Runtime, Provider, OESM, queue, or
  execution code.
- Evidence must bind semantic retrieval to plan and Critic outcomes.
- An invalid decision returns repair feedback; it cannot cross the adapter.
- Audit persistence stores only valid serialized contracts and is not AKB or
  execution state.

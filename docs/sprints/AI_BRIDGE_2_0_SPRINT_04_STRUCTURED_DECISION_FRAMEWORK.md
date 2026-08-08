# Sprint 04 – Structured Decision Framework

Status: PASS — READY FOR PRODUCT OWNER REVIEW

Factory Development Mode is authorized by the Product Owner for AI Bridge
self-development on `main`, without a Bridge-managed provider execution.
Baseline: `0b974aee9a4cc7f9a4720f81acbf7d1647d64479`.

## Scope

Sprint 04 establishes the canonical, versioned, auditable
`StructuredDecision.v1` contract between the private Reasoning result and a
future Runtime. It includes validation, confidence dimensions, decision
evidence, a non-executing Runtime projection, and the read-only-from-an-
execution-perspective Decision API.

```text
User Request -> Semantic Layer -> Reasoning Framework
             -> Structured Decision Framework -> [STOP]
```

## Explicit exclusions

This Sprint does not alter Runtime or its state machines, invoke providers,
enqueue work, execute work, write AKB, perform Reflection, or perform Knowledge
Integration. The only persistence is an append-only audit record for a valid
decision contract; it has no Runtime relationship and cannot dispatch work.

## Acceptance

- `StructuredDecision.v1` has goal, intent, behaviour, multi-dimensional
  confidence, a bounded plan, requirements, risk, summaries, and evidence.
- The validator returns repair feedback for missing/invalid fields and blocks
  Runtime projection when invalid.
- Evidence binds Knowledge IDs, embedding hits, behaviour, plan IDs, and Critic
  observations to the contract.
- `POST /reasoning/decision`, `GET /reasoning/decision/{id}`, and
  `GET /reasoning/schema` expose the decision boundary without execution.
- The canonical E2E test stops at a validated contract and an inert
  `ExecutionRequest` projection.

## Release gates

Repository-wide Ruff, mypy, Django check, migration plan, import and scope
validation, full pytest regression, Sprint acceptance, architecture/evidence
integrity, and the Factory acceptance scenario are required from final state.

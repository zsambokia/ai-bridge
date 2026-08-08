# Sprint 03 – Cognitive Decision Framework (Reasoning)

Status: PASS — READY FOR PRODUCT OWNER REVIEW. Factory Development Mode was
authorized by the Product Owner for AI Bridge self-development on `main`,
without a Bridge-managed provider execution. Baseline:
`74d1e2832df33d04672530c3a7c267cdc3da073b`.

## Scope

Implement the pure, non-executing reasoning pipeline:

```text
Semantic Context -> Understanding -> Situation -> Behaviour -> Reasoning
                 -> Critic -> Planning -> Structured Decision
```

The pipeline consumes `SemanticContextV2`, produces inspectable typed
artifacts, and stops at `StructuredDecision`. It does not execute, call a
provider, modify Runtime, write AKB, or transition state machines.

## Acceptance

- Understanding identifies domain, intent, entities, complexity and confidence.
- Situation is a factual, non-mutating snapshot of supplied context.
- Behaviour selects a reasoning posture, never an executable action.
- Reasoning states mission and rationale; Critic returns feedback only.
- Planning returns a dependency-bearing task graph with evidence.
- The canonical E2E test proves Semantic Context through Structured Decision
  and proves that no execution boundary is crossed.

## Release gates

Repository-wide Ruff, mypy, Django check, migration plan, scope validation,
full pytest regression, architecture/evidence integrity and the scope-specific
acceptance tests must pass from the final state.

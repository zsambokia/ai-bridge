# Cognitive Decision Framework

## Boundary

Sprint 03 introduces `projects.reasoning`, a pure in-memory framework that
turns the bounded retrieval output of `projects.semantic.SemanticContextV2`
into a `StructuredDecision`.

```text
Semantic Layer (ranked evidence only)
    -> Understanding
    -> Situation Model
    -> Behaviour Engine
    -> Reasoning Engine
    -> Critic
    -> Planner
    -> Structured Decision
    -> [STOP]
```

Every stage returns an immutable typed artifact. The Critic can request user
input through `needs_user`, but cannot authorize, execute, mutate, or retry.
The Planner creates only a dependency graph and expected evidence.

## Ownership and invariants

- Semantic Layer supplies candidates and evidence; it never makes business
  decisions.
- Reasoning owns interpretation and an explainable decision proposal, never
  runtime dispatch.
- Runtime remains the sole deterministic execution owner and is unchanged.
- Providers are outside this Sprint; no provider call is made.
- AKB/Governance owns knowledge lifecycle. This framework is read-only and
  performs no knowledge, execution, or state-machine write.

This separation preserves the canonical future path:

```text
Semantic Layer -> Reasoning Layer -> Structured Decision -> Runtime
```

---
status: APPROVED_TARGET_RECORD
date: 2026-08-10
---

# Sprint 1 Provider Architecture Addendum

## Authority and scope

The Product Owner completed and approved the Provider Architecture v2.0 target
within the Architecture Convergence Program. This additive record supplements
Sprint 1's documentation-only assessment. It authorizes neither implementation
nor modification of the Runtime, Workflow Engine, models, migrations or
provider adapters.

## Recorded decisions

- Provider is a stateless, versioned external-resource definition.
- Provider Executor is the stateful unit of an external call.
- Provider manages its Executor pool and provider-specific resources.
- Provider Resolver belongs to the Operational Foundation and decides selection
  under capability, health, cost, priority and capacity policy before Provider
  Binding is created.
- Capability resolution and Provider selection are separate responsibilities.
- An Execution has an immutable Provider Binding. Provider outage, capacity
  exhaustion, fallback and failover are explicit policy-governed outcomes;
  after binding there is no automatic cross-provider fallback.
- Recovery may replace a failed Provider Executor only within the Provider
  already bound to the Execution, and only when that Provider's Runtime Profile
  permits recovery.

## Sprint artefacts updated

The Provider target is incorporated in the Gap Analysis, Constitution Book
Plan, Migration Map, ADR Recommendation List (ADR-029), Compliance Matrix,
Repository Transformation Matrix and AKB Current State. The original Sprint 1
closure report remains historical evidence for the original delivery; this
addendum has its own closure record.

## Next controlled action

Adopt ADR-029 in a separately approved Constitution Book / ADR Sprint, then
plan provider migration only after its persistence, capacity, policy and
compatibility choices are explicit.

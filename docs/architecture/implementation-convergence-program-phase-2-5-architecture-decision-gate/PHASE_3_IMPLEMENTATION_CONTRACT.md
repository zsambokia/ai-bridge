# Phase 3 Implementation Contract — Proposed

**Classification:** Proposed Implementation Convergence contract. It is not a
canonical architecture source. Any material conflict with an approved target
must return through the [Architecture Challenge
Gate](../ARCHITECTURE_IMPLEMENTATION_CONVERGENCE_GOVERNANCE.md#agc-002--architecture-challenge-gate).

## Authority boundary

This is a proposed implementation contract, not implementation authority. It becomes usable only after the Product Owner accepts the Phase 2.5 decisions and an exact approved implementation Sprint is issued under repository governance. Each child Sprint must independently define scope, risk, migration/rebuild authority, Release Gates, evidence paths, and rollback/recovery requirements.

## Preconditions

| Required before the first implementation Sprint | Why it is required |
| --- | --- |
| Product Owner decision for AC-01, AC-02, AC-04 and AC-06 | Defines the remaining canonical aggregate and ownership boundaries; AC-03 and AC-05 are accepted in Articles VI and VII. |
| Accepted ADR-034 through ADR-038, or explicitly revised equivalents | Makes the decision durable and reviewable. |
| Controlled constitutional clarification for AC-06, if approved | Removes transitional `ExecutionRun` wording before it can guide implementation incorrectly. |
| Scope hierarchy cardinalities and authorization policy | Required before durable model and API design. |
| Approved data disposition per affected development data set | Separates rebuild/migration/destructive choices from architectural planning. |

## Proposed implementation sequence

| Implementation slice | Canonical result | Prerequisites | Explicit exclusions |
| --- | --- | --- | --- |
| 3.1 Scope foundation | Organization → Workspace → Project hierarchy; Scope-owned Repository/Provider/AKB Resources; scope-aware authorization and inheritance contracts | Article VI / ADR-035 | No customer migration or external tenant onboarding without scope approval. |
| 3.2 Mission and delivery boundary | MSM-authorized immutable Operational Work Item with queue/lease/retry delivery state | AC-01, AC-06 / ADR-034, ADR-038 | No Kernel Execution replacement yet. |
| 3.3 Kernel execution foundation | One Kernel-owned Execution, immutable Execution Request, events, evidence correlation, and state machine | AC-02, AC-06 | No provider fallback or automatic cross-provider recovery. |
| 3.4 Provider integration | Capability resolution, Provider Resolver, immutable Provider Binding, Provider Executor Runtime Profile and same-provider recovery | AC-02 | No historical Provider Gateway as a first-class interface. |
| 3.5 Context and AKB minimum | Context Package manifest, Knowledge Object/version/reference primitives, KLM publication and invalidation | AC-04 | No broad document-store compatibility layer by default. |
| 3.6 Localization foundation | English canonical technical identifiers and multilingual, traceable representations for approved semantic object types | ADR-037 implementation-design decision | No automatic translation or overwrite of source Evidence. |
| 3.7 Cutover and removal | Approved migration/rebuild, removal of historical models and transitional documentation | Every preceding acceptance gate | No unbounded dual path. |

The order is deliberate: scope and ownership precede persistence; Mission and Operational Foundation boundaries precede Kernel execution; the Kernel boundary precedes Provider and AKB integrations.

## Non-negotiable implementation invariants

- Only MSM authorizes business state transitions and Operational Work Items.
- Operational Foundation owns delivery mechanics, not Kernel Execution state.
- Only AI Kernel owns Execution and its Kernel State.
- Provider Binding is immutable for an Execution; executor recovery remains within the same Provider.
- Context Packages, Knowledge Object versions, Knowledge References, Evidence, and Kernel Events are immutable after publication/creation.
- Every persistent canonical domain object has exactly one direct Scope owner and a named lifecycle authority.
- Compatibility is opt-in, time-bounded, and evidenced; it is never assumed because a historical table or API exists.

## Required acceptance evidence for each child Sprint

1. Contract-bound baseline and exact approved scope.
2. Repository/model/API impact assessment against this blueprint.
3. State-machine and ownership tests for the slice.
4. Migration or rebuild plan, including preservation/disposition of development data and rollback where applicable.
5. Security and scope-isolation tests where a durable scoped object is introduced.
6. Documentation/ADR/Constitution cross-reference check.
7. Final evidence generated from the final branch state and a closure report.

## Prohibited shortcuts

- Renaming `ExecutionRun` to `Execution` without moving lifecycle ownership.
- Reusing `ExecutionJob` as an Execution Attempt solely to avoid a schema change.
- Treating a Repository or physical Execution Workspace as a logical Scope.
- Making a Provider, Provider Gateway, or Provider Executor the owner of Mission, Context, Evidence, or Execution.
- Introducing an implicit locale fallback or rewriting the original language of evidence.

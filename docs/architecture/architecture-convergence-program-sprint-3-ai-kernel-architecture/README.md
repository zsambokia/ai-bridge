---
status: APPROVED_DOCUMENTATION_SCOPE
classification: NON_EXECUTABLE_ARCHITECTURE_SPRINT_RECORD
execution_mode: Factory Development Mode
task_type: DOCUMENTATION
handoff_identifier: ARCHITECTURE-CONVERGENCE-SPRINT-3-AI-KERNEL-20260810
depends_on:
  - docs/architecture/architecture-convergence-program-sprint-1/README.md
  - docs/architecture/architecture-convergence-program-sprint-1/PROVIDER_ARCHITECTURE_V2.md
  - docs/architecture/AI_KERNEL_ARCHITECTURE_CONSTITUTION.md
evidence_root: docs/evidence/architecture-convergence-program-sprint-3-ai-kernel-architecture/
---

# Architecture Convergence Program – Sprint 3

## Article III – AI Kernel Architecture

## Status and authority

This is a non-executable architecture Sprint record. It intentionally lives
outside `docs/sprints/`, which is reserved for Bridge-issued, database-backed,
hash-bound executable SPRINT scopes. Product Owner Factory Development Mode
authority permits this documentation and target-architecture Sprint without an
AI Bridge-managed provider execution, provider heartbeat or Bridge-issued
running execution; it does not impersonate one.

## Objective

Converge the approved Article III AI Kernel architecture, Provider update and
repository terminology into the Constitution Book plan. The work records the
target boundary and a controlled migration route; it does not change runtime
behaviour.

## Approved scope

1. Add Article III as an approved target Constitution Book entry with sections
   3.1–3.19.
2. Incorporate the final Provider rules: stateless Provider, stateful Provider
   Executor, immutable Provider Binding, same-Provider recovery and Runtime
   Profile.
3. Record the Execution-first model, capability-first routing, immutable
   Context Package integration, Kernel Events, leases, recovery, scheduling,
   telemetry, evidence and security invariants.
4. Produce a terminology convergence matrix for current repository names and
   target canonical names, including compatibility and breaking-change status.
5. Update the Constitution Book plan and ADR recommendation register.

## Explicit exclusions

This Sprint MUST NOT change application code, Django models, migrations, APIs,
Runtime/AI Kernel implementation, Workflow Engine, provider adapters, provider
selection, data, external configuration or historical evidence. It MUST NOT
rename `ExecutionRun`, `ExecutionRequest`, runtime symbols or documentation in
bulk. It makes no implementation-compliance claim and does not approve an
automatic Provider fallback.

## Assessment and reuse

| Current foundation | Target treatment |
| --- | --- |
| `ExecutionRun`, `ExecutionJob`, recovery and progress events | Retain as migration input; map to target Execution only through ADR-023. |
| `projects/runtime_contract.py` and `projects/decision_contract/framework.py` | Retain immutable-contract patterns; do not equate current `ExecutionRequest` with final aggregate without ADR-023. |
| Operational Foundation and Provider Gateway | Retain operational mechanics; converge boundary/terminology only after ADR-029 and ADR-033. |
| Provider Architecture v2.0 addendum | Modify to record immutable binding, same-Provider recovery and Runtime Profile. |
| Existing Runtime/Engine documentation | Keep as current or historical evidence; classify, do not silently rewrite. |

## Required ADR recommendations

| Proposed ADR | Required decision | Reason |
| --- | --- | --- |
| ADR-023 | Execution aggregate and `ExecutionRun`/job/recovery compatibility. | Existing records have production governance and recovery semantics. |
| ADR-024 | Capability declaration and resolution contract. | Capability-first routing cannot be inferred from current Engine paths. |
| ADR-025 | Context Package contract. | The Kernel must bind one immutable, reproducible package. |
| ADR-027 | Kernel Event envelope and replay compatibility. | Existing event streams are heterogeneous. |
| ADR-029 | Provider binding, Executor lifecycle, Runtime Profile and same-Provider recovery. | Prevents accidental cross-provider fallback or ownership ambiguity. |
| ADR-033 | AI Kernel boundary and terminology transition. | Separates target terminology from legacy Runtime symbols safely. |

## Controlled migration map

| Phase | Outcome | Dependencies | Required proof |
| --- | --- | --- | --- |
| 0 – Ratify | Adopt Article III and ADRs into the Constitution Book. | Book adoption, ADR-023–029, ADR-033. | Canonical amendment and accepted ADRs. |
| 1 – Contracts | Define Execution, Provider Binding, Runtime Profile, Context and event compatibility contracts. | Phase 0. | Contract and transition tests. |
| 2 – Kernel boundary | Introduce Kernel-owned registry/state machine while retaining legacy mechanics behind adapters. | ADR-023, ADR-027, ADR-033. | Identity, event and recovery compatibility evidence. |
| 3 – Provider convergence | Implement capability resolution, immutable binding and same-Provider Executor recovery. | ADR-024, ADR-029. | No cross-provider fallback and profile-enforcement evidence. |
| 4 – Terminology retirement | Deprecate aliases only after compatibility proof and consumer migration. | Phases 1–3. | Search, API, migration and historical-preservation evidence. |

## Acceptance criteria

1. Article III defines the Kernel boundary without assigning business logic,
   Mission ownership or Context construction to it.
2. Execution is Kernel-owned and Provider binding is immutable throughout an
   Execution.
3. Provider Executor replacement/recovery stays within the bound Provider and
   Runtime Profile governs supported technical behaviour.
4. The terminology matrix preserves required canonical terms and marks every
   proposed change as retain, rename, alias, deprecated or historical.
5. The Constitution Book and ADR plan distinguish target architecture from
   current implementation.
6. No implementation artifact is changed; standard documentation gates pass.

## Required evidence

- `docs/evidence/architecture-convergence-program-sprint-3-ai-kernel-architecture/LOCAL_EXECUTION_RECORD.md`
- `docs/evidence/architecture-convergence-program-sprint-3-ai-kernel-architecture/OPERATIONAL_ACCEPTANCE.md`
- `docs/evidence/architecture-convergence-program-sprint-3-ai-kernel-architecture/CLOSURE_REPORT.md`
- `docs/evidence/architecture-convergence-program-sprint-3-ai-kernel-architecture/acceptance-results.json`

## Release-gate additions

Standard repository Release Gates apply. This documentation-only Sprint also
requires Article/Provider/ADR link verification, terminology-matrix review,
scope/exclusion verification and final-diff validation. Operational Acceptance
is `NOT APPLICABLE - documentation-only; no runtime artifact was changed` and
is not runtime proof.

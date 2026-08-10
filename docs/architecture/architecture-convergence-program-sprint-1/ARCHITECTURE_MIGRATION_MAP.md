---
status: PROPOSED
version: 0.1.0
---

# Architecture Migration Map

This is a dependency-ordered program map, not implementation authority.

| Phase | Outcome | Prerequisites | Reuse / change boundary | Proof required before next phase |
| --- | --- | --- | --- | --- |
| 0 — Converge | Adopt Book and ADR decisions. | This Sprint; Product Owner approval. | Documentation only. | Traceable Book, accepted ADRs, no false compliance claim. |
| 1 — Identity contracts | Define scope hierarchy, actor authorization, locale identity and reserved `Workspace` terminology. | ADR-021, ADR-026, ADR-028. | Reuse Project identity; do not overload physical `ExecutionWorkspace`. | Isolation and authorization contract tests. |
| 2 — Intake and capability | Establish Mission Intake Port and Capability catalogue/resolution. | ADR-022, ADR-024; Phase 1. | Preserve Factory Chat as human interface; route API/MCP/scheduler adapters through one intake contract. | Equivalent Mission creation and denial evidence for every ingress. |
| 3 — AI Kernel, Execution and provider boundary | Establish the accepted AI Kernel boundary; introduce first-class Execution and immutable Context Package; bind attempts to `ExecutionRun`; define Capability Resolution, Provider Integration, Provider Resolver, Provider Binding, Provider and Provider Executor contracts. | ADR-023, ADR-025, ADR-029, ADR-033, ADR-034; Phase 2. | Reuse `ExecutionRun`, jobs, recovery and provider-integration adapter mechanics; do not duplicate them or erase audit history. Provider selection must finish before binding; an Executor may be replaced only within the same bound Provider. | Reproducible context, idempotent execution, immutable provider-binding audit trail, Kernel Profile enforcement and same-provider recovery trace. |
| 4 — Strangler migration | Move Factory Chat/Orki and workflow/provider direct paths behind Mission → Capability → AI Kernel → Execution → Capability Resolution → Provider → Provider Executor. | Phases 2–3. | Retire only adapters proven bypassed; preserve historical evidence. | E2E mission-to-provider-executor route, same-provider recovery, explicit provider-outage handling and audit evidence. |
| 5 — Scope and localization rollout | Apply scope and locale rules to UI, prompts, personas, AKB and documentation. | Phases 1–4. | Incremental backfill with explicit defaults and provenance. | Cross-scope denial, locale fallback and canonical/derived-content tests. |
| 6 — Event convergence and retirement | Publish canonical event/outbox contract and remove proven redundant legacy routes. | ADR-027; completed strangler proof. | Map existing Execution/Provider/Orki/Workflow events; do not delete audit history. | Replay, idempotency, observability and retention evidence. |

## Guardrails

- Phase 3 additionally requires ADR-034 before `ExecutionJob` is retained,
  mapped to an Execution Attempt or retired. It also establishes Kernel Profile
  terminology and the separate Engine Definition Registry and Capability
  Registry.
- Provider Integration and Provider Resolver complete selection before binding.
  A Provider Gateway may exist only as an implementation adapter/boundary, not
  as a first-class architectural object.
- No data migration precedes the corresponding ADR and backward-compatibility
  plan.
- A feature is tenant-ready only when scope is explicit and authorization is
  enforced; a nullable foreign key alone is not readiness.
- Localization never changes the canonical meaning or identifier of a
  normative decision.
- Provider capacity exhaustion is an explicit operational outcome. An eligible
  alternative may be selected only before the Execution's Provider Binding is
  created; after binding, the system may wait, recover within the same Provider
  or fail according to policy, but must not silently fail over.
- R20-00 remains the baseline until a new independent compliance assessment
  proves the end-to-end target route.

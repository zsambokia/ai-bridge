---
status: PROPOSED
version: 0.1.0
---

# Constitution Book Plan

## Purpose and authority model

The Constitution Book is a single navigable normative body, not a replacement
architecture written beside the existing one. Adoption happens in a later,
explicitly approved Constitution amendment Sprint. Until then the existing
Bridge Constitution and Runtime 2.0 Constitution remain authoritative.

## Proposed Book structure

| Book part | Starting material | Planned treatment |
| --- | --- | --- |
| 0. Charter, language and authority | Bridge Constitution | Retain governance; amend the product-only/multi-tenancy language after ADR-021. English is canonical for normative content. |
| 1. Scope, identity and tenancy | Project context, Bridge Constitution | New: Organization, Workspace, Repository and Project scope semantics; ownership, authorization and correlation requirements. |
| 2. Runtime intake and Mission | Runtime 2.0 Constitution | Modify: Mission Intake Port is unified; Conversation is only the human interface. |
| 3. Capability and Domain Engines | Architecture + Engine Constitutions | Modify: Capability is addressed first; Engine is one possible capability implementation; business state allowed, operational state external. |
| 4. AI Kernel, Execution and Operational Foundation | Runtime 2.0 + Foundation Constitution + Article III – AI Kernel Architecture | Modify: define first-class Execution, ExecutionRun attempt semantics, AI Kernel boundary, handoff, recovery, scheduling, registry, events and Foundation separation. |
| 4a. Provider resources and executors | Provider Architecture v2.0 + Article III | New: Provider Integration and Provider Resolver precede a stateless Provider definition and stateful Provider Executor; immutable Provider Binding, same-Provider recovery, Kernel Profile and Provider-owned capacity/pool. Provider Gateway is an implementation boundary only. |
| 5. Context, knowledge and evidence | AKB Foundation + Knowledge Pipeline + AKB Knowledge Object & Lifecycle Constitution | Modify: Context Package contract and evidence/reproducibility rules while preserving AKB ownership; add Knowledge Object and independent Knowledge Lifecycle Management target chapters. |
| 6. Events, audit and recovery | State Machine Constitution + existing evidence rules | Modify: canonical envelope/outbox/idempotency expectations, without selecting an event product prematurely. |
| 7. Localization | New | New: UI, prompts, personas, knowledge and documentation; canonical English and derived localization governance. |
| 8. Transition and historical record | Architecture Evolution, Baseline, ADRs | Retain: migration register and immutable historical evidence, with `HISTORICAL`/`TRANSITIONAL` labels. |

## Publication rules

For Book part 4, `Engine Definition Registry` and `Capability Registry` are
distinct registry types. `Kernel Managers`, `Kernel Registries` and `Kernel
Objects` replace a generic Kernel Services category; the detailed naming and
the `ExecutionJob`/Execution Attempt decision remain subject to ADR-033 and
ADR-034.

1. One Book index is the technical entry point; chapters may retain their files
   where that keeps traceability.
2. A chapter declares `CANONICAL`, `SUPPORTING`, `TRANSITIONAL`, or
   `HISTORICAL`; no document silently changes status.
3. Normative identifiers, ADRs, Capability definitions and canonical
   documentation are English. Translations are derived, version-bound assets.
4. An ADR must be accepted before a chapter introduces a new data/authority
   contract.
5. Historical evidence is linked, not retroactively rewritten.

## Adoption acceptance criteria

- No contradiction remains between the amended Bridge Charter, Book chapters
  and Runtime 2.0 target.
- Mission Intake, Capability, Execution, Context Package, Scope and Locale
  have defined owners, invariants and terminology.
- Provider, Provider Executor, Executor Pool and Provider Resolver have
  defined ownership, state, selection, capacity and recovery boundaries.
- Engine Definition Registry and Capability Registry have distinct authorities;
  every first-class Kernel Object follows the Definition-to-Registry-to-Instance
  pattern, followed by its State Machine, Events and Evidence.
- AI Kernel terminology is used only for the operational execution core;
  historical `Runtime` terms have an explicit compatibility status.
- The Book distinguishes target architecture from implemented capability.
- Every implementation change maps to an accepted ADR and a migration phase.

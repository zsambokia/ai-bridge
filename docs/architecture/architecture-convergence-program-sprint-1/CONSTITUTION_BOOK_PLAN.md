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
| 3. Capability and Domain Engines | Architecture + Engine Constitutions | Modify: Capability is addressed first; Engine is one provider; business state allowed, operational state external. |
| 4. Execution and Operational Foundation | Runtime 2.0 + Foundation Constitution | Modify: define first-class Execution, ExecutionRun attempt semantics, handoff, recovery and provider boundary. |
| 5. Context, knowledge and evidence | AKB Foundation + Knowledge Pipeline | Modify: Context Package contract and evidence/reproducibility rules while preserving AKB ownership. |
| 6. Events, audit and recovery | State Machine Constitution + existing evidence rules | Modify: canonical envelope/outbox/idempotency expectations, without selecting an event product prematurely. |
| 7. Localization | New | New: UI, prompts, personas, knowledge and documentation; canonical English and derived localization governance. |
| 8. Transition and historical record | Architecture Evolution, Baseline, ADRs | Retain: migration register and immutable historical evidence, with `HISTORICAL`/`TRANSITIONAL` labels. |

## Publication rules

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
- The Book distinguishes target architecture from implemented capability.
- Every implementation change maps to an accepted ADR and a migration phase.

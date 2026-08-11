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

Terminology Finalization is tracked in
[Architecture Convergence Program – Sprint 4](../architecture-convergence-program-sprint-4-terminology-finalization/README.md).
Its classification register distinguishes approved target terms from
transitional governance and immutable historical records; it does not itself
adopt the Constitution Book.

## Proposed Book structure

| Book part | Starting material | Planned treatment |
| --- | --- | --- |
| 0. Charter, language and authority | Bridge Constitution | Retain governance; amend the product-only/multi-tenancy language after ADR-021. English is canonical for normative content. |
| 0a. Architecture documentation governance | Article V — Architecture Documentation Governance | New: canonical diagrams are normative architecture artifacts; each ADR and Architecture Convergence change records a Diagram Impact Assessment; Mermaid-in-Markdown is the authoritative logical source, Draw.io is derived, and every diagram declares an Architecture Status. |
| 1. Scope, identity and tenancy | Project context, Bridge Constitution, Article VI — Scope Architecture | New: Organization → Workspace → Project scope semantics; Repository and Provider as scope-owned Resources; ownership, authorization, inheritance and correlation requirements. |
| 2. Runtime intake and Mission | Runtime 2.0 Constitution | Modify: Mission Intake Port is unified; Conversation is only the human interface. |
| 2a. Conversation to Mission | Article IV - Conversation to Mission Architecture | New: Factory Chat is a UI adapter; Conversation Understanding and the CSE govern human interaction; Mission Resolution is the sole human-Conversation Mission-intake boundary while MSM remains the sole Mission lifecycle owner. |
| 3. Capability and Domain Engines | Architecture + Engine Constitutions | Modify: Capability is addressed first; Engine is one possible capability implementation; business state allowed, operational state external. |
| 4. AI Kernel, Execution and Operational Foundation | Runtime 2.0 + Foundation Constitution + Article III – AI Kernel Architecture | Modify: define first-class Execution, ExecutionRun attempt semantics, AI Kernel boundary, handoff, recovery, scheduling, registry, events and Foundation separation. |
| 4a. Provider resources and executors | Provider Architecture v2.0 + Article III | New: Provider Integration and Provider Resolver precede a stateless Provider definition and stateful Provider Executor; immutable Provider Binding, same-Provider recovery, Kernel Profile and Provider-owned capacity/pool. Provider Gateway is an implementation boundary only. |
| 5. Context, knowledge and evidence | AKB Foundation + Knowledge Pipeline + AKB Knowledge Object & Lifecycle Constitution | Modify: Context Package contract and evidence/reproducibility rules while preserving AKB ownership; add Knowledge Object and independent Knowledge Lifecycle Management target chapters. |
| 6. Events, audit and recovery | State Machine Constitution + existing evidence rules | Modify: canonical envelope/outbox/idempotency expectations, without selecting an event product prematurely. |
| 7. Localization | Article VII -- Localization Architecture | New: English canonical machine identifiers; multilingual UI, knowledge, persona, conversation, documentation and summaries; derived, traceable evidence translations. |
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
3. Canonical code and technical identifiers, normative identifiers, ADRs,
   Capability definitions and canonical documentation are English. User-facing
   and semantic content is localization-ready; translations are derived,
   traceable representations and never overwrite original Evidence.
4. An ADR must be accepted before a chapter introduces a new data/authority
   contract.
5. Historical evidence is linked, not retroactively rewritten.
6. Every canonical diagram has one version-controlled Markdown/Mermaid logical source; any editable `.drawio` is derived from it;
   derived PNG, SVG, and PDF artifacts do not become a second source of
   architectural truth and need not be regenerated for every documentation
   change.
7. Every ADR and Architecture Convergence change records a Diagram Impact
   Assessment before closure, including an explicit no-impact conclusion where
   no diagram source change is necessary.
8. Every canonical diagram declares one of `DRAFT`, `ASSESSMENT`, `APPROVED`,
   `CANONICAL`, `TRANSITIONAL`, `HISTORICAL`, or `DEPRECATED` in visible
   metadata and its Markdown companion. The [Visual Constitution](../diagrams/README.md)
   indexes the current canonical set.

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
- Canonical diagrams are consistent with their corresponding Constitution
  chapters, and each adopted architectural change has a completed Diagram
  Impact Assessment.

---
status: APPROVED_DOCUMENTATION_SCOPE
classification: NON_EXECUTABLE_ARCHITECTURE_SPRINT_RECORD
execution_mode: Factory Development Mode
task_type: DOCUMENTATION
handoff_identifier: ARCHITECTURE-CONVERGENCE-SPRINT-4-TERMINOLOGY-FINALIZATION-20260810
depends_on:
  - docs/architecture/architecture-convergence-program-sprint-1/README.md
  - docs/architecture/architecture-convergence-program-sprint-2-akb-knowledge-object-lifecycle/README.md
  - docs/architecture/architecture-convergence-program-sprint-3-ai-kernel-architecture/README.md
  - docs/architecture/architecture-convergence-program-sprint-3-ai-kernel-architecture/TERMINOLOGY_CONVERGENCE_MATRIX.md
evidence_root: docs/evidence/architecture-convergence-program-sprint-4-terminology-finalization/
---

# Architecture Convergence Program – Sprint 4

## Constitution Convergence – Terminology Finalization

## Status and authority

This is the Product Owner-authorised, documentation-only convergence Sprint.
Factory Development Mode authorises local repository work without a
Bridge-managed provider execution. This record does not claim that the target
architecture is implemented, and it does not alter application code, models,
migrations, APIs, Runtime/AI Kernel behaviour, workflows, data or external
configuration.

The [Terminology Convergence Matrix](../architecture-convergence-program-sprint-3-ai-kernel-architecture/TERMINOLOGY_CONVERGENCE_MATRIX.md)
is the terminology Single Source of Truth for this Sprint. Article I and
Article III are approved target entries; their adoption as the single
normative Constitution Book remains governed by ADR-020 and the Book-adoption
process.

## Objective

Converge the complete `docs/` corpus to one explicit terminology policy. Active
target and transitional architecture documents must use the canonical terms,
ownership boundaries and diagrams. Immutable evidence and historical records
must be preserved, classified and made unambiguous rather than silently
rewritten.

## Approved scope

1. Inventory all documents in `docs/`, including architecture, constitution,
   runtime, ADR, AKB, contracts, operations, roadmap, sprint and evidence
   records.
2. Classify every document family as active target, transitional, historical
   or immutable evidence, with an explicit treatment rule.
3. Apply the Matrix to active and transitional Constitution, AI Kernel,
   Provider, AKB, Operational Foundation, Book-plan, Gap Analysis and related
   architecture documents, including diagrams and cross references.
4. Preserve historical snapshots, accepted ADRs and execution evidence as
   historical records; record their legacy vocabulary in the classification
   register instead of falsifying the record.
5. Produce the convergence report, consistency matrix, open-issues/ADR record
   and closure evidence.

## Explicit exclusions

- No implementation, code-symbol, API, model, migration, workflow or data
  rename.
- No automatic `ExecutionJob` rename; ADR-034 remains required.
- No automatic Provider fallback or Provider ownership change.
- No retroactive editing of immutable evidence, accepted ADR decision bodies or
  historical sprint acceptance results.
- No Constitution Book adoption claim before the separate adoption Sprint.

## Canonical terminology rules

| Topic | Required treatment |
| --- | --- |
| Technical execution core | `AI Kernel`; retain `Runtime` only for generic or historical usage. |
| Provider boundary | `Provider Integration -> Provider Resolver -> Provider -> Provider Executor`; Gateway is adapter-only. |
| Kernel categories | `Kernel Managers`, `Kernel Registries`, `Kernel Objects`; `Kernel Services` is not a canonical umbrella. |
| Registries | Keep `Engine Definition Registry` and `Capability Registry` distinct. |
| ExecutionJob | Keep unchanged pending ADR-034. |
| First-class Kernel objects | Apply the meaningful parts of `Definition -> Registry -> Instance -> State Machine -> Events -> Evidence`. |
| Historical vocabulary | Preserve verbatim and visibly classify as `HISTORICAL` or `TRANSITIONAL`. |

## Required deliverables

- [Terminology Convergence Report](TERMINOLOGY_CONVERGENCE_REPORT.md)
- [Consistency Matrix](CONSISTENCY_MATRIX.md)
- [Open Issues and ADR Needs](OPEN_ISSUES_AND_ADR_NEEDS.md)
- [Document Classification Register](DOCUMENT_CLASSIFICATION_REGISTER.md)
- [Closure report](../../evidence/architecture-convergence-program-sprint-4-terminology-finalization/CLOSURE_REPORT.md)

## Acceptance criteria

1. Every one of the 819 documents present in `docs/` at assessment is covered
   by an explicit family-level classification rule.
2. Every active target or transitional architecture document uses the Matrix
   or carries a precise transition note; diagrams follow the same rule.
3. Historical and evidence documents are not silently rewritten, and their
   legacy terminology is visible in the classification register.
4. `Provider Gateway` is never described as a first-class target object.
5. `Kernel Services` is not presented as a canonical target category.
6. `Engine Definition Registry` and `Capability Registry` remain distinct.
7. `ExecutionJob` remains an ADR-034 decision, not an automatic rename.
8. Markdown links and Article/ADR references affected by the Sprint resolve.

## Required evidence and Release Gates

Standard repository Release Gates apply. This documentation-only Sprint adds
full-corpus inventory, targeted terminology scans, Markdown-link verification,
Matrix/Article/ADR cross-reference verification and final diff review.
Operational Acceptance is `NOT APPLICABLE – documentation-only; no runtime
artifact was changed` and is not a runtime-compliance assertion.

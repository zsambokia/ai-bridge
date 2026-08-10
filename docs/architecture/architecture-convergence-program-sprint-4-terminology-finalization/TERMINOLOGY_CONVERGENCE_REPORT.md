---
status: CURRENT
scope: Architecture Convergence Program – Sprint 4
language: en
---

# Terminology Convergence Report

## Outcome

The Architecture Documentation now has an explicit three-layer vocabulary:

```text
Approved target: Constitution Book Articles and the Terminology Matrix
        ↓
Transitional governance: existing constitutions, Runtime 2.0 and implementation contracts
        ↓
Historical record: accepted ADRs, prior maps, sprint scopes and immutable evidence
```

This is a documentation convergence, not a claim of implementation migration.

## Applied decisions

| Matrix decision | Documentation convergence |
| --- | --- |
| Runtime operational core -> AI Kernel | Article III is the target source. Runtime 2.0 is explicitly TRANSITIONAL; generic and historical Runtime usage remains valid. |
| Provider Gateway -> Provider Integration adapter | Active/transitional boundary references use Provider Integration. Gateway is retained only as an adapter or historical term. |
| Kernel Services -> three categories | Article III defines Kernel Managers, Kernel Registries and Kernel Objects. No target document treats Kernel Services as a category. |
| Engine Registry vs Capability Registry | Article III invariant AK-014 and the Matrix keep Engine Definition Registry and Capability Registry separate. |
| ExecutionJob | No rename applied. Its status is an explicit ADR-034 decision. |
| Uniform object pattern | Article III and the Matrix apply Definition -> Registry -> Instance -> State Machine -> Events -> Evidence to meaningful parts of first-class objects. |
| Runtime Object/State/Registry/Policy/Profile/Resource/Queue | Matrix defines corresponding Kernel terms only inside the AI Kernel boundary; business/MSM terms remain distinct. |

## Ownership convergence

```text
Conversation (human only) / external ingress
                    ↓
                 Mission -> MSM
                    ↓
          Operational Foundation
                    ↓
                 AI Kernel
                    ↓
Execution -> Capability Resolution -> immutable Provider Binding
                    ↓
Provider Integration -> Provider Resolver -> Provider -> Provider Executor
```

The MSM owns business-process state. Operational Foundation is its own layer,
not an Engine or Kernel category. The AI Kernel owns technical Execution state.
Engine and Provider supply Capability implementation/execution but never own
the Execution. Context Builder remains outside the Kernel and supplies an
immutable Context Package.

## Corpus review method

The review inventoried all 819 existing `docs/` files by top-level family,
searched all text documentation for Matrix-controlled legacy terminology and
checked the active architecture subset manually. The classification register
sets the modification rule for every family. Legacy terms found in historical
or immutable evidence are retained deliberately; changing them would make the
record less auditable.

## Diagram treatment

Article III contains the canonical target diagram. Diagrams in historical
Architecture Map and Architecture Evolution are preserved as labelled
snapshots. Active/transitional provider-bound flows now name the boundary
`Provider Integration adapter`; this does not assert replacement of an
implementation class named Gateway.

## Cross-reference result

The new Sprint links to the Matrix and all prior convergence Sprints. The
transitional constitutions link by name to Articles I/III and the planned
Book-adoption path. Current and proposed ADR references are listed in the
open-issues record. Markdown link verification is captured in Sprint 4
closure evidence.

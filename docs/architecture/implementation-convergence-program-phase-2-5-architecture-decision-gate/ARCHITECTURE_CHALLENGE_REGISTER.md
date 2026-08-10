# Architecture Challenge Register

## Decision method

Each challenge starts with the constitutional target, reconstructs the present repository lifecycle from source evidence, compares viable canonical alternatives, and ends with one recommendation requiring Product Owner confirmation. Recommendations are intentionally not constitutional amendments.

## AC-01 — `ExecutionJob`

| Item | Assessment |
| --- | --- |
| Constitutional target | Operational Foundation owns delivery mechanics; the AI Kernel owns one first-class `Execution`. Queue and lease infrastructure must not redefine Execution ownership. |
| Repository evidence | `projects/models.py` describes `ExecutionJob` as a durable, lease-owned queue entry for one `ExecutionRun`. `projects/execution.py` creates an `ExecutionRun`, then an `ExecutionJob`; job claiming assigns lease owner, expiry, fencing token, retry/recovery state, and sequence. |
| Finding | The current object is a delivery envelope. It is neither the business Mission nor a provider attempt, and it must not become the canonical Execution merely because it is durable. |
| Alternative A | Retain `ExecutionJob` as the canonical kernel execution. Rejected: its queue/lease lifecycle belongs to Operational Foundation, not Kernel execution semantics. |
| Alternative B | Rename it to `ExecutionAttempt`. Rejected: a job may be retried or recovered without denoting a discrete provider attempt. |
| Alternative C | Retain it as a durable Operational Work Item. Viable, but retaining the historical name adds no architectural value. |
| **Recommendation** | **`ExecutionJob` does not exist in the canonical model. Its valid responsibilities become the delivery state of a first-class, Operational-Foundation-owned `OperationalWorkItem`.** The Work Item contains an immutable MSM-authorized specification and mutable queue, lease, retry, scheduling, and recovery-delivery state. |
| Product Owner decision | Approve direct replacement of `ExecutionJob` by `OperationalWorkItem`, or select an alternative. |
| ADR | Required: **ADR-034 — Canonical work-item and execution-attempt model**. |

## AC-02 — Canonical Execution Model

| Item | Assessment |
| --- | --- |
| Constitutional target | The Kernel creates and owns one first-class `Execution`; an Engine and Provider are capability providers, and Provider Binding is immutable for an Execution. |
| Repository evidence | `OrkiExecution` in `projects/orki_runtime.py` combines conversation analysis, planning, approval, dispatch, verification, reflection, and knowledge-candidate activity. `ExecutionRun` is a contract-bound dispatcher record. `ExecutionJob` provides queue/lease mechanics. Provider calls traverse `provider_gateway.py`; recovery attempts and progress events are separately persisted. |
| Finding | The current three-object model mixes Mission intake, operational delivery, and kernel execution. `OrkiExecution` is an historical orchestration projection, not the target Execution. `ExecutionRun` is closest to the target identity but its current lifecycle is entangled with dispatcher and job concerns. |
| Alternative A | Preserve all three with clarified names. Rejected: retains duplicated authority and compatibility-first complexity. |
| Alternative B | Make `ExecutionRun` an `ExecutionAttempt`. Rejected: it is contract-bound and lifecycle-wide, not one provider invocation. |
| Alternative C | Create both `Execution` and an always-persisted `ExecutionAttempt`. Viable only if separate attempt semantics are required by an accepted retry/recovery policy; current evidence does not justify that extra aggregate for MVP. |
| **Recommendation** | **Replace the three historical concepts with one Kernel-owned `Execution`; do not introduce a first-class `ExecutionAttempt` initially.** Provider executor creation, invocation, crash, retry, checkpoint, and recovery are append-only Kernel Events and Evidence correlated to the Execution. An attempt aggregate may be introduced later only by ADR with distinct lifecycle semantics. `OrkiExecution` is decomposed into Conversation/Mission/MSM work and removed; `ExecutionRun` is replaced, not preserved as a compatibility model. |
| Product Owner decision | Approve the one-Execution model and deferred-attempt rule, or select a different canonical aggregate model. |
| ADR | Required: **ADR-034 — Canonical work-item and execution-attempt model**. |

## AC-03 — Identity, Scope, and Ownership

| Item | Assessment |
| --- | --- |
| Constitutional target | The platform is scope-aware, tenant-ready, organization-ready, and workspace-ready. Every durable object requires unambiguous owner and scope. |
| Repository evidence | The repository has Project-bound scopes and contracts (`projects/scopes.py`, `projects/contracts.py`), physical execution workspaces (`projects/workspace.py`), and repository documents/snapshots (`projects/repository_lifecycle.py`). It has no canonical `Organization`, logical `Workspace`, or `Repository` ownership aggregate. |
| Finding | Current project binding cannot safely stand in for tenant and scope ownership; physical execution workspace must not be confused with a logical Workspace. |
| Alternative A | Continue with Project as the only scope. Rejected: fails the approved tenant- and workspace-ready constitutional target. |
| Alternative B | Add organization and workspace only as optional metadata. Rejected: optional ownership cannot support authorization or deterministic object provenance. |
| **Recommendation** | **Adopt `Organization → Workspace → Repository → Project` as the logical ownership hierarchy.** `Organization` is the tenant/authorization root; `Workspace` is a logical operating scope; `Repository` is a source and knowledge boundary; `Project` is the governed product context associated with a repository. Every durable object records its owning Project and derives its Organization, Workspace, and Repository scope from that relationship. `ExecutionWorkspace` remains a separately named physical provider resource. |
| Product Owner decision | Approve the hierarchy, including the separation of logical Workspace from physical Execution Workspace, and decide final cardinality rules before persistence design. |
| ADR | Required: **ADR-035 — Canonical identity, ownership, and scope hierarchy**. |

## AC-04 — Minimum Canonical AKB Model

| Item | Assessment |
| --- | --- |
| Constitutional target | AKB stores versioned Knowledge Objects, not documents. Stable identity, immutable versions, lifecycle, provenance, graph relationships, and immutable Knowledge References are mandatory. KLM is independent from Runtime/Kernel execution. |
| Repository evidence | `KnowledgeEntry`, `KnowledgeRevision`, and `KnowledgeContextPackage` in `projects/models.py` and `projects/knowledge*.py` are entry/document-centric. They do not establish a uniform typed object root with versioned graph relationships and reference-by-version semantics. |
| Finding | The current model can supply migration evidence but is not the canonical AKB model. |
| Alternative A | Extend `KnowledgeEntry` as the universal object. Rejected: its semantics are entry-centric and would preserve the old abstraction under a new label. |
| Alternative B | Build every specialized knowledge type before any AKB use. Rejected: unnecessarily delays a usable uniform model. |
| **Recommendation** | **Start with five canonical primitives:** `KnowledgeObject` (stable URI and typed identity), immutable `KnowledgeObjectVersion`, versioned `KnowledgeRelationship`, immutable `KnowledgeReference`, and immutable `ContextPackage` manifest. Minimum governed object types are Architecture Principle, ADR, Requirement, Capability, Workflow, Persona, Policy, Evidence, and Glossary Term. Knowledge Lifecycle Management initially supplies change detection, update planning, publication, freshness status, and context invalidation; representations remain secondary projections. |
| Product Owner decision | Approve the minimum primitives, initial type set, and KLM minimum boundary. |
| ADR | Required: **ADR-036 — Minimum canonical AKB and knowledge lifecycle model**. |

## AC-05 — Localization Model

| Item | Assessment |
| --- | --- |
| Constitutional target | The platform is localization-ready across UI, prompts, personas, knowledge, documentation, and business-relevant evidence. English is canonical for normative documentation, definitions, and internal identifiers. |
| Repository evidence | The reviewed application models expose no platform-wide locale, localized representation, translation provenance, or fallback model. |
| Finding | UI-string translation alone would violate the constitutional scope; blindly translating evidence would compromise provenance. |
| Alternative A | Implement UI-only localization. Rejected: not localization-ready for prompts, persona, and AKB. |
| Alternative B | Translate every stored object and evidence record. Rejected: changes original evidence semantics and raises unjustified cost. |
| **Recommendation** | **Use an explicit, versioned `LocalizedRepresentation` owned by a localizable object version.** It carries BCP 47 locale, source-version reference, content, lifecycle status, and provenance. Canonical normative source is English (`en`); fallback is explicit and never silently alters source evidence. Evidence preserves its origin language; a localized interpretation is separate derived evidence with its own provenance. |
| Product Owner decision | Approve this representation model, canonical English/fallback rule, and which object categories are localizable in the MVP. |
| ADR | Required: **ADR-037 — Localization and canonical-language model**. |

## AC-06 — `ExecutionRun` and Operational Foundation Boundary

| Item | Assessment |
| --- | --- |
| Constitutional target | The AI Kernel Constitution gives the Kernel ownership of Execution. The Operational Foundation Constitution gives Operational Foundation queueing, scheduling, lease, retry, recovery, and delivery mechanics. Provider v2 and terminology documents mark `ExecutionRun` transitional/pending ADR. |
| Repository evidence | `ExecutionRun` is created by the dispatcher before `ExecutionJob`. Operational Foundation documentation still includes an `ExecutionRun` lifecycle reference, while Kernel documentation names `Execution`. |
| Finding | The current name and lifecycle coupling create an explicit constitutional boundary ambiguity: delivery/recovery mechanics are not the same as Kernel execution state. |
| Alternative A | Keep `ExecutionRun` as a shared OF/Kernel aggregate. Rejected: shared ownership defeats the constitutional boundary. |
| Alternative B | Rename every `ExecutionRun` occurrence to `Execution` without redesign. Rejected: a textual rename preserves incorrect lifecycle responsibilities. |
| **Recommendation** | **The canonical object is `Execution`, owned only by AI Kernel. `ExecutionRun` is removed rather than renamed in place.** Operational Foundation owns `OperationalWorkItem` delivery state; Kernel owns execution state. OF may request or resume Kernel work through immutable contracts, but may not transition Execution directly. A follow-up constitutional clarification is required only after Product Owner approval, because current transitional wording names `ExecutionRun`. |
| Product Owner decision | Approve the boundary and authorize the subsequent controlled constitutional/ADR convergence; do not amend the Constitution in this Sprint. |
| ADR | Required: **ADR-038 — Operational Work Item / Kernel Execution ownership boundary**. |

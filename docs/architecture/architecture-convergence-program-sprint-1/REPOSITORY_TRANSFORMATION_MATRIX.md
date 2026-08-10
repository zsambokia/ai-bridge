---
status: SUPPORTING
version: 0.1.0
---

# Repository Transformation Matrix

The full repository inventory was assessed by architectural responsibility;
this matrix groups files that share a transformation decision. It proposes no
code change in Sprint 1.

| Repository element | Current role | Classification | Required future transformation / rationale |
| --- | --- | --- | --- |
| `docs/constitution/BRIDGE_CONSTITUTION.md` | Governing charter. | Módosítani / ADR szükséges | Reconcile its single-product/non-tenant wording with tenant-ready platform capability after ADR-021. |
| `docs/architecture/ARCHITECTURE_CONSTITUTION.md`, `ARCHITECTURE_MAP.md` | Core technical law and topology. | Módosítani | Preserve laws; add intake, capability, AI Kernel/Execution, context, scope and locale chapters/links through controlled Book adoption. |
| `docs/runtime/runtime_2_0_constitution.md` | Runtime target. | Módosítani | Clarify Conversation adapter, Engine business-vs-operational state and Execution aggregate. |
| Foundation, Engine and State Machine Constitutions | Layer and ownership foundations. | Megtartani / Módosítani | Retain; align as Constitution Book chapters and add new invariants. |
| `ARCHITECTURE_EVOLUTION.md`, `ARCHITECTURE_BASELINE.md`, R20-00 evidence | Transition and audit history. | Migrálni | Link from Book transition register; label historical/transitional, never rewrite conclusions. |
| `docs/akb/*`, knowledge pipeline architecture | Governed knowledge and provenance. | Módosítani | Extend via Context Package and locale/scope contracts without taking AKB ownership from its domain. |
| `docs/architecture/ADRs/*` | Current accepted decisions. | Megtartani / Új elem | Preserve accepted ADRs; add ADR-020–029 only through later approval. |
| `projects/models.py` Project/Repository-related models | Project-centric identity. | Új elem / ADR szükséges | Historical assessment superseded by Article VI / ADR-035: introduce the Organization -> Workspace -> Project Scope hierarchy and a Scope-owned Repository Resource in an approved implementation Sprint; avoid collision with `ExecutionWorkspace`. |
| `projects/models.py` `ExecutionRun`, jobs, recovery, delivery, progress events | Reusable operational mechanics. | Migrálni / Alias megtartása | Bind to target Kernel-owned Execution through ADR-023; retain `ExecutionRun` attempt/recovery semantics until compatibility proof. |
| `projects/models.py` `FactoryMission`, conversation and MCP bindings | Current mission/conversation records. | Módosítani | Make Mission intake canonical and map human/external ingress adapters. |
| `projects/orki_runtime.py`, `workflow_engine.py`, workflow models | Orki/workflow orchestration; direct legacy route remains. | Migrálni | Strangle direct provider/workflow path behind Capability and Execution; do not delete before proof. |
| `projects/execution.py`, provider gateway/provider models | Execution/provider transport mechanisms. | Megtartani / Migrálni | Reuse behind the AI Kernel/Operational Foundation boundary; introduce Provider Integration/Resolver, Provider Binding, Kernel Profile, stateless Provider and stateful Provider Executor only after ADR-029, ADR-033 and ADR-034. |
| `projects/runtime_contract.py` | Pure runtime candidate contracts. | Megtartani | Extend only after ADR decisions; useful pattern for immutable contracts. |
| Knowledge context, entries, revisions, embeddings, pipeline receipts | Domain-specific knowledge context and evidence. | Módosítani | Preserve domain models; create generalized Context Package relationship rather than repurposing blindly. |
| Orki, cognitive, persona and reasoning models | Cognitive/domain state. | Módosítani | Keep business state in bounded contexts; add capability, scope and localization metadata where approved. |
| Execution/Provider/Orki/Workflow event models | Multiple audit/event streams. | Migrálni / ADR szükséges | Map to a canonical envelope/outbox/replay policy; retain source history. |
| Existing `ExecutionProvider` registry, Codex CLI adapter and provider audit history | Fixed-provider governed execution and append-only provider records. | Megtartani / Migrálni | Preserve as migration input; replace neither its audit history nor its governance checks. Decouple provider selection from resource management and executor lifecycle under ADR-029. |
| `projects/templates/**`, Factory Chat views/services | Human-facing UI with existing Hungarian copy. | Módosítani | Use a localization layer; Conversation remains human interaction, not universal intake. |
| `bridge/settings/*.py` | Django settings. | Módosítani | Establish i18n configuration only in localization implementation Sprint. |
| `projects/tests/**` | Existing behavioural and architecture evidence. | Módosítani | Preserve tests; add contract, isolation, recovery, locale and compatibility acceptance tests by phase. |
| `projects/migrations/**` | Current schema history. | Megtartani | Never alter history; future changes are additive, reversible migration plans. |
| This Sprint package and evidence record | Target/convergence evidence. | Új elem | Input to Book adoption and each later implementation Sprint. |

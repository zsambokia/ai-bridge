---
status: APPROVED_TARGET
scope: Architecture Convergence Program – Sprint 3
language: en
---

# Architecture Terminology Convergence Matrix

## Rules

Article III is the target canonical source for this terminology. This matrix
does not authorize a code or API rename. “Breaking?” describes a future
implementation change, not this documentation Sprint. Required retained terms
are Conversation, Mission, Mission State Machine (MSM), Operational Foundation,
Context Package, Persona, Capability, Evidence, Execution, Executor, Provider
and AKB.

| Current term / repository occurrence | Canonical target | Classification | Rationale | Impact | Breaking? |
| --- | --- | --- | --- | --- | --- |
| `Runtime` when it means the operational execution core | AI Kernel | Átnevezni | “AI Kernel” distinguishes the execution core from generic runtime activity. | New target docs and later active-doc changes. | Yes, if public symbols change. |
| `Runtime` in historical Runtime 2.0, accepted evidence or generic language | Retain as historical/generic Runtime | Historical | It may describe a historical document or a broader runtime concept, not the AI Kernel. | Do not bulk-rewrite. | No. |
| Runtime Services | Kernel Services | Átnevezni | Names the services in Article III precisely. | Documentation/architecture contracts first. | Potentially. |
| Runtime Configuration | Kernel Configuration | Átnevezni | Configuration belongs to the Kernel only where it configures its execution core. | Future configuration namespace review. | Potentially. |
| Runtime Scheduler | Kernel Scheduler | Átnevezni | Scheduler is a Kernel Service and has no business-priority authority. | Future service/API rename. | Potentially. |
| Runtime Lifecycle | Execution Lifecycle / Kernel Lifecycle | Átnevezni | Use Execution Lifecycle for state; Kernel Lifecycle only for Kernel service lifecycle. | Documentation distinction. | No now. |
| Runtime Telemetry | Kernel Telemetry | Átnevezni | Provider-neutral execution observation is a Kernel concern. | Future metrics naming. | Potentially. |
| `RuntimeEvent` / “Runtime Event” | Kernel Event for Article III technical state changes | Alias megtartása | Existing events may have different schemas and owners; ADR-027 must map them. | Introduce target name without rewriting streams. | Yes, after schema/API change. |
| `Engine` for a domain capability implementation | Capability Engine where clarity is needed | Alias megtartása | Capability is addressed first; “Engine” alone remains valid where its bounded-context role is already unambiguous. | Target docs; no blanket rename. | No now. |
| Engine Registry | Capability Registry, if it registers capability implementations | Új elem | No generic registry should be renamed unless its responsibility is capability discovery. | ADR-024 contract design. | Potentially. |
| Engine Resolution | Capability Resolution | Átnevezni | Resolution selects eligible capability providers/implementations, not an Engine by name. | Future routing contract. | Potentially. |
| Provider | Provider (stateless Capability Provider definition) | Megtartani | Required stable term; it is the canonical architectural object. | Provider documentation clarified. | No. |
| Provider Driver | Provider Driver as an implementation-level adapter alias | Alias megtartása | It may name a concrete adapter, but must not replace the architectural Provider term. | Avoids confusing a driver with the Provider definition. | No. |
| Provider Gateway | Provider Gateway, Kernel technical boundary | Megtartani / Migrálni | Existing gateway mechanics are reusable; target ownership and contracts change only through ADR-029/033. | Compatibility mapping. | Potentially. |
| Provider Executor | Provider Executor | Megtartani | Required stable stateful runtime-instance term. | New target contract; no present model rename. | No. |
| `ExecutionRun` | Execution (target aggregate); retain `ExecutionRun` transitional record | Alias megtartása | Current run has governed attempt, recovery and audit semantics that cannot be erased by renaming. | ADR-023 compatibility mapping. | Yes, if model/API renamed. |
| `ExecutionJob` | Technical job/attempt associated with Execution | Megtartani / Migrálni | A job is not necessarily the first-class Execution identity. | ADR-023. | Potentially. |
| `ExecutionRequest` (code type) | Execution Request (canonical prose); retain `ExecutionRequest` code alias | Alias megtartása | Code naming follows language convention; “Work Request” is too ambiguous with Mission/business work. | Documentation normalization only. | No. |
| `ExecutionWorkspace` | ExecutionWorkspace (physical workspace) | Megtartani | Must remain distinct from a tenant logical Workspace. | ADR-028 terminology reservation. | No. |
| Context Builder | Higher-layer Context/knowledge component | Megtartani / Migrálni | It supplies immutable Context Packages; it is explicitly not a Kernel Service. | Boundary clarification. | No now. |
| Operational Foundation | Operational Foundation | Megtartani | Required separate architectural layer, never an Engine, Runtime synonym or Kernel Service. | Documentation guards. | No. |
| Conversation, Mission, MSM, Context Package, Persona, Capability, Evidence, AKB | Same term | Megtartani | Product Owner-required canonical terms. | None beyond consistency checks. | No. |

## Repository evidence and disposition

| Repository element | Observed terminology | Sprint 3 disposition |
| --- | --- | --- |
| `docs/architecture/ARCHITECTURE_MAP.md`, `ARCHITECTURE_EVOLUTION.md` | `ExecutionRun`, Provider Gateway and Runtime-era topology. | Historical/transitional input; update only in a later Book-adoption Sprint. |
| `docs/runtime/runtime_2_0_constitution.md` | Existing Runtime 2.0 target terminology. | Retain; map through ADR-033, do not rewrite authority silently. |
| `docs/architecture/OPERATIONAL_FOUNDATION_CONSTITUTION.md` | Foundation owns mechanical delivery and Provider Gateway. | Retain as current foundation; reconcile boundary through adoption and ADR-029/033. |
| `projects/models.py`, `projects/execution.py`, recovery/delivery/activity modules | `ExecutionRun`, `ExecutionJob`, lifecycle and events. | Retain intact; future compatibility migration only. |
| `projects/decision_contract/framework.py` and `projects/runtime_contract.py` | `ExecutionRequest` and immutable contract patterns. | Retain source patterns; no `Work Request` rename. |
| Provider audit records and fixed Codex CLI path | Provider/Gateway implementation vocabulary. | Preserve immutable history and governed path; no compliance relabel. |

## Deprecation rule

A term becomes `Deprecated` only after ADR-backed compatibility mapping,
consumer migration, evidence of no remaining supported use and a documented
retirement date. Until then, aliases preserve implementation compatibility and
historical terminology remains discoverable.

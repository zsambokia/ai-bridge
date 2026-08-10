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
| Runtime Services | Kernel Managers, Kernel Registries or Kernel Objects, according to responsibility | Kivonni / Átnevezni | `Kernel Services` is no longer a canonical umbrella term; it conflates three distinct categories. | Documentation/architecture contracts first. | Potentially. |
| Runtime Configuration | Kernel Configuration | Átnevezni | Configuration belongs to the Kernel only where it configures its execution core. | Future configuration namespace review. | Potentially. |
| Runtime Scheduler | Kernel Scheduler | Átnevezni | Scheduler is a Kernel Service and has no business-priority authority. | Future service/API rename. | Potentially. |
| Runtime Lifecycle | Execution Lifecycle / Kernel Lifecycle | Átnevezni | Use Execution Lifecycle for state; Kernel Lifecycle only for Kernel service lifecycle. | Documentation distinction. | No now. |
| Runtime Telemetry | Kernel Telemetry | Átnevezni | Provider-neutral execution observation is a Kernel concern. | Future metrics naming. | Potentially. |
| Runtime Object | Kernel Object | Átnevezni | Use only for first-class technical objects in the AI Kernel boundary. | Future architecture and API terminology review. | Potentially. |
| Runtime State | Kernel State | Átnevezni | Use for AI Kernel technical state; preserve business state as MSM state. | State and event contract review. | Potentially. |
| Runtime Registry | Kernel Registry | Átnevezni | Use where the Registry governs a first-class Kernel Object. | Persistence and retention contract review. | Potentially. |
| Runtime Policy | Kernel Policy | Átnevezni | Use where policy governs Kernel technical behaviour, not business policy. | Policy namespace review. | Potentially. |
| Runtime Profile | Kernel Profile | Átnevezni | A Provider declares Kernel-supported execution behaviour; profile terms must not imply Provider ownership of the Kernel. | Provider contract terminology. | Potentially. |
| Runtime Resource | Kernel Resource | Átnevezni | Use for a resource governed by the execution core. | Resource and capacity terminology. | Potentially. |
| Runtime Queue | Kernel Queue | Átnevezni | Use only where the queue is part of the AI Kernel's technical execution boundary. | Queue compatibility review. | Potentially. |
| `RuntimeEvent` / “Runtime Event” | Kernel Event for Article III technical state changes | Alias megtartása | Existing events may have different schemas and owners; ADR-027 must map them. | Introduce target name without rewriting streams. | Yes, after schema/API change. |
| `Engine` for a domain capability implementation | Capability Engine where clarity is needed | Alias megtartása | Capability is addressed first; “Engine” alone remains valid where its bounded-context role is already unambiguous. | Target docs; no blanket rename. | No now. |
| Engine Registry | Engine Definition Registry | Átnevezni | An Engine-definition catalogue owns Engine definitions and remains distinct from Capability discovery. | ADR-024 contract design. | Potentially. |
| Capability Registry | Capability Registry | Megtartani / Új elem | It records Capability contracts and discovery independently of Engine definitions; it SHALL NOT replace the Engine Definition Registry. | ADR-024 contract design. | Potentially. |
| Engine Resolution | Capability Resolution | Átnevezni | Resolution selects eligible capability providers/implementations, not an Engine by name. | Future routing contract. | Potentially. |
| Provider | Provider (stateless Capability Provider definition) | Megtartani | Required stable term; it is the canonical architectural object. | Provider documentation clarified. | No. |
| Provider Driver | Provider Driver as an implementation-level adapter alias | Alias megtartása | It may name a concrete adapter, but must not replace the architectural Provider term. | Avoids confusing a driver with the Provider definition. | No. |
| Provider Gateway | Provider Integration adapter/boundary | Deprecated / Alias megtartása | The canonical sequence is Provider Integration → Provider Resolver → Provider → Provider Executor. Gateway may remain only as an implementation adapter, never a first-class architectural object. | Compatibility mapping through ADR-029/033. | Potentially. |
| Provider Executor | Provider Executor | Megtartani | Required stable stateful runtime-instance term. | New target contract; no present model rename. | No. |
| `ExecutionRun` | Execution (target aggregate); retain `ExecutionRun` transitional record | Alias megtartása | Current run has governed attempt, recovery and audit semantics that cannot be erased by renaming. | ADR-023 compatibility mapping. | Yes, if model/API renamed. |
| `ExecutionJob` | Undecided: retained implementation term or `Execution Attempt` | ADR szükséges | Its queue, lease, retry and recovery semantics cannot be inferred from the target Execution aggregate. No automatic rename is authorized. | ADR-034; retain unchanged until decision and compatibility proof. | Potentially. |
| `ExecutionRequest` (code type) | Execution Request (canonical prose); retain `ExecutionRequest` code alias | Alias megtartása | Code naming follows language convention; “Work Request” is too ambiguous with Mission/business work. | Documentation normalization only. | No. |
| `ExecutionWorkspace` | ExecutionWorkspace (physical workspace) | Megtartani | Must remain distinct from a tenant logical Workspace. | ADR-028 terminology reservation. | No. |
| Context Builder | Higher-layer Context/knowledge component | Megtartani / Migrálni | It supplies immutable Context Packages; it is explicitly not a Kernel Manager, Registry or Object. | Boundary clarification. | No now. |
| Operational Foundation | Operational Foundation | Megtartani | Required separate architectural layer, never an Engine, Runtime synonym or Kernel Manager, Registry or Object. | Documentation guards. | No. |
| Conversation, Mission, MSM, Context Package, Persona, Capability, Evidence, AKB | Same term | Megtartani | Product Owner-required canonical terms. | None beyond consistency checks. | No. |

## Uniform Kernel Object Pattern

The Constitution Book SHALL use this pattern for every first-class Kernel
Object, applying only the elements meaningful to the object:

```text
Definition → Registry → Instance → State Machine → Events → Evidence
```

| Object | Required pattern interpretation |
| --- | --- |
| Execution | Definition/Request, Execution Registry, Execution instance, Kernel State Machine, Kernel Events and immutable Evidence. |
| Provider | Provider definition, Engine Definition Registry/Capability Registry references as appropriate, Provider Executor instance, applicable lifecycle, Events and Evidence. |
| Lease | Lease definition/policy, applicable Kernel Registry, active lease instance, lease lifecycle, Events and Evidence. |
| Knowledge | Knowledge Object definition, Knowledge Registry, versioned Knowledge Object instance, lifecycle, Knowledge Events and provenance Evidence. |

The pattern does not mandate a separate database table or service for every
element. It makes ownership, identity, lifecycle, events and evidence explicit.
Exact persistence and compatibility decisions remain ADR-governed.

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

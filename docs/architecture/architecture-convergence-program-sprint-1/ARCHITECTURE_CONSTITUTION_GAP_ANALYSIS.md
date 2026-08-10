---
status: SUPPORTING
version: 0.1.0
---

# Architecture Constitution Gap Analysis

## Decision baseline

The Product Owner approved the following target state: Mission is the common
Runtime intake; Conversation is mandatory only for human interaction; the
Operational Foundation is an independent layer; Execution is first-class;
Capabilities, not Engines, are addressed; Context Packages are immutable,
versioned, reproducible, evidence-based and auditable; and the platform is
scope-aware, tenant-ready and localization-ready. These are target decisions,
not claims that the repository already implements them.

`Stateless Engine` means no operational execution state is owned by an Engine.
It does **not** prohibit a Domain Engine from owning durable business data in
its bounded context.

Provider Architecture v2.0 completes the corresponding external-execution
boundary: a Provider is a stateless resource definition; a Provider Executor
is the stateful, auditable and recoverable unit that performs one external
call. Provider selection belongs to the Operational Foundation's Provider
Resolver. Provider resource/capacity control remains with the selected
Provider. See [Provider Architecture v2.0](PROVIDER_ARCHITECTURE_V2.md).

## Material findings

| Area / current source | Current position | Target gap | Decision | Required next step |
| --- | --- | --- | --- | --- |
| Bridge Constitution preamble | Defines Bridge as neither a multi-tenant platform nor abstraction for hypothetical cases. | Conflicts with tenant-ready and scope-aware platform direction. | ADR szükséges | ADR and later constitutional amendment must distinguish platform readiness from immediate product tenancy. |
| Architecture Constitution | Establishes bounded domain ownership, MSM authority, immutable requests, Foundation handoff and evidence. | Does not explicitly define Mission Intake, Capability resolution, Context Package, scope, or localization. | Módosítani | Retain its laws and add the missing laws in the Book adoption Sprint. |
| Architecture Map | Correctly maps `Engine → Execution Request → MSM → Work Item → Foundation → ExecutionRun → Provider`. | It is Engine-addressed and lacks external intake, capability resolution and scope/locale boundaries. | Módosítani | Make it the Book navigation map and extend the target topology. |
| Runtime 2.0 Constitution | Already separates Mission, Engine and `ExecutionRun`; Foundation owns mechanical delivery. | Conversation is described as ingress; Engine wording permits persisted state without separating business and execution state; no canonical `Execution` aggregate. | Módosítani | Define Mission Intake Port, Execution-to-ExecutionRun relationship, and stateless-engine rule. |
| Operational Foundation Constitution | Establishes a provider-bound, reusable operational layer. | Its independent architectural status and contracts must be strengthened in the Book. | Megtartani / Módosítani | Preserve its ownership boundary; publish it as a Book chapter with capability and event contracts. |
| Provider architecture | Existing registry/gateway and fixed-provider execution mechanics are reusable, but the current implementation contains a hard-coded single-provider path. | No stateless Provider, Provider Executor, Executor Pool or Provider Resolver contract exists as the target boundary. | Új elem / ADR szükséges | Adopt Provider Architecture v2.0 through ADR-029 before implementation; preserve existing provider audit history. |
| Engine / State Machine Constitutions | Strong bounded-context and lifecycle-separation basis. | No Capability declaration/resolution contract; no explicit rule that execution state lives outside an Engine. | Módosítani | Add capability declaration/resolution and operational-state prohibition. |
| AKB Foundation and Knowledge Pipeline | Provide governed knowledge, evidence and a `KnowledgeContextPackage`. | No general Context Package contract, source manifest, reproducibility policy, scope or locale model. | Módosítani | Generalize only by a later ADR-backed contract; preserve AKB ownership. |
| Historical baseline / evolution records | Accurately record OESM/Orki and R20-00 as historical or transitional. | Need consistent Book-era status and migration references. | Átnevezni / Migrálni | Keep evidence immutable; classify records as `HISTORICAL` or `TRANSITIONAL`, never rewrite their conclusions. |
| Repository implementation | Reusable `ExecutionRun`, jobs, recovery, provider gateway, Factory Mission, knowledge and evidence components exist. Factory Chat/Orki still has a synchronous workflow/provider route; R20-00 finds no E2E MSM route. | Target route and contracts are not yet implemented. | Migrálni | Use the staged map; do not equate reusable components with constitutional compliance. |
| Project scope model | `Project` provides project identity/isolation. | There is no Organization, tenancy scope hierarchy, scoped authorization, or repository ownership hierarchy. | Új elem / ADR szükséges | Decide hierarchy and enforcement model before data-model work. |
| Localization | UI includes Hungarian strings; project settings do not establish a platform i18n model. | No locale fallback, localized prompt/persona/knowledge/document model, or canonical-to-derived governance. | Új elem / ADR szükséges | Establish language architecture before translations or localized content migration. |

## Target topology (conceptual)

```text
Human Conversation ─┐
API / MCP / Scheduler / Webhook / Automation ─┴─> Mission Intake Port
                                                    │
                                                    v
Scope + policy + Context Package ───────────────> Mission
                                                    │
                                                    v
                                             Capability resolution
                                                    │
                                                    v
                                              Execution (aggregate)
                                                    │
                                                    v
Operational Foundation → ExecutionRun → Provider Resolver → Provider → Provider Executor
```

Each arrow must carry correlation, scope, policy and evidence references.
Capabilities are resolved independently of Providers. An Engine, Tool or Agent
may implement a Capability; the Provider is the selected external-resource
boundary and does not own Mission or operational Execution state.

## Explicit non-decisions

This analysis does not choose the tenant hierarchy, authorization technology,
Execution schema, Context Package storage layout, localization framework,
event-bus product, or the mapping between existing `ExecutionRun` and the
target Execution aggregate. Provider Executor persistence, pool topology and
the provider-selection policy are governed by ADR-029 before implementation.

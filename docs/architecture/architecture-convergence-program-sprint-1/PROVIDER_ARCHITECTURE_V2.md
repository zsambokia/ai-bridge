---
status: APPROVED_TARGET
version: 2.0.0
scope: Architecture Convergence Program – Sprint 1 addendum
---

# Provider Architecture v2.0

## Decision

The AI Kernel addresses external execution through Provider contracts, never by
coupling directly to a vendor such as OpenAI, Anthropic, Codex or an MCP
server. A Provider does not execute a request itself: it supplies or reserves
a Provider Executor that performs the external call.

This is an approved target architecture. It is not an implementation change,
an amendment to an existing canonical Constitution, or a claim that the
current fixed-provider path is compliant.

## Invariants

1. **Stateless Provider.** A Provider is a versioned resource definition. It
   declares capabilities, configuration schema, authentication requirements,
   health, limits, priority, availability and cost model. It owns no per-call
   Context Package, lease, retry state, Persona session, Evidence, Telemetry,
   Usage, Output or execution state.
2. **Stateful Provider Executor.** Every external call is performed by a
   Provider Executor. It is auditable, restartable, leaseable and retryable;
   it carries the correlation to its Execution, selected Provider, Capability,
   Context Package, configuration, timeout, policy, telemetry, evidence,
   usage, cost, output and lifecycle state.
3. **Provider-owned resources.** The Provider owns executor-pool reservation
   and release, concurrency limits, rate limits, quota, connection resources
   and provider-specific cost limits. The Runtime does not reimplement those
   resource details.
4. **Capability independence.** A Capability is resolved independently of a
   Provider. The same Capability may be fulfilled through more than one
   eligible Provider. Provider support is an eligibility declaration, not
   Capability ownership.
5. **Foundation-owned selection.** The Provider Resolver is an Operational
   Foundation component. It selects an eligible Provider according to
   capability, policy, health, priority, cost and capacity, and applies
   governed fallback, failover and load-balancing policy.
6. **Explicit capacity outcomes.** If no Executor can be reserved, the
   Provider reports capacity exhaustion. The Operational Foundation may queue,
   choose another eligible Provider or fail according to policy. Silent
   fallback is prohibited.
7. **Immutable Provider Binding.** The selected Provider is bound to an
   Execution before external work begins and SHALL NOT change during that
   Execution. Cross-provider failover is prohibited after the binding exists.
8. **Same-Provider recovery.** A failed Provider Executor may be replaced or
   reattached only by the same bound Provider. If recovery is unavailable or
   unsafe, the Execution becomes an explicit awaiting-provider, blocked or
   failed outcome; it never silently uses a different Provider.
9. **Runtime Profile.** Every Provider publishes a versioned Runtime Profile
   declaring supported checkpoint, resume, recovery, migration, streaming,
   lease, timeout, concurrency and retry behaviour. The Kernel and Foundation
   enforce that declared profile rather than inferring provider behaviour.

## Responsibilities

| Component | Owns | Must not own |
| --- | --- | --- |
| Capability Resolver | Capability discovery and eligibility of implementations | Vendor selection, executor capacity or external-call state |
| Engine | Domain capability implementation and bounded-context business state | Operational execution state |
| Operational Foundation / Provider Resolver | Policy-governed pre-binding Provider selection, fallback decision and correlation | Provider-specific pool mechanics or post-binding provider switching |
| Provider | Stateless definition and provider-specific resource/pool management | Per-call execution state or Mission authority |
| Provider Executor | One external-call lifecycle, lease/retry/evidence/telemetry/output | Mission authority or cross-provider selection policy |

## Target flow

```text
Mission → MSM → Operational Foundation → immutable Execution Request
  → AI Kernel → Capability Resolution → Provider Resolver → bind Provider
  → reserve Provider Executor → External Service → result/evidence/telemetry
  → Execution update / Kernel Event → MSM
```

`ExecutionRun` remains a reusable existing attempt/recovery record until an
ADR-backed migration defines its exact relationship to Execution and Provider
Executor. Existing provider audit history remains immutable migration input.

## Provider Executor lifecycle

```text
Created → Reserved → Preparing → Running → Waiting Provider → Retry → Completed
                                         └──────────────→ Failed | Cancelled |
                                                              Timed Out | Recovered
```

An Executor returns to its Provider pool only after its terminal lifecycle,
evidence and resource-release requirements have been satisfied.

## Required ADR and implementation boundary

[ADR-029](ADR_RECOMMENDATION_LIST.md) is required before implementation. It
must decide persistence and identity of Provider Executors, pool topology,
pre-binding selection/fallback policy, immutable Provider Binding,
same-Provider recovery, Runtime Profile schema, capacity/error contracts,
authorization, secrets, event/replay compatibility, and the migration from the
existing fixed-provider gateway. No current provider model, AI Kernel/Runtime,
Workflow Engine, schema or adapter is changed by this addendum.

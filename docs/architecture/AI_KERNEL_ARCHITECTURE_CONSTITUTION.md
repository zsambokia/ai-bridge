---
status: APPROVED_TARGET
version: 1.0.0
scope: Architecture Convergence Program – Sprint 3
language: en
---

# Article III – AI Kernel Architecture

## Status and authority

This is an approved target Constitution Book entry. It records the Product
Owner-approved architectural direction; it does not assert that the current
repository implements it. Existing Constitutions and accepted ADRs retain
their current authority until a controlled Book-adoption Sprint changes that
status. All normative terms in this entry are English.

## 3.1 Purpose of the AI Kernel

The AI Kernel is AI Bridge's operational execution core. It transforms an
immutable Execution Request into a managed, observable, secure and
reproducible Execution. It begins after the Operational Foundation has
admitted the request and ends after the result, evidence and Kernel Events are
persisted.

The AI Kernel executes; it does not decide. The Mission State Machine (MSM)
owns business-process state and decides what happens next. Operational
Foundation is a separate architectural layer: it is neither an Engine nor a
Kernel Service. Human interactions start in Conversation; API, MCP, Scheduler,
Webhook and Automation adapters converge on the same Mission intake model.

## 3.2 Responsibilities and boundaries

The AI Kernel SHALL manage Execution lifecycle, scheduling, capability
resolution, immutable Context Package binding, Provider Executor coordination,
leases, technical recovery, telemetry, evidence, security and Kernel Events.
It SHALL NOT contain business logic, orchestrate a Mission, own Mission state,
build business Context, change a Context Package, or communicate with an
external system except through a Provider and its Provider Executor.

The Kernel implementation is stateless. Durable operational state belongs to
first-class runtime objects such as Execution, Lease, Provider Executor,
Evidence and Telemetry. Bounded-context business data may remain with its
Domain/Capability Engine and does not violate this rule.

## 3.3 AI Kernel Services

Kernel Services cooperate through defined technical contracts and each owns one
technical responsibility. They do not own business decisions.

| Service | Responsibility | Exclusion |
| --- | --- | --- |
| Execution Manager | Create, start, stop, cancel and coordinate Executions. | Performing provider work itself. |
| Execution Registry | Authoritative identity, correlation, lifecycle and history record. | Business-data duplication or dispatch. |
| Kernel Scheduler | Decide when an admitted Execution may start. | Business priority, workflow progression or Provider policy. |
| Capability Resolver | Resolve requested Capability to eligible implementation/Provider candidates. | Business intent. |
| Provider Gateway | Exclusive technical gateway to Provider Executors. | Mission ownership or Context construction. |
| Lease Manager | Acquire, renew, expire and release technical leases. | Business waiting. |
| Recovery Manager | Recover an existing Execution safely. | Replacing the Execution or changing Mission state. |
| Kernel Telemetry and Evidence Managers | Record provider-neutral observations and immutable evidence. | Business interpretation. |
| Kernel Configuration and Security Managers | Govern versioned configuration, isolation, authorization and secrets. | Unauthorised cross-scope access. |
| Kernel Event Dispatcher | Publish immutable technical state-change events. | Triggering business workflow progression. |

Context Builder is deliberately not a Kernel Service. It belongs to the
higher-layer Context/knowledge boundary and supplies a completed immutable
Context Package to the Kernel.

## 3.4 Execution Model

Execution is the first-class, stateful technical object. An Execution is not a
Mission, Workflow or Engine invocation. Every Execution originates from one
immutable Execution Request and records at least its identity, requested
Capability, Context Package version, Provider Binding, scope/owner,
correlation, status, lease, timestamps, Evidence references and Telemetry
references.

The AI Kernel exclusively owns Execution state. An Engine provides a
Capability; it does not run or own an Execution. A Provider executes work; it
does not own the Execution. The compatibility relationship between the target
Execution aggregate and the existing `ExecutionRun`, jobs and recovery records
is intentionally deferred to ADR-023.

## 3.5 Execution Lifecycle and State Machine

The Kernel SHALL use a deterministic technical state machine. Valid canonical
states are `Created`, `Scheduled`, `Preparing`, `Running`, `Waiting`, `Retry`,
`Cancelling`, `Completed`, `Failed` and `Cancelled`. `Completed`, `Failed` and
`Cancelled` are terminal. Every accepted transition is validated, append-only,
and emits exactly one Kernel Event.

```text
Created → Scheduled → Preparing → Running → Completed
                                  ├→ Waiting → Running
                                  ├→ Retry → Preparing
                                  ├→ Cancelling → Cancelled
                                  └→ Failed
```

`Waiting` represents only a technical dependency such as provider response,
resource availability or an external callback. Business approval/waiting stays
in the MSM. Recovery continues the same Execution identity when safe; it never
silently creates a replacement Execution.

## 3.6 Execution Registry

Every Execution SHALL be registered exactly once in the authoritative
Execution Registry. The Registry preserves globally unique identity,
correlation, parent-child links, lifecycle history and retention references for
active and historical Executions. Identity is immutable and history is
append-only. Correlation does not imply ownership.

The Registry pattern may be applied to other first-class operational objects
(for example Lease and Provider Executor), but this article establishes only
the Execution Registry as mandatory. The exact persistence topology remains an
implementation decision.

## 3.7 Capability Resolution

The platform addresses Capabilities, never provider, Engine or tool names.
Every Execution Request declares its required Capability and applicable
version. Before start, the Kernel resolves eligible Providers using declared
Capability support, Runtime Profile, availability, authorization, scope,
security and deterministic policy constraints. Capability versions evolve
independently of Provider versions.

Provider selection happens only after eligibility is established and is
recorded as the immutable Provider Binding. If no eligible Provider exists, the
Execution does not start; the Kernel produces structured resolution evidence
and a Kernel Event. Provider fallback is allowed only before an Execution is
bound and only when explicit selection policy permits it.

## 3.8 Context Integration

Every Execution SHALL reference one immutable, versioned, reproducible,
evidence-based and auditable Context Package. The Context Package exists before
execution begins; the Kernel only binds and delivers it. The Kernel never
constructs, enriches or mutates business Context.

Context Package validity is explicit. A stale or invalid package may be
consumed only under an explicit policy recorded in Evidence; otherwise the
Execution is blocked until a valid package is supplied. Knowledge References in
the package preserve Knowledge Object identity and version rather than copying
knowledge into the Execution.

## 3.9 Provider Integration

A **Provider** is a stateless Capability Provider definition: it declares
supported Capabilities, configuration, authentication method, timeout,
concurrency and retry rules, and a Runtime Profile. A Provider contains no
Execution, Context, Mission, Evidence or per-call operational state.

A **Provider Executor** is the stateful runtime instance created or reserved
by its Provider. It may carry workspace, session, cache, temporary files,
processes and provider-specific recovery state. It is replaceable within the
same Provider; it is never the owner of an Execution.

Provider Binding is immutable for an Execution. Once bound, no automatic
cross-provider switch or failover is allowed. Recovery may create or reserve a
new Provider Executor only with the same Provider and only if its Runtime
Profile permits recovery. Provider unavailability produces an explicit
`Awaiting Provider`, blocked or failed technical outcome according to policy;
it never silently selects another Provider.

Every Provider SHALL publish a versioned Runtime Profile that declares, at a
minimum, supported checkpoint, resume, recovery, migration, streaming and
lease behaviour. A Provider may execute work only; it shall not make business
decisions, modify a Mission or build Context.

## 3.10 Kernel Events

Kernel Events are immutable, provider-neutral records of technical state
changes, including `ExecutionCreated`, `ExecutionScheduled`,
`ExecutionPreparing`, `ExecutionStarted`, `ExecutionWaiting`,
`ExecutionRetrying`, `ExecutionCompleted`, `ExecutionFailed`,
`ExecutionCancelling` and `ExecutionCancelled`. Consumers may interpret these
events, but the events themselves neither encode business progression nor
trigger it. Canonical event-envelope and replay decisions remain under ADR-027.

## 3.11 Recovery

Recovery is a normal technical capability. It validates the existing
Execution, immutable Provider Binding, Context Package version, checkpoint and
lease before resuming. It preserves identity and append-only history. When
safe continuation is impossible, the Execution transitions to `Failed` with
structured evidence. Recovery never substitutes another Provider.

## 3.12 Lease Management

Leases protect exclusive technical ownership of an Execution or Provider
Executor. Lease acquisition, renewal, expiry, release and ownership changes
are observable, scope-aware and auditable. Lease loss pauses or fails technical
execution under policy; it cannot advance a Mission or alter business state.

## 3.13 Scheduling

Kernel Scheduler determines when an admitted Execution receives technical
resources. Its inputs may include priority supplied by higher layers,
capacity, lease status, Provider Runtime Profile, concurrency and applicable
scope/security policies. It does not determine business priority or the next
workflow step. Scheduling decisions are reproducible from their recorded
inputs and configuration version.

## 3.14 Kernel Telemetry

The Kernel records provider-neutral execution duration, queue time, Provider
latency, resource usage, retries, failures and recovery activity. Telemetry is
correlated to Execution and scope and is retained separately from business
state. Provider-specific metrics may be attached without becoming Kernel
control logic.

## 3.15 Evidence

Every Execution SHALL produce immutable Evidence sufficient to establish its
request, Context Package version, Capability, Provider Binding, Executor
attempts, state transitions, outputs, failures and recovery decisions. Evidence
is attributable, traceable and suitable for audit; it is not optional logging.

## 3.16 Security

Kernel Security enforces authenticated, authorized and scope-aware access to
Execution, Context, Evidence, Provider credentials and Executor resources.
It supports the platform's tenant-ready Organization/Workspace/Repository
scope model and prevents cross-scope data or executor access. Secrets are
provided only through governed Provider integration and never recorded in
Context, Events, Telemetry or Evidence. Localization does not change canonical
identifiers, authorization or evidence semantics.

## 3.17 AI Kernel Invariants

1. **AK-001:** The Kernel SHALL NOT implement business logic or orchestrate business workflows.
2. **AK-002:** MSM exclusively owns business-process state.
3. **AK-003:** The Kernel accepts immutable Execution Requests only.
4. **AK-004:** The Kernel never mutates or constructs a Context Package.
5. **AK-005:** The Kernel executes external work through Providers and Provider Executors only.
6. **AK-006:** Capability addressing and Provider selection are deterministic and auditable.
7. **AK-007:** Execution is Kernel-owned; Engine and Provider are not its owners.
8. **AK-008:** Provider Binding is immutable for the Execution lifecycle.
9. **AK-009:** Recovery preserves Execution identity and stays within the bound Provider.
10. **AK-010:** Execution history, Evidence and state-transition Events are append-only.
11. **AK-011:** Every Execution is observable, attributable and evidence-producing.
12. **AK-012:** Scope authorization applies to all Kernel objects and operations.

## 3.18 AI Kernel Principles

The Kernel executes, not decides. It manages Executions, not Missions. It owns
technical coordination, not business state. It is provider-independent even
though a particular Execution has an immutable Provider Binding. Everything it
executes is reproducible, observable, attributable and evidence-backed.

## 3.19 AI Kernel Architecture Diagram

```text
Human: Conversation ─┐
API / MCP / Scheduler / Webhook / Automation ─┤
                                              ▼
                                           Mission
                                              ▼
                                            MSM
                                              ▼
                                Operational Foundation
                                              ▼
                              immutable Execution Request
                                              ▼
┌──────────────────────────────── AI Kernel ──────────────────────────────┐
│ Execution → Capability Resolution → immutable Provider Binding           │
│      │             │                         │                            │
│      ├─ Context Package (read-only)          └─ Provider Executor        │
│      ├─ Registry / Lease / Scheduler / Recovery       │                   │
│      └─ Kernel Events / Telemetry / Evidence          ▼                   │
└──────────────────────────────────────────────── External system ─────────┘
                                              │
                                              ▼
                                   Execution update / Kernel Event → MSM
```

## Controlled convergence

Implementation requires accepted ADR-023 (Execution compatibility), ADR-024
(Capability contract), ADR-025 (Context Package), ADR-027 (events), ADR-029
(Provider architecture) and ADR-033 (AI Kernel terminology and boundary
transition). This entry neither renames repository symbols nor changes Runtime,
Workflow Engine, models, data, APIs or provider behaviour.

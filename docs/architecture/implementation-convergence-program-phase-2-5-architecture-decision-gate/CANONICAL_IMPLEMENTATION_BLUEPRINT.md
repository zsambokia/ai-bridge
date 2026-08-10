# Canonical Implementation Blueprint

## Status and use

This is the recommended canonical model for Product Owner review. It becomes an implementation contract only when the decisions in the [Architecture Challenge Register](ARCHITECTURE_CHALLENGE_REGISTER.md) are accepted. It does not amend the Constitution.

## Canonical control flow

```text
Human interaction
    -> Conversation
    -> Mission intake / update
    -> Mission State Machine authorization
    -> immutable OperationalWorkItem specification
    -> Operational Foundation delivery mechanics
       (queue, schedule, lease, retry, recovery delivery)
    -> immutable ExecutionRequest
    -> AI Kernel creates or resumes Execution
    -> Capability Resolution
    -> Provider Integration -> Provider Resolver
    -> immutable ProviderBinding -> Provider -> ProviderExecutor
    -> external LLM / MCP / Tool / Human / API
    -> Provider response, Evidence, and Kernel Events
    -> Kernel updates Execution
    -> Mission State Machine receives the authorized outcome
```

Conversation is required for human interaction, not for API, MCP, Scheduler, Webhook, or Automation entry. Every entry route converges on Mission intake, and only an MSM-authorized Operational Work Item may request Kernel execution.

## Boundary rules

1. Mission and Mission State Machine own business intent and its authorized lifecycle; they do not own delivery leases or provider sessions.
2. Operational Foundation owns the durable delivery envelope, queue, scheduling, lease, retry, and recovery-delivery mechanics of an `OperationalWorkItem`; it does not own Kernel Execution state.
3. AI Kernel owns `Execution`, its state machine, event stream, immutable Provider Binding, capability resolution, and execution evidence correlation.
4. Provider Integration resolves a Provider. A Provider is a stateless capability provider; its `ProviderExecutor` is a stateful resource. The executor may be replaced only by the same bound Provider according to its Runtime Profile.
5. A Context Package is immutable and versioned. The Kernel consumes it read-only through Knowledge References that pin Knowledge Object versions.
6. AKB and Knowledge Lifecycle Management are independent of runtime execution. They publish immutable knowledge versions and invalidate context according to policy.
7. Evidence and events are append-only. A source may emit evidence but cannot rewrite already published evidence.

## Canonical first-class objects

| Object | Owner / lifecycle authority | Persisted? | Mutability | Canonical relationship |
| --- | --- | --- | --- | --- |
| Organization | Identity and authorization domain | Yes | Controlled lifecycle | Tenant and authorization root. |
| Workspace | Organization | Yes | Controlled lifecycle | Logical operating scope; contains repositories. |
| Repository | Workspace | Yes | Controlled lifecycle | Source, knowledge, and provenance boundary. |
| Project | Repository | Yes | Controlled lifecycle | Governed product context; root owner for operational objects. |
| Conversation | Conversation domain | Yes | Message history is append-only; conversation state controlled | Human interaction entry only; may inform Mission intake. |
| Mission | Mission domain / MSM | Yes | State transitions only through MSM | Expresses intent and business lifecycle. |
| Mission State Machine | Mission domain | Transition/event record | Deterministic transitions | Sole authority for Mission lifecycle and Operational Work Item authorization. |
| OperationalWorkItem | Operational Foundation | Yes | Immutable authorized specification; separate mutable delivery state | Delivery envelope for one authorized unit of work; replaces historical `ExecutionJob`. |
| ExecutionRequest | Operational Foundation to AI Kernel contract | Yes, as immutable contract or event payload | Immutable | Requests creation/resumption of a Kernel Execution; includes scope, capability, context reference, and work correlation. |
| Execution | AI Kernel | Yes | State changes only through Kernel state machine and events | One first-class kernel execution. Replaces historical `ExecutionRun`; never owned by Provider or Operational Foundation. |
| ProviderBinding | AI Kernel | Yes | Immutable once Execution is admitted | Associates exactly one Provider with an Execution. |
| Provider | Provider Integration / definition registry | Yes | Versioned definition; stateless | Declares capabilities and Runtime Profile. |
| ProviderExecutor | Bound Provider resource lifecycle; Kernel correlates | Durable correlation record plus volatile resource as required | Stateful, replaceable only by same Provider | Performs the bound external invocation; it does not own Execution. |
| ContextPackage | Context / knowledge boundary | Yes | Immutable and versioned | Supplies reproducible execution context through pinned Knowledge References. |
| KnowledgeObject | AKB | Yes | Stable identity; lifecycle controlled | Typed knowledge root with a stable `knowledge://` URI. |
| KnowledgeObjectVersion | AKB / KLM publication | Yes | Immutable after publication | Versioned content, provenance, language, and confidence for a Knowledge Object. |
| KnowledgeRelationship | AKB / KLM publication | Yes | Versioned and provenance-bearing | Graph edge between knowledge objects/versions. |
| KnowledgeReference | Context Package | Yes, in immutable manifest | Immutable | Pins a Knowledge Object version selected for a context. |
| Evidence | Evidence domain / producing component | Yes | Append-only and immutable | Traceable observation, result, or decision input. |
| KernelEvent | AI Kernel | Yes | Append-only and immutable | Provider-neutral execution event correlated to an Execution. |

`ExecutionAttempt` is deliberately not a first-class object in this MVP blueprint. Provider executor/invocation, retry, checkpoint, recovery, and failure facts are correlated event/evidence records. A future aggregate needs a distinct lifecycle and an ADR; a repeated provider call alone is not sufficient justification.

## State ownership model

```text
Mission state                  -> Mission State Machine
Operational delivery state     -> OperationalWorkItem / Operational Foundation
Kernel execution state         -> Execution / AI Kernel
Provider resource state        -> ProviderExecutor / bound Provider
Knowledge lifecycle state      -> KnowledgeObject / Knowledge Lifecycle Management
Context validity               -> ContextPackage / Context Invalidation policy
```

No state machine crosses these ownership boundaries. Components exchange immutable contracts, events, evidence, and references instead.

## Canonical terminology decisions in the blueprint

| Historical implementation term | Canonical fate |
| --- | --- |
| `OrkiExecution` | Decompose into Conversation/Mission/MSM intake and outcome projection; remove as a canonical runtime aggregate. |
| `ExecutionRun` | Replace with Kernel-owned `Execution`; do not perform a blind rename. |
| `ExecutionJob` | Replace with Operational-Foundation-owned `OperationalWorkItem`; do not treat it as an attempt. |
| Provider Gateway | Internal Provider Integration adapter/boundary, not a first-class canonical object. |
| Runtime Event / Runtime State | Kernel Event / Kernel State where the subject is the AI Kernel. |
| Physical Execution Workspace | Provider executor resource; distinct from logical Workspace scope. |

## Minimum canonical persistence boundary

The canonical data design is intentionally aggregate-first, not table-first. At implementation design time it must persist at least: scope hierarchy; Mission and MSM transitions; Operational Work Item and lease/delivery transitions; Execution and Kernel Events; immutable Provider Binding; executor/invocation correlation; immutable Context Package manifest; Knowledge Object identities/versions/relationships; and Evidence. No existing schema is authoritative merely because it already stores similar fields.

## Non-goals

- No compatibility API, alias, dual-write, or historical projection is assumed.
- No data reset, deletion, external migration, or code/database change is authorized by this document.
- No provider fallback across an immutable Provider Binding is permitted.
- No direct AKB document editing is introduced; publication remains a knowledge lifecycle action.

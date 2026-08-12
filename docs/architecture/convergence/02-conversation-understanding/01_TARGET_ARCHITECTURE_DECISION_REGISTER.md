# 02 — Target Architecture Decision Register

Status: **APPROVED TARGET ARCHITECTURE**

This register records the decisions reached in section 02. It distinguishes target architecture from current implementation and from the pre-existing Constitution.

## A. Cognitive Processing

### CP-01 — Understanding is a stateless capability
`Understanding` is a reusable, stateless AI Bridge capability. `Conversation Understanding` is one application of it, not a stateful domain owner.

### CP-02 — Context → Understanding → Evaluation
The canonical cognitive-processing pattern is:

`Effective Scope / Profile → Context Assembly → immutable Context Package → Understanding → immutable Understanding Result → Evaluation → immutable Evaluation Result → Domain Authority`.

### CP-03 — Understanding is not authority
Understanding may observe, interpret, resolve references, identify ambiguity and infer meaning, but it may not mutate domain state or decide domain consequences.

### CP-04 — Result ≠ consequence
Understanding Result and Evaluation Result are immutable processing results. The relevant Domain Authority owns the state transition or business consequence.

### CP-05 — Historical validity ≠ current applicability
An immutable result remains a historical fact about what was produced from a specific input/context/profile. Later use for a new consequence requires applicability evaluation where policy requires it.

### CP-06 — Cognitive Profile
A Cognitive Profile is a versioned processing contract, not merely a prompt. It can bind context policy, understanding policy and evaluation policy. Stateless services operate from a pre-resolved Effective Scope and applicable profile/policy; they do not invent their own operational context.

## B. Factory Protocol foundation

### FP-L0 — Effective Operational Scope & Isolation
L0 establishes the effective operational scope and isolation boundary for a governed handoff. It may include scope identity plus resolved resource/policy/profile bindings and resolution provenance. Stateless services do not independently resolve their own operating scope.

### FP-L1 — Evidence Protocol
Evidence proves or supports facts; it is not logging, a decision engine or domain authority. Architecturally significant handoffs/transitions produce immutable, integrity-verifiable Evidence according to applicable contracts. The domain owns the semantic fact; Evidence Infrastructure owns recording, integrity and retrieval. Evidence sufficiency is evaluated separately from domain consequence.

### FP-L2 — Provenance & Causality Protocol
Provenance/Causality is an independent logical graph connecting first-class objects with semantically typed relations. Evidence may support a relation but is not the relation itself.

Canonical relation design uses a small stable family set with controlled, versioned specializations. Ad-hoc runtime relation types are forbidden. Every relation has one authoritative direction; inverse navigation is a query/projection, not a separately persisted fact.

Materialized relations are append-only historical facts. Source, target and semantics are immutable. Lifecycle may evolve through `PENDING`, `ACTIVE`, `RETRACTED`, `SUPERSEDED` according to policy. `PENDING` is a governance state, not a mandatory starting state.

Relation authority and activation evidence requirements belong to the versioned Relation Definition/Registry. Provenance Infrastructure records and manages relations but does not become domain authority.

Evidence challenge does not automatically retract a relation. Evidence assurance is represented by immutable Evaluation Results with canonical outcomes such as `SUFFICIENT`, `DEGRADED`, `INSUFFICIENT`, `INDETERMINATE`; it is not a second mutable relation state machine.

A relation is normally a canonical typed graph edge. A first-class Relation Record is required only when its canonical definition requires independent persistence, authority, evidence or lifecycle semantics.

### FP-L3 — Artifact Protocol
An output becomes a canonical Artifact only when an applicable versioned Artifact Contract qualifies it. Producers may not self-declare arbitrary outputs as canonical Artifacts.

Artifact Identity is stable; Artifact Versions are immutable. Historical references must target the concrete Artifact Version, not a mutable `latest` alias. A new version represents a new materialization of the same semantic purpose/contract; a changed semantic purpose requires a new Artifact Identity.

Artifact Version is a canonical metadata/identity record and is distinct from its payload. Persistent versions require verifiable content integrity. Payload mutation cannot mutate an existing version.

Artifact Contract governs qualification, semantic purpose, identity/versioning, persistence, integrity, composition/dependencies, applicability, retention/availability/scope, governance/lifecycle and lifecycle authority as applicable.

Artifact Infrastructure owns materialization/storage/integrity/version mechanics. Domain-specific lifecycle meaning and consequences belong to the Domain Authority designated by contract.

Artifact is not a special Evidence subtype. Evidence Records may reference an Artifact Version for a specific proof purpose without changing the Artifact's identity.

### FP-L3 — Artifact → Knowledge boundary
A complete Artifact Version does not automatically become AKB Knowledge. Knowledge Publication identifies semantically independent knowledge units with their own identity, type, status, version and provenance.

`Knowledge Candidate` is a first-class immutable provenance-linked intermediate object, but is not yet canonical Knowledge. Understanding may produce candidates; it may not publish directly into AKB.

Publication Resolution is not binary. Canonical outcomes include `CREATE`, `REVISE`, `CONFIRM`, `DUPLICATE`, `CONFLICT`, `REJECT`. Evaluation classifies the candidate's relationship to existing Knowledge; Knowledge Domain Authority owns the publication consequence.

Conflict detection does not automatically invalidate current canonical Knowledge.

## C. Resolution / unresolved authority work

### RES-01 — Resolution Protocol concept
The system requires a standard mechanism for cases a domain cannot or may not resolve itself. A Resolution Subject may include Claim, Decision Request, Input Request and future controlled types. Resolution carries authority requirements, required context/evidence, an authoritative result and a domain consequence.

### RES-02 — Claim
A Claim is more than a free-text assertion: it is a governed, scoped assertion with provenance, applicable policy/contract and an authority/resolution obligation. Claim is one Resolution Subject, not the whole resolution architecture.

## D. L4 / FactoryIP

### FP-L4 — Transport Layer
L4 is the transport layer for semantic domain/protocol-boundary communication. Not every internal service call is a Factory message/packet.

The full L0–L4 communication stack is named **FactoryIP**. The transported unit is a **Factory Packet**. Each protocol layer owns only its own semantics and need not understand the internal semantics of other layers.

### FIP-01 — FactoryIP is not CRUD
FactoryIP is the canonical semantic inter-domain communication protocol. HTTP, MCP, WebSocket or other access technologies may be adapters, but they may not bypass canonical FactoryIP domain boundaries to mutate/read internal domain state directly.

### FIP-02 — FactoryIP Node
A FactoryIP Node is an independently addressable service boundary on the Factory LAN, not necessarily an internal component/process. Node identity, exposed service identity and technical endpoint/location are separate concepts. Internal implementation is hidden behind published semantic services.

A domain/component qualifies as a Node only when it represents a stable service boundary, legitimate inter-node communication is required, and its implementation can remain hidden behind that boundary.

### FIP-03 — Published services
Published services are semantic contracts, not database CRUD endpoints. For the Conversation Node, the approved service families are:

- `conversation.interaction`
- `conversation.context`
- `conversation.projection`

Direct `conversation.create/update/delete`, `message.create/update`, or `state.set/transition` LAN services are not canonical.

### FIP-04 — Factory Fabric Service
The **Factory Fabric Service (FFS)** is the FactoryIP name/service resolution control-plane concept. It resolves stable logical FactoryIP identities/services to transport bindings/endpoints. Payload traffic does not flow through FFS.

For MVP, FFS should remain deliberately thin; dynamic discovery, leases, heartbeats, load balancing, distributed registry and active-active clustering are not prerequisites unless later topology requirements justify them.

### FIP-05 — Zoning
Zoning is the single canonical FactoryIP communication-permission mechanism at the transport topology level. It determines which source/destination services may communicate in an Effective Scope. Domain authorization remains separate. Zoning must be finalized only after the Node/service topology is known; do not prematurely freeze an ALLOW/DENY matrix.

## E. Existing canonical principles explicitly preserved

The following baseline principles remain intact and must be reconciled, not discarded:

- Factory Chat is UI/interaction boundary, not Runtime.
- Conversation is a first-class durable domain object.
- Runtime begins only after Mission exists and Operational Foundation admits work.
- MSM is the exclusive business owner of Mission lifecycle.
- Operational Foundation is the unified operational execution infrastructure.
- Engines are stateless Capability Providers and do not call each other directly.
- Execution routing is Capability-based.
- Provider definition and Provider Executor execution are distinct.
- Context Package is immutable and versioned.
- Persona belongs to Context, not hidden Engine state.
- Important executions/decisions/changes produce Evidence.
- Shared Knowledge must be versioned, searchable, provenance-aware and auditable.
- AI Kernel is the operational execution core after Operational Foundation admission; it is not Cognitive Processing. The Kernel executes; it does not decide.

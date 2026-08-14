---
status: APPROVED_TARGET
owner: Architecture
classification: CONSTITUTION_BOOK_ENTRY
version: 1.0.0
authority: Architecture Convergence 02 (R-15–R-27)
---

# Article VIII — Factory Protocol and Inter-Domain Boundary Architecture

## Authority and purpose

This Article is the canonical target for semantic communication between AI
Bridge domains. It supersedes any conflicting canonical description that treats
HTTP, MCP, WebSocket, a shared database, a provider adapter, or a UI route as a
cross-domain authority. It does not authorize a distributed rewrite, a schema,
or a physical network topology.

**FactoryIP** is the complete L0–L4 semantic communication stack. A **Factory
Packet** is its transported L4 unit. Each layer owns only its own semantics;
lower-layer transport availability never establishes domain authority.

## VII.1 L0 — Effective Operational Scope and Isolation

L0 resolves an immutable Effective Operational Scope for a boundary operation.
Scope identity remains distinct from the resolved resource, policy, profile and
authorization bindings. The resolution records versioned provenance and may
fail closed; it does not solicit, skip, repair, or create a business outcome.

## VII.2 L1 — Evidence

Evidence is immutable proof or support for an attributable fact, decision,
handoff, or processing result. It is neither logging nor a domain authority.
The relevant domain owns the semantic fact; Evidence Infrastructure owns
recording, integrity, retention and retrieval. Sufficiency is evaluated
separately from any domain consequence and integrity must be verifiable.

## VII.3 L2 — Provenance and causality graph

L2 records typed, version-aware, directionally authoritative relationships.
Relation Definitions declare family, specialization, owner, lifecycle and
activation-evidence requirements. Relation history is append-only; `RETRACTED`
is distinct from pending or absent. Evidence may be challenged and re-evaluated
without silently mutating a relation. Assurance is an immutable Evaluation
Result (`SUFFICIENT`, `DEGRADED`, `INSUFFICIENT`, or `INDETERMINATE`). A typed
edge is promoted to a first-class Relation Record only when lifecycle,
governance, identity or evidence requirements make that necessary.

## VII.4 L3 — Artifact Contract and knowledge boundary

An output is a canonical Artifact only when an applicable versioned **Artifact
Contract** qualifies it. The contract governs semantic purpose, stable Artifact
Identity, immutable Artifact Version, persistence, integrity, composition and
dependency, applicability, retention, scope, lifecycle and authority. Payload
is separate from identity/version metadata; Evidence is referenced, never
wholesale embedded. Identity/version qualification, contract lineage, payload
integrity and L2 provenance are mandatory before calling an object an Artifact.

Artifact is not automatically Knowledge. The only canonical route is:

```text
qualified Artifact → immutable Knowledge Candidate → Publication Resolution
→ CREATE | REVISE | CONFIRM | DUPLICATE | CONFLICT | REJECT
→ published Knowledge Object version (where resolved)
```

The Knowledge Domain Authority owns publication consequence. Conflict detection
never silently overwrites or retracts canonical Knowledge.

## VII.5 Resolution and Claim

Resolution Protocol is the cross-cutting boundary for unresolved accountable
authority work. A Claim is one governed Resolution Subject, not a universal
representation of every unresolved condition. Claim, decision, approval and
publication remain owned by their accountable domain.

## VII.6 L4 — Factory Packet transport

L4 transports a Factory Packet across a declared semantic boundary. A packet
binds L0 effective scope, L1 evidence references, L2 provenance references,
L3 artifact/version references where applicable, service intent, correlation,
integrity and delivery metadata. L4 is not a generic internal service-call
wrapper and does not make arbitrary CRUD reach-through legitimate.

## VII.7 Nodes, services, FFS and zoning

A **FactoryIP Node** is a logical, independently addressable service boundary.
Node identity, published service identity and endpoint/location are distinct.
Nodes expose semantic services, not direct access to internal domain state;
external adapters have no internal reach-through path.

The Conversation Node exposes only `conversation.interaction`,
`conversation.context`, and `conversation.projection`. Its concrete
`conversation.context` consumers remain an explicit topology question until
Context Assembly/domain topology is approved.

The **Factory Fabric Service (FFS)** is the thin control plane that resolves a
stable logical Node/service identity to a transport binding. Payload traffic
does not transit FFS. Dynamic discovery, leases, heartbeats, load balancing and
active-active clustering are not MVP prerequisites.

**Zoning** is the single FactoryIP transport-level permission mechanism: it
determines which source and destination services may communicate in an Effective
Scope. It is separate from domain authorization, is not an inbound/outbound
allow-list synonym, and is finalized only after Node/service topology is known.

## VII.8 Cognitive Processing and Kernel separation

Context Assembly, Understanding and Evaluation are reusable, stateless Cognitive
Processing. They consume an Effective Scope/Profile/Policy and emit immutable
Context Package, Understanding Result and Evaluation Result objects. They do
not own domain consequence. The AI Kernel is post-admission operational
execution infrastructure; it is not Cognitive Processing and this Article does
not infer a Kernel LAN, Node, service or endpoint.

## VII.9 Invariants

1. A protocol adapter SHALL NOT bypass a domain boundary through CRUD or shared-state reach-through.
2. L1 Evidence SHALL NOT become a decision authority.
3. L2 relation history and L3 Artifact Versions are immutable and append-only.
4. An Artifact SHALL NOT become published Knowledge without Publication Resolution.
5. FFS SHALL NOT proxy payload data.
6. Zoning SHALL NOT replace domain authorization.
7. A Node SHALL NOT be inferred from a class, process, Kernel component, or endpoint.
8. Cognitive Processing SHALL NOT be placed inside the AI Kernel.

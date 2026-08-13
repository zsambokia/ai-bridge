# Source-derived target architecture

This is the target reconstructed from the local conversation alone. It is not
yet a statement that the repository or Constitution implements it.

## Governing model

Architecture Convergence establishes approved semantics independently of
implementation. The existing Constitution is a current canonical baseline for
comparison; it is not entitled to erase an approved convergence delta. Before
MVP, incorrect architecture may be replaced rather than retained for backward
compatibility (R-01, R-02, R-29).

## Conversation and cognitive processing boundary

Conversation is the boundary from Product Owner interaction toward Mission. It
does not decide Mission semantics. Its semantic state, lifecycle state, and
decision-stability/proposal handling are separate concerns. CSM orchestrates
Conversation transitions but is not a universal master orchestrator.

Conversation Understanding is a reusable stateless consumer of a canonical
Context Package. It obtains resolved Cognitive Profile/policy through Effective
Scope, produces immutable Understanding Results, and does not directly mutate
Conversation State or determine domain consequences. Observations, historical
interpretations, and present applicability are distinct. Evaluation is a
generic stateless capability; profile resolution diagnoses controlled failure
instead of improvising user interaction or repair.

## Factory Protocol

The cross-cutting protocol is a five-layer model:

```text
L4  Factory Message / Packet: envelope, delivery/interaction, payload
L3  Artifact / Knowledge: immutable versioned artifacts and publication flow
L2  Provenance / Causality: relation semantics, lifecycle, authority
L1  Evidence: contract-defined proof of handoff/production
L0  Effective Scope: effective policy, context, operation and profile binding
```

The stack is accumulated at real domain/protocol boundaries. An Evidence record
does not substitute for a causal relation; a relation does not erase its
history. Artifact contracts decide lifecycle and durable state handling.

An Artifact is immutable and versioned. Knowledge is not a full-artifact copy:
semantically independent knowledge candidates proceed through a publication
resolution. Claims are owner-bearing resolution cases where ambiguity cannot be
handled deterministically by normal workflow.

## FactoryIP fabric

FactoryIP is the full L0–L4 boundary stack and transports Factory Packets
between source and destination at genuine domain/protocol boundaries. L4 has
more than one upper protocol: it is not synonymous with Resolution.

Factory Fabric Service (FFS) is logically authoritative but may be physically
distributed. In MVP it is deliberately thin: a static/name-routing control
plane, not a packet data-plane proxy. High availability is deferred.

Zoning is the canonical firewall-like source-to-destination communication
authorization. It is distinct from domain authorization; separate
inbound/outbound/forbidden communication contracts must not be reintroduced.

A Node exposes services across FactoryIP only after qualification. Factory Chat
is an independently addressable FactoryIP Node, but remains a UI boundary—not
Runtime and not Conversation owner. AI Kernel must not be equated with
Cognitive Processing or pulled into this LAN model until its own architecture
has been reviewed.

## Required convergence outcome

The source states that all L0–L4 packages, FactoryIP, FFS and the Node model
are foundational cross-cutting changes. Their semantic and constitutional
delta must be made canonical before advancing to the later MSM work. Any
implementation or Constitution change must trace back to the reconstruction
ledger and preserve the negative invariants.

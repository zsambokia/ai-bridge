# Architecture Convergence 02 — Constitution Amendment

Status: DRAFT / WORKING
Canonical effect: NONE until Product Owner closure approval and merge to `main`

## Purpose

This document is the evolving amendment view of Architecture Convergence 02. It translates accepted working decisions into candidate constitutional language. It must remain narrower than the Change Register: unresolved ideas do not become constitutional text.

## Candidate constitutional invariants

### 1. Cognitive and runtime boundary

The canonical high-level chain distinguishes cognitive/pre-Mission processing from operational execution:

```text
Product Owner
→ Factory Chat
→ Conversation
→ Conversation Understanding
→ Conversation State / Mission Resolution
→ Mission
→ Mission State Machine
→ Operational Foundation
→ immutable Execution Request
→ AI Kernel
→ Execution
→ Capability Resolution
→ Provider Binding
→ Provider Executor
→ external Provider / LLM / MCP / Tool
```

The AI Kernel is the operational execution core. It begins after Operational Foundation admission of an immutable Execution Request. Cognitive processing, Conversation Understanding, Conversation State evaluation and Mission Resolution are not AI Kernel responsibilities.

**Invariant:** The Kernel executes; it does not own business decision authority.

### 2. Context boundary

Business/cognitive Context is assembled above the Kernel. Context construction is not Kernel state. Runtime execution consumes an immutable, versioned Context Package prepared before the relevant execution boundary.

The exact Context Assembly ownership and final Context Package contract remain subject to later explicit convergence and are not invented by this amendment.

### 3. Factory Protocol stack

Factory cross-boundary semantics are layered and must be constitutionally defined layer by layer:

```text
L0 — Scope & Isolation
L1 — Evidence
L2 — Provenance & Causality
L3 — Artifact Layer
L4 — Factory Message Protocol
FactoryIP — semantic inter-domain communication model over the stack
```

A future final amendment must contain the approved semantics of each layer. Merely naming “L0–L4” is insufficient.

### 4. Artifact invariant

Artifacts are first-class, immutable and versioned protocol objects. Their model explicitly covers materialization/payload, integrity, composition/dependencies, applicability and retention/availability/scope.

Evidence does not bypass the Artifact model. Artifact persistence and AKB knowledge persistence are distinct: an Artifact does not automatically become a Knowledge Object merely because it exists or contains useful information.

### 5. Factory Message Protocol

L4 is the Factory Message Protocol. It is a general semantic messaging layer supporting multiple cross-boundary interactions. Resolution is one possible interaction, not the definition of the layer.

A Factory Message conceptually combines a common envelope, interaction/transport semantics and interaction-specific payload. Factory Messages are required where a genuine domain/protocol boundary is crossed; internal implementation calls are not automatically Factory Messages.

### 6. FactoryIP and Node boundary

FactoryIP is not a generic CRUD or database API. It is the semantic communication model used between Factory domains/Nodes.

A FactoryIP Node exposes stable semantic services to the Factory LAN and hides its internal implementation and canonical state mechanics.

**Invariant:** A Node's canonical domain state cannot be mutated by reaching through its FactoryIP boundary.

External technologies such as MCP, HTTP or WebSocket may provide access adapters. They do not acquire authority to bypass FactoryIP or directly mutate another Node's canonical state.

### 7. Conversation Node service boundary

The Conversation Domain is represented to the Factory LAN through semantic service families:

- `conversation.interaction`
- `conversation.context`
- `conversation.projection`

These services represent domain communication, not CRUD exposure.

The canonical service model does not expose generic `conversation.create/update/delete`, `message.create/update`, or external `state.set/transition` operations as FactoryIP authority.

Conversation retains authority over its canonical state and over how accepted interactions and projections affect that state.

### 8. Cognitive Processing

Conversation Understanding does not itself own business decision authority. Cognitive Processing is modeled as generalizable stateless processing over explicitly supplied Context. Context, Understanding and Evaluation are distinct concerns.

Result, Outcome and Projection are distinct concepts and must not be treated as synonyms.

Claim may be modeled as a first-class object where responsibility or decision-authority semantics require it. Claim is not defined as an L3 resolution mechanism.

## Explicitly not finalized by this draft

- exact L0 semantics;
- exact L1 semantics;
- exact L2 semantics;
- complete FFS semantics;
- Factory LAN Zoning;
- final ownership of Context Assembly;
- final consumer contract of `conversation.context`;
- final first-class schemas for Understanding/Evaluation/Claim/Result/Outcome/Projection.

These remain open until supported by approved decisions and evidence.

# Architecture Convergence 02 — Change Register

Status: WORKING / NON-CANONICAL UNTIL CLOSURE
Owner: Product Owner
Branch: `architecture/02-conversation-understanding-convergence`

## Purpose

This is the live convergence register for Architecture Convergence 02. It records accepted architectural deltas while design continues. Acceptance in this register means Product Owner acceptance within the 02 working change-set; it does not make the change canonical on `main` until closure review and merge.

## Working rules

- Architecture first: understanding → architecture → decision → implementation.
- `main` remains the canonical repository baseline until this change-set is closed and merged.
- Proposals and open questions are not silently promoted to accepted decisions.
- Cross-cutting foundation decisions discovered during 02 must be recorded explicitly rather than hidden inside Conversation-specific wording.
- Current implementation does not override target architecture.
- Zoning is deferred until the relevant Factory LAN Node and service topology is known.

## Accepted change areas

### Factory Protocol foundation

The 02 closure must carry the full layer-by-layer canonical model, not merely a reference to “L0–L4”. The working foundation stack contains:

- L0 — Scope & Isolation
- L1 — Evidence
- L2 — Provenance & Causality
- L3 — Artifact Layer
- L4 — Factory Message Protocol
- FactoryIP as the semantic inter-domain communication model built over the protocol stack

Detailed L0–L2 wording remains to be reconstructed from approved 02 decisions before closure; it must not be invented from memory.

### L3 — Artifact Layer

Accepted direction:

- Artifact is first-class, immutable and versioned.
- Artifact concerns include materialization/payload, integrity, composition/dependencies, applicability, retention/availability/scope and protocol boundary.
- Evidence is not a special exception to Artifact handling.
- Complete Artifacts do not automatically become AKB knowledge; knowledge objects/blocks are derived under Knowledge lifecycle rules.

### L4 — Factory Message Protocol

Accepted direction:

- L4 is the Factory Message Protocol.
- It supports multiple protocols/interactions; Resolution is one interaction, not the definition of L4.
- A Factory Message consists conceptually of a common envelope, transport/interaction semantics and interaction-specific payload.
- Factory Messages are required at genuine domain/protocol boundaries, not for arbitrary internal method calls.

### FactoryIP

Accepted direction:

- FactoryIP is not a CRUD/API layer.
- FactoryIP is the semantic communication protocol/model between Factory domains/Nodes.
- External access technologies such as HTTP, WebSocket or MCP may act as adapters, but they must not bypass the canonical FactoryIP boundary of a Node.
- A FactoryIP Node exposes stable semantic services while hiding its internal implementation and canonical state mechanics.
- Direct reach-through into another Node's internal state is prohibited by architecture.
- FFS belongs to the FactoryIP foundation and requires full canonical wording during closure.
- Zoning is deliberately deferred until Node + service topology is sufficiently complete.

### Conversation Domain / Node

Accepted service model:

- `conversation.interaction` — accepts Conversation-relevant interaction semantically, rather than exposing message CRUD.
- `conversation.context` — provides purpose-bound authoritative Conversation context.
- `conversation.projection` — projects relevant facts originating in other domains into the Conversation under Conversation authority.

Negative boundary:

- no canonical `conversation.create/update/delete` service family;
- no `message.create/update` service family as FactoryIP semantics;
- no external `state.set/transition` authority;
- external adapters must not bypass the Conversation Node to mutate canonical Conversation state.

The concrete consumer of `conversation.context` remains open until Context Assembly is designed.

### Cognitive / pre-Mission architecture

Accepted direction:

- Conversation Understanding is not decision authority.
- Cognitive Processing is a generalizable stateless processing model.
- Context, Understanding and Evaluation are distinct concerns.
- Result, Outcome and Projection are distinct concepts and must not be collapsed.
- Claim may be a first-class object carrying responsibility/decision-authority semantics, but Claim is not an L3 resolution mechanism.

### AI Kernel boundary correction

Accepted correction:

- AI Kernel is the operational execution core after Operational Foundation admission.
- Conversation Understanding / Cognitive processing / CSE / Mission Resolution are pre-Mission or higher-level cognitive concerns and are not the AI Kernel.
- The Kernel executes; it does not decide.
- Context construction is outside the Kernel; the Kernel consumes an already prepared immutable Context Package.

## Required closure work

Before 02 can be proposed for merge:

1. reconstruct and write the approved L0, L1 and L2 models from evidence;
2. complete canonical L3 and L4 definitions;
3. complete FactoryIP, FactoryIP Node and FFS definitions;
4. converge Conversation and Cognitive Processing wording with the existing Constitution;
5. identify contradictions with existing canonical documents;
6. prepare explicit Constitution amendments;
7. classify unresolved items as OPEN rather than guessing;
8. perform final Product Owner closure review.

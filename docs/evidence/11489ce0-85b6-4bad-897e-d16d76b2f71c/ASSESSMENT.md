# Repository assessment — Factory Chat and Conversation Layer

Scope: `bridge:ai-bridge:sprint:11489ce0-85b6-4bad-897e-d16d76b2f71c`, proposal
version `1`, hash `0cf818d7df806f5e1f98bc78b040574de46b8778ddd1d5771ca2909e5ccaecb1`.
Baseline: `08534749ad8c1bc51e07c53001fd196f43957688` on `main`.

## Finding

The implementation was not converged with the approved issue #22 architecture.
`factory_chat_message` called `receive_conversation_event`, which persisted an
`OrkiExecution` and could dispatch Runtime work directly from a browser POST.
`FactoryMission` was one-to-one with `FactoryChatSession`, so a UI session was
also the effective human mission/intake state. `FactoryChatMessage` was the
only durable transcript record. The existing `KnowledgeContextPackage` was an
immutable AKB retrieval record, but was not a general Context Package with a
resolved Context Profile.

## Architecture challenge

The approved issue target is internally coherent and is the Product Owner's
latest decision. The previous Article IV text requiring a global retrieval
order and numeric maturity bands conflicts with CH-05, CH-06, and CH-10; it is
a documentation/implementation migration gap, not a materially superior
alternative. No business decision is required.

## Approved migration decision

Introduce an independent durable Conversation aggregate, stateless transition
and context-assembly services, a Mission Resolution record, and a general
Context Package contract. Factory Chat becomes an adapter that records a
Conversation action and returns its projection; it neither starts Runtime nor
creates a Mission. Legacy Factory/Runtime records may remain as historical
data, but are not used by the Factory Chat route.

# Architecture Convergence 02 implementation-obligation matrix

Status date: 2026-08-14.  Scope authority: Product Owner Factory Development
Mode instruction for the approved source reconstruction Epic.  This is a new
implementation record; it does not alter the historical closure material.

## Classification key

Each approved reconstructed decision has exactly one classification:

| Code | Meaning |
|---|---|
| A | Canonical architecture only; no new executable obligation in this slice. |
| B | Implemented and verified in the Factory Protocol MVP. |
| C | An executable obligation, deliberately bounded for a later approved implementation section. |
| D | Explicitly deferred by the approved decision itself. |
| E | Open semantic question; no implementation is inferred. |

There are no E rows: the source reconstruction contains no unresolved approved
semantic decision.  `CHAT-####` locators are the complete binding chat-decision
set: the source ledger has already excluded unapproved assistant proposals.

| Decision / binding chat locators | Class | Runtime or canonical disposition | Verification |
|---|---:|---|---|
| R-01 / CHAT-0003–0004 | A | Replacement authority governs convergence, not a service behavior. | Source ledger and Constitution. |
| R-02 / CHAT-0011–0012,0063–0074 | A | Separates target semantics from this implementation convergence. | Source Epic boundary. |
| R-03 / CHAT-0031–0032 | B | Conversation remains a bridge; `dispatch_conversation_understanding` has no Mission mutation. | `test_end_to_end_packet_flow_filters_knowledge_before_retrieval`. |
| R-04 / CHAT-0033–0038,0061–0062 | B | Result is separate from conversation lifecycle/state. | Immutable `CognitiveProcessingResult`; CSM-only evaluation. |
| R-05 / CHAT-0045–0058 | B | Context Profile is resolved and Context Package is assembled separately. | Profile resolution and pre-retrieval eligibility test. |
| R-06 / CHAT-0083–0085 | B | Understanding is a stateless protocol operation, not state authority. | No ConversationState write in protocol dispatch. |
| R-07 / CHAT-0085–0086,0131–0134,0147–0150 | B | Immutable structured processing result with no direct state write. | Immutable model and E2E test. |
| R-08 / CHAT-0093–0096,0107–0108 | B | Processing request/result are packets/results, not auto-artifacts. | Packet flow test; separate explicit artifact API. |
| R-09 / CHAT-0113–0118,0173–0178 | B | L0 snapshot binds tenant, workspace, resources, policy, and profile. | `EffectiveOperationalScope` immutability test. |
| R-10 / CHAT-0123–0128 | B | Missing profile returns `PROFILE_UNRESOLVED`; it does not repair or solicit. | `test_unresolved_profile_has_explicit_return_without_cognitive_result`. |
| R-11 / CHAT-0131–0138 | B | Evaluation is stateless structured output; historical assurance extensions are C. | E2E result evaluation. |
| R-12 / CHAT-0139–0146 | B | CSM is named as sole state authority; protocol emits outcome only. | E2E assertion `CSM_ONLY`. |
| R-13 / CHAT-0155–0160 | B | Artifact identity and immutable versions have contract/payload/integrity fields. | `FactoryArtifactVersion` constraints and test. |
| R-14 / CHAT-0161–0164,0179–0192 | B | Handoff evidence is immutable and scope-bound. | `FactoryEvidence` and E2E packets. |
| R-15 / CHAT-0165–0178,0241–0244,0301–0304,0381–0382 | B | L0–L4 are independently persisted/referenced. | Models, migration 0069, E2E flow. |
| R-16 / CHAT-0180–0192 | B | Evidence records source, subject, payload hash, scope, and time. | `record_evidence`. |
| R-17 / CHAT-0194–0228 | B | Directional provenance relation and lifecycle event are separate immutable records. | Provenance test. |
| R-18 / CHAT-0209–0216 | B | Challenge/retract are append-only status events, never deletion. | Challenge append test. |
| R-19 / CHAT-0229–0240 | C | Canonical assurance result families and re-evaluation workflow require their own approved section. | Explicitly not inferred from this bounded vertical slice. |
| R-20 / CHAT-0245–0262,0293–0295,0412–0417 | B | Immutable versioned artifact contract, payload hash, and integrity hash are enforced. | Migration/model constraints. |
| R-21 / CHAT-0263–0272 | B | Candidate and resolution are separate; publication needs explicit approval and a supplied KnowledgeEntry. | `EXPLICIT_APPROVAL` test. |
| R-22 / CHAT-0275–0282 | C | Accountable Claim domain is a later semantic model, not silently invented here. | Bounded out of slice. |
| R-23 / CHAT-0285–0304 | B | L4 packet includes envelope, delivery endpoints, correlation and payload contract. | `FactoryPacket` and E2E flow. |
| R-24 / CHAT-0301–0308,0327–0330 | B | Sender → packet/L0–L4 → route → zone → destination → response is executable. | E2E packet test. |
| R-25 / CHAT-0311–0328 | B | FFS resolves node/service/routing only; it does not proxy payload data. | `resolve_route` implementation and test. |
| R-26 / CHAT-0322–0328,0355–0358 | B | Default deny, reciprocal allow, and deny precedence are a separate zoning decision. | `test_zoning_denies_even_when_an_allow_exists`. |
| R-27 / CHAT-0339–0350 | B | Factory Chat and Conversation have explicit nodes; Conversation Understanding is published service. | `_conversation_surface`. |
| R-28 / CHAT-0351–0354,0365–0370 | B | No Kernel node/service/LAN inference; cognitive result is protocol-local and stateless. | Protocol inspection and negative invariant test. |
| R-29 / CHAT-0369–0372 | A | The source/Constitution comparison is governance, not a missing runtime behavior. | Source reconstruction evidence. |
| R-30 / CHAT-0377–0382 | B | Foundation is delivered as one L0–L4 vertical slice before later MSM work. | Migration, runtime module, integration suite. |
| R-31 / CHAT-0396–0423 | A | Preserve detailed reconstruction and historical evidence without ID reuse. | This matrix and immutable prior evidence. |

## Scope boundary

Rows C are intentionally not claimed as implemented.  They require a new
approved implementation section.  No A, C, or D item is represented as a
working runtime feature; no E item is inferred.

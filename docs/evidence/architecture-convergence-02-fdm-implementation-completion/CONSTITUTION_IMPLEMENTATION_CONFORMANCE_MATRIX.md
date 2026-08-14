# Constitution-to-implementation conformance matrix

| Constitutional / architecture obligation | Concrete implementation | Evidence |
|---|---|---|
| L0 scope precedes semantic retrieval | `resolve_effective_scope` freezes tenant/workspace/resource/policy/profile bindings; `assemble_context` receives eligible IDs before lookup. | `projects/factory_protocol.py`; E2E context-ID assertion. |
| L1 evidence is first class | Immutable `FactoryEvidence` has scope, source, subject, payload hash and timestamp. | Migration 0069; `record_evidence`. |
| L2 preserves provenance history | Immutable relation plus append-only status events support active/challenged/retracted states. | `append_provenance_relation`, `append_provenance_status`; provenance test. |
| L3 separates artifact from knowledge | Versioned artifact, candidate, and explicit resolution models prevent automatic knowledge publication. | Explicit approval failure test. |
| L4 is a delivery protocol | Immutable request/response packets retain source, destination, correlation, payload and linkage. | E2E packet round-trip test. |
| FFS is control plane only | `resolve_route` returns a route decision and never transports content. | Factory protocol implementation. |
| Zoning is not domain authorization | `ZoneRule` enforces deny-by-default and deny precedence independently of user permissions. | Zone denial test. |
| Factory Chat is UI node, Conversation has published service | `_conversation_surface` makes both explicit nodes and publishes only `conversation.understanding`. | Runtime surface creation. |
| Cognitive Processing is stateless and outside Kernel | Dispatch constructs an immutable result and calls no Kernel or cognitive-state service. | Protocol module; existing architecture negative test. |
| CSM owns state | Evaluation explicitly declares `CSM_ONLY`; dispatch does not mutate ConversationState. | E2E test and source inspection. |
| Mission and Knowledge are bounded | Evaluation declares no Mission mutation; Knowledge publication is a separate explicit resolution. | E2E result and candidate-resolution test. |

All entries are conformance claims for the bounded MVP, not claims that later
Claim/assurance workflows have been implemented.

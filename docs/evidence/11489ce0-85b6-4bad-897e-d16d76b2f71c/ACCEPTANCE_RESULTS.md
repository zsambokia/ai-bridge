# Acceptance results

## Implemented acceptance boundary

- Factory Chat is a presentation adapter over durable Conversations. Posting a
  message records it with an idempotent correlation key and does not create an
  `OrkiExecution` or dispatch a provider.
- Conversation state is durable and separates semantic state, lifecycle state,
  readiness, version, evidence, and provenance.
- Decisions are durable. An accepted decision cannot be replaced except by an
  explicit superseding decision.
- Context Profiles are version-addressed inputs to auditable Context Packages;
  constrained retrieval is policy-directed rather than a fixed global flow.
- Mission Resolution records an explicit outcome and rationale only. It does
  not create or start a Mission/runtime.
- Migration `0068_conversation_domain_convergence` creates the new domain and
  converts existing project-scoped Factory Chat sessions/messages without
  treating browser-session closure as Conversation closure.

## Evidence

The focused durable-boundary scenarios pass in
`projects/tests/test_conversation.py`. The final release gate passed with 361
tests passing. Former direct ingress scenarios are explicitly skipped because
they assert behavior prohibited by this Sprint's architecture boundary.

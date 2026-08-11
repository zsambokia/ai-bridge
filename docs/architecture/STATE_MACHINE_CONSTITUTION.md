---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: Constitution Book (planned adoption)
version: 1.0.0
---

# State Machine Constitution

> **Terminology status (2026-08-10):** Transitional. MSM remains the business
> state-machine owner. Article III defines the target AI Kernel technical
> state machine and Kernel Events. Article IV defines the Conversation State
> Engine (CSE) as the Conversation Domain owner. This document does not
> authorize model or event-stream renames.

Every durable lifecycle SHALL have one named state-machine owner and an
explicit transition contract.

1. MSM exclusively owns Mission lifecycle state. CSE exclusively owns
   Conversation Domain progression and may only request Mission Resolution; it
   cannot create or transition Mission state. A Domain Engine exclusively owns
   its own internal lifecycle state. The Operational Foundation owns work
   delivery mechanics; it does not own Mission, Conversation, or Engine
   business state.
2. A state machine MUST NOT write another state machine's state, including
   through a convenience service or shared persistence shortcut.
3. Cross-domain progression SHALL use durable immutable requests, authorized
   Work Items, results, events, and evidence. The MSM is the only coordinator
   that may interpret an Execution Request into a Work Item.
4. Transitions SHALL be attributable, ordered or versioned as appropriate,
   idempotent, recoverable, and evidence-linked. Invalid or duplicate
   transitions SHALL fail closed or reconcile through the owner.
5. A projection may read a permitted view but MUST NOT become a state-machine
   writer. Provider transport may report a receipt but MUST NOT transition
   Mission or Engine business state.

This constitution does not certify legacy OESM or other existing state
implementations as compliant. Their status is governed by the evolution
register and evidence.

The canonical CSE progression, maturity semantics, Mission Resolution boundary,
and Conversation-specific invariants are defined by [Article IV - Conversation
to Mission Architecture](CONVERSATION_TO_MISSION_ARCHITECTURE_CONSTITUTION.md).

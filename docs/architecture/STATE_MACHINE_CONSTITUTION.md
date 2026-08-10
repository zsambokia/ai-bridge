---
status: CANONICAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# State Machine Constitution

Every durable lifecycle SHALL have one named state-machine owner and an
explicit transition contract.

1. MSM exclusively owns Mission lifecycle state. A Domain Engine exclusively
   owns its own internal lifecycle state. The Operational Foundation owns work
   delivery mechanics; it does not own Mission or Engine business state.
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

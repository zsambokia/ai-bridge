---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Operational Engine Contract

## Universal lifecycle

```text
poll -> claim durable work -> load versioned context -> execute bounded step
-> write evidence -> publish state/event -> acknowledge -> idle
```

No engine retains authority only in memory. A crash after any stage is reconciled from the durable work item, idempotency key, state transition and evidence receipt.

## Required interface

```text
EngineWorkItem
  id, engine_kind, mission_id, correlation_id, idempotency_key
  requested_transition, input_refs, policy_ref, attempt, available_at

EngineResult
  outcome: COMPLETED | WAITING | RETRY | FAILED | REJECTED
  state_patch_ref, evidence_refs, events, retry_at, error_class
```

An engine must validate that it owns `engine_kind`, claim the item atomically, load only versioned inputs, and publish a result atomically with its evidence references. Result publication is rejected if the expected source-state version no longer matches.

## Errors and recovery

* `RETRYABLE`: bounded exponential retry with a durable next-at timestamp.
* `WAITING`: external/user condition with a named resumption event; no active lease.
* `REJECTED`: invalid policy, stale input, or wrong owner; evidence required.
* `FAILED`: retry budget exhausted or non-recoverable error; Runtime decides mission-level escalation.
* duplicate delivery: result must be idempotent by work-item and transition key.

## Ownership

The engine owns its internal state and evidence. The queue owns delivery. The Runtime owns mission/approval authority. The Provider Gateway owns provider communication. The evidence store owns immutable receipts. This contract is intentionally transport-neutral: polling is the initial mechanism, with event delivery allowed later.

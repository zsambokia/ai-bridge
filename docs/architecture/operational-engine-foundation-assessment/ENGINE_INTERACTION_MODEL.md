# Engine interaction model

## Interaction rules

Operational Engines communicate only through durable state, events, evidence references, repository/context receipts and work queue records. They must not call each other as in-process services.

```text
Planning result -> Runtime verifies gate -> workflow work item
Workflow task -> ExecutionRun request -> Provider Gateway
Provider receipt -> ExecutionRun result -> Workflow event
Workflow completion -> Reflection work item
Reflection proposal -> governed Learning work item
```

## Polling versus event bus

Use durable polling first: it is simple to operate, naturally restart-safe, observable, and compatible with the existing runtime maturity. Use an outbox-style event record for every publication. A future event bus may deliver those same events, but it must not become the source of truth or erase the poll/reconciliation path.

The recommended model is therefore **durable state + outbox events + polling workers**, not a synchronous engine mesh and not an event bus as the sole coordinator.

## Conversation boundary

Conversation is a distinct layer, not an Operational Engine. It renders the work journal, accepts user input, persists the transcript, and calls a Runtime command. It does not own planning/workflow state. The primary workspace is the chat; side panels are read-only live projections of canonical state and evidence.

# Authorization validation

The conflicting token is discovery-only. The repair does not assign the
conflicting `ExecutionRun` to the blocked `ConversationOrchestration`, does not
change either contract, and does not add a scope-wide cancellation endpoint.

`execution.cancel` continues to resolve the active run and validates the
durable approval reference against that run's own contract before cancellation.
The regression test asserts that the blocked orchestration has no run while
the returned token belongs to the independently active run.

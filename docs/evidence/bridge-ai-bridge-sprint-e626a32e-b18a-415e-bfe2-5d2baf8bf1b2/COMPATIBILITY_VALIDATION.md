# Compatibility Validation

The existing `conversation.confirm` and `scope.confirm_and_execute` operations
remain unchanged as the ordinary same-session paths. Recovery is additive and
uses the existing public registry, canonical scope, approval, orchestration,
idempotency, audit, contract, and execution services.

`pytest` passed all 92 tests, including the existing MCP, contract, execution,
scope, provider, remote transport, and service coverage. `ruff check .` and
`mypy .` also passed. No migration or persisted schema change is required.

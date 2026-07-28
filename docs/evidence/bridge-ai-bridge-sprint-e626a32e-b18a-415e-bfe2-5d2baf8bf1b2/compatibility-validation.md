# Compatibility validation

`conversation.confirm` and `scope.confirm_and_execute` remain unchanged public
paths. The recovery capability is additive: `scope.resume` and
`scope.resume_confirm_and_execute` are new names on tool surface
`2026-07-28.3`.

The full suite passed with 92 tests. This includes the pre-existing
conversational confirmation and orchestration tests, plus recovery tests for a
new caller session, durable approval reuse, idempotent replay, and stale-hash
rejection.

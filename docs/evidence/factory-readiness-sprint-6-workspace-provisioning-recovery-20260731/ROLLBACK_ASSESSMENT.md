# Rollback assessment

The change is additive and uses existing `ExecutionRun`, `ExecutionJob`, and
`ExecutionRecoveryAttempt` persistence; it requires no migration. Reverting
the code commit restores previous reconciliation behavior but reintroduces the
quiet stale-STARTING gap. Existing recovery attempts and events remain valid
historical evidence and are not deleted by a rollback.

# Migration plan

Migration `projects.0026_execution_recovery` extends the existing durable queue
without rewriting existing rows: it adds checkpoint, retry/backoff and bounded
reconciliation-evidence fields to `ExecutionJob`, adds recovery job statuses,
and creates the append-only `ExecutionRecoveryAttempt` table. Rollback is the
standard Django reverse migration before dependent data is relied upon; no
existing scope, contract, run, or event is altered by the migration itself.

# Local execution break-glass terminalization

`force_terminalize_execution` is a deliberately narrow Django management command for a Product Owner-authorized local incident. It is not an MCP tool and never starts, cancels, requeues, or recovers a provider process.

## Safe operating boundary

Before a non-dry-run command, identify any `run_execution_worker` or `reconcile_execution_jobs` process that could mutate the target record. Do not race it. Under separately documented Product Owner operational authority, its scheduler source may be safely stopped, the operation performed, and the single prior scheduler configuration restored for a smoke run. Do not stop unrelated worker, provider, database, or web services.

Back up the runtime SQLite database before the first mutation, preserve the workspace, execute a dry run, then execute the same command without `--dry-run`.

The command only admits either:

- a `REQUESTED` execution with no provider identifier and a queued or leased job;
- a `RUNNING` execution whose provider PID is no longer alive and whose append-only event stream contains `PROVIDER_COMPLETED` with `provider_event_type=process.exit`; or
- the narrow `STARTING` / `RECOVERING` state whose job is `RECOVERING`, where the same exit evidence and a single consistent provider identifier prove that reconciliation is attempting an unsafe restart.

It refuses any other lifecycle, a live provider process, conflicting provider identifiers, missing exit evidence, or a missing `--preserve-workspace` flag. The run, queue job, and contract are locked and terminalized in one transaction: the run becomes `CANCELLED`, the job becomes non-claimable `FAILED`, its lease and recovery schedule are cleared, and the contract becomes `CANCELLED`. If a workspace exists, its files and paths are retained, its status becomes `RETAINED`, and only its stale provider PID is cleared. Repeating an already-terminal run is an idempotent no-op.

## Command

```text
python manage.py force_terminalize_execution <execution-token> \
  --reason "<Product Owner emergency reason>" \
  --operator "<operator identity>" \
  --preserve-workspace --dry-run
```

Remove `--dry-run` only after the preconditions and database backup have been recorded. Output is machine-readable JSON. The command writes the append-only `EXECUTION_BREAK_GLASS_TERMINALIZED` event with the operator, reason, idempotency key, before/after states, PID observation, heartbeat, provider exit evidence, and workspace-preservation declaration.

## Product capability follow-up

This local command is incident tooling, not the intended operating model. A future governed force-cancel capability must be exposed through a dedicated MCP control-plane operation with authenticated Product Owner identity, explicit approval reference, execution-state preconditions, durable idempotency, and the same complete audit event. It must remain separate from ordinary execution approval and provider recovery flows.

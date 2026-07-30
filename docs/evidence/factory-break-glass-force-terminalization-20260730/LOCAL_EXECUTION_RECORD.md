# Factory Development Mode execution record

## Authority and scope

- Authority: explicit Product Owner Factory Development Mode authorization in the current conversation, including local implementation, backup, safe reconciler control, dry run, terminalization, restoration, and smoke test.
- Scope: terminalize only `bd028cb4-8134-4201-b1b4-9167161fd5c9` and `11210830-e201-4f90-a40f-dea988d290a4` without provider recovery.
- Branch: `main`.
- Baseline: `dc261c1485b82ee4882fae3b1b7f300fe36622d6`.

## Operational sequence completed

1. Found the scheduled task `AI-Bridge-Execution-Recovery-Reconciler` as the source of competing `reconcile_execution_jobs --once` processes (PIDs `26124` and `20360`). No execution worker or target provider process was running.
2. Ended the task's active instance and temporarily disabled that task only; after a full interval, no reconciler process was active. No database, web, provider, or unrelated worker service was stopped.
3. Created `runtime-db-backups/ai-bridge-before-force-terminalization-20260730-202634.sqlite3` before mutation. SQLite integrity check: `ok`; SHA-256: `6990CD4D3D2ABF5A1E9E11C8D34404AD42CC06B64BC989D2EAFCA0C5241F40DE`.
4. Dry-run passed for both tokens. It projected `CANCELLED` run and contract, `FAILED` job, cleared lease/recovery fields, and for the second token a retained workspace with cleared PID.
5. Terminalized the first token and verified every terminal invariant before touching the second. Then terminalized the second token. Each created one append-only `EXECUTION_BREAK_GLASS_TERMINALIZED` audit event.
6. Repeated each command: both returned idempotent `ALREADY_TERMINAL` and created no duplicate audit event.
7. Re-enabled the same scheduled task, triggered one smoke execution, and observed `LastTaskResult=0`, task state `Ready`, and no target restart.

## Final runtime state

| execution | run | job | contract | scope | workspace | audit count |
| --- | --- | --- | --- | --- | --- | --- |
| `bd028cb4-8134-4201-b1b4-9167161fd5c9` | `CANCELLED` | `FAILED` | `CANCELLED` | `APPROVED` | none | 1 |
| `11210830-e201-4f90-a40f-dea988d290a4` | `CANCELLED` | `FAILED` | `CANCELLED` | `APPROVED` | `RETAINED`, PID cleared | 1 |

Both jobs have blank lease owner, null lease expiry, and null next recovery. The second run retains its prior `PROVIDER_COMPLETED/process.exit` evidence; PID `2620` was absent before and after the operation. Neither scope is active.

## Local changes

- `projects/force_terminalization.py`: supports the bounded recovery-restart case only with finished-provider evidence, locks and cancels the contract, retains the workspace, clears stale provider PID, and reports projected dry-run states.
- `projects/management/commands/force_terminalize_execution.py`: local machine-readable command.
- `projects/tests/test_force_terminalization.py`: focused acceptance coverage.
- `docs/operations/BREAK_GLASS_EXECUTION_TERMINALIZATION.md`: runbook.

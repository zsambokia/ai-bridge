# Closure report — local break-glass terminalization hotfix

## Status

**BLOCKED — BUSINESS DECISION REQUIRED**

The authorized runtime recovery, implementation, evidence capture, and scoped
quality checks are complete. The only remaining Release Gate failure is the
repository-wide formatter, which would modify 11 files outside this hotfix,
including pre-existing user work. Preserving unrelated work prohibits making
that scope expansion without an explicit Product Owner decision.

## Delivered and verified

- Added a deliberately narrow local `force_terminalize_execution` command.
  It admits only a safe request, a proven-finished stale provider, or the
  bounded `STARTING`/`RECOVERING` restart case with the same proof. It does not
  invoke provider cancellation, restart, requeue, or recovery.
- The scheduled recovery reconciler was stopped at its scheduler source,
  temporarily disabled, and observed inactive before mutation. The same task
  was restored, triggered once, and returned `LastTaskResult=0`.
- Fresh pre-mutation SQLite backup:
  `runtime-db-backups/ai-bridge-before-force-terminalization-20260730-202634.sqlite3`;
  integrity `ok`; SHA-256
  `6990CD4D3D2ABF5A1E9E11C8D34404AD42CC06B64BC989D2EAFCA0C5241F40DE`.
- Both requested tokens passed dry-run, were terminalized one at a time, and
  passed a repeated idempotency invocation without a duplicate audit event.

| execution | run | job | contract | scope | workspace | audit count |
| --- | --- | --- | --- | --- | --- | --- |
| `bd028cb4-8134-4201-b1b4-9167161fd5c9` | `CANCELLED` | `FAILED` | `CANCELLED` | `APPROVED` | none | 1 |
| `11210830-e201-4f90-a40f-dea988d290a4` | `CANCELLED` | `FAILED` | `CANCELLED` | `APPROVED` | `RETAINED`, PID cleared | 1 |

Neither scope is active. Both jobs have no lease owner, lease expiry, or next
recovery timestamp. The second target retains its existing
`PROVIDER_COMPLETED/process.exit` event; the recorded provider PID `2620` was
not running before or after the operation.

## Validation evidence

- Scoped formatter, Ruff lint, focused tests, and mypy: PASS.
- Focused command acceptance tests: `7 passed`.
- Full repository tests: `185 passed`.
- `manage.py check`, migration-drift check, and scope validation: PASS.
- Canonical release gate: all stages pass through lint; `ruff format --check .`
  reports exactly these out-of-scope files: `projects/admin.py`,
  `projects/contracts.py`, `projects/execution.py`,
  `projects/execution_recovery.py`,
  `projects/management/commands/validate_scopes.py`, `projects/providers.py`,
  `projects/scopes.py`, `projects/tests/test_execution.py`,
  `projects/tests/test_execution_recovery.py`, `projects/tests/test_workspace.py`,
  and `projects/workspace.py`.

## Required decision

Authorize formatting the listed unrelated files, or explicitly accept the
current repository-wide formatter exception. No commit or push was requested
or performed.

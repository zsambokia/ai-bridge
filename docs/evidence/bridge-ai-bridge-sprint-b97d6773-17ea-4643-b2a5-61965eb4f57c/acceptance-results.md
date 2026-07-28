# Acceptance results

## Conflicting execution discovery

The stage `scope.orchestration_status` response for the pre-existing blocked
Bridge Demo scope returned the independently active execution token
`d06e3195-3637-48fd-a930-785f5d4fd734` and lifecycle `RUNNING`. The blocked
orchestration remained unbound to that run.

## Cancellation

`execution.cancel` accepted the token together with the active run's own
durable approval reference and returned `CANCELLED`. Follow-up calls to
`execution.get_run_status`, `execution.get_activity_summary`, and
`execution.list_events` all succeeded. The status and activity summary report
`CANCELLED`; the events include `EXECUTION_CANCELLED`.

## Release gates

All final local gates passed on 2026-07-28:

- `ruff check .`
- `mypy .` — 89 source files, no issues
- `python manage.py validate_scopes`
- `pytest -q` — 88 passed

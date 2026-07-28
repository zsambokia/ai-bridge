# Governed Execution Cancellation — Issue #7 evidence

## Scope and baseline

This evidence covers GitHub Issue #7, **Sprint — Governed Execution
Cancellation via MCP**, on branch `agent/governed-execution-cancellation`,
based on the Factory Development Mode lifecycle foundation. It uses the
repository-root bootstrap override only for this `ai-bridge` self-development
repair. Customer-project contract-first governance remains unchanged.

## Pre-change audit and gap decision

| Capability | Pre-change state | Decision |
| --- | --- | --- |
| Canonical run lifecycle, provider-finished reconciliation, watchdog | Complete | Reuse, do not replace |
| Shared evidence-derived Product Owner activity projection | Complete | Extend with cancellation facts |
| MCP cancellation | Partial: immediate legacy mutation, no confirmation or durable cancellation record | Replace boundary with prepare/confirm/cancel flow over canonical service |
| Django cancellation | Missing | Add confirmation UI over the same service |
| Graceful provider cancellation | Partial: raw Windows process-tree kill | Replace with provider termination request and reconciliation |
| Durable idempotent cancellation/recovery evidence | Missing | Add row-locked record, events, reconciliation, and regressions |

## Acceptance evidence

- `execution.prepare_cancel` returns an evidence-derived run summary and does
  not mutate lifecycle; `execution.confirm_cancel` persists the derived caller
  binding and confirmation; `execution.cancel` requires the stored
  confirmation.
- `ExecutionCancellation` records requester, reason, confirmation, provider
  acknowledgement, completion, and status. `ExecutionRun` transitions through
  `CANCELLING` before `CANCELLED`.
- Row-locked canonical services make duplicate/restart/watchdog reconciliation
  idempotent; tests prove one cancellation/evidence event sequence.
- MCP and Django use the same lifecycle service. The existing activity
  projection maps persisted cancellation events and continues to keep raw
  provider events separate.
- The normal provider adapter requests termination without a raw `taskkill`
  process-tree kill. There is no routine force-cancel action.

## Validation results

```powershell
pytest -q projects/tests/test_execution.py projects/tests/test_governed_mcp.py projects/tests/test_providers.py
python manage.py makemigrations --check --dry-run
python manage.py check
ruff check .
ruff format --check .
mypy .
pytest -q
```

All commands passed from the implementation worktree:

- migration drift check: `No changes detected`;
- Django system check: no issues;
- Ruff lint and format: passed;
- mypy: `Success: no issues found in 92 source files`;
- full pytest: `88 passed`.

This evidence is versioned in the same commit history as the implementation and
does not claim deploy or merge completion.

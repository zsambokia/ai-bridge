# Sprint 016 acceptance results

**Sprint:** Canonical Execution Lifecycle Integrity and Autonomous Recovery
**Execution profile:** Product Owner Factory Development Mode
**Baseline:** `ff3cf82dee9f580da83c215fb25f7636b2b5fa22` on `main`
**Result:** PASS pending delivery-commit binding

## Acceptance mapping

| Acceptance scenario | Evidence and result |
| --- | --- |
| Worker dies after leasing work | Stale lease, replacement-worker reclaim, and reattach paths are covered by `projects/tests/test_execution_recovery.py`; the one-to-one job plus transactional claim prevents a second provider start. PASS. |
| Provider PID is absent | `test_missing_workspace_provider_pid_enters_bounded_recovery` fault-injects a dead PID, clears the workspace to `READY`, records an event, and enters bounded checkpoint recovery. Existing no-checkpoint/retry-limit tests prove review-required terminalization. PASS. |
| Run and job disagree | Terminal-run/active-job convergence and active-run/terminal-job fail-closed behaviour are both tested twice for idempotence and create an event plus recovery evidence. PASS. |
| Duplicate dispatch/retry arrives | `claim_next_job` admits only active runs and `execute_claimed_job` locks and rechecks before provider work. The preclaimed terminal-run race test proves the original terminal lifecycle is preserved. PASS. |
| Recovery limit is crossed | Existing recovery-limit and review-lifecycle tests remain green; the controller persists root-cause evidence and reaches the canonical blocker/terminal state. PASS. |
| Admin and MCP inspect one record | Admin recovery summary and `execution.get_run_status` expose the same safe queue, lease, recovery, workspace, and evidence projection; MCP test coverage is green. PASS. |
| Real governed E2E recovery completes | A consumed-contract run is recovered through the actual `reconcile_execution_jobs --once` management-command entry point, then claimed by a replacement worker. Full repository gates and a live no-op controller pass are recorded below. PASS. |

## Machine and operational evidence

| Check | Result |
| --- | --- |
| Focused lifecycle suite | `70 passed` |
| Repository test suite: `pytest` | `195 passed in 10.26s` |
| `ruff check .` | PASS |
| `mypy .` | PASS — 139 source files |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `python manage.py reconcile_execution_jobs --once` | PASS — `Reconciled 0 execution job(s).` |

## Evidence boundaries

The E2E test uses the real durable contract, run, job, recovery-attempt, and
management-command boundaries. It uses a deterministic missing-provider test
double only at the provider adapter edge; no synthetic execution state or
parallel queue is used. The live controller check above is intentionally
no-op on the current local durable state and demonstrates safe repeated
operation. No production operation, credential change, or unrelated Sprint
was performed.

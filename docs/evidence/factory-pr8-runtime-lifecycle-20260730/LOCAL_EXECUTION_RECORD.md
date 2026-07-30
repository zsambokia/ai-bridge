# Factory Development Mode execution record — PR #8 and runtime lifecycle

## Authority and boundary

Product Owner Factory Development Mode authorization received on 2026-07-30
for `zsambokia/ai-bridge`: make PR #8 main-compatible; implement governed
cancellation and provider-terminal canonical lifecycle repair; validate,
migrate, deploy, verify runtime, and reconcile execution
`c7c47b9e-6f3c-4932-9812-e2b6461bb4c4` to `BLOCKED_EXTERNAL_INPUT`.

The authorization explicitly permits local repository and target-runtime repair
without a Bridge-issued running execution or active provider heartbeat. It does
not authorize unrelated changes or history rewrites.

## Baseline and repository binding

| Field | Value |
| --- | --- |
| Repository | `zsambokia/ai-bridge` |
| Remote | `https://github.com/zsambokia/ai-bridge.git` |
| Branch | `main` (main-only development) |
| Baseline / `origin/main` | `dc261c1485b82ee4882fae3b1b7f300fe36622d6` |
| PR #8 head | `43e5b75dfb961840052d9779e1679b3d8d9ac418` |
| PR #8 base | `af4800b9ebe5cf2496ca6aa48404f78e51f0c6df` |
| PR #8 state at intake | open draft; not merged |

## Intake inventory — preserved existing work

No existing modification has been reset, deleted, staged, or overwritten.

| Path(s) | Intake classification | Disposition |
| --- | --- | --- |
| `projects/contracts.py`, `projects/execution.py`, `projects/governed_mcp.py`, `projects/workspace.py`, `projects/tests/test_contracts.py`, `projects/tests/test_execution.py` | Workspace provisioning / pre-execution recovery | Retained and integrated: it is directly compatible with queue release and lifecycle repair. `execution.py`, `governed_mcp.py`, and `test_execution.py` also received the scoped cancellation/terminalization changes. |
| `projects/force_terminalization.py`, `projects/management/commands/force_terminalize_execution.py`, `projects/tests/test_force_terminalization.py`, `projects/tests/test_workspace.py` | Break-glass terminalization / workspace test work | Retained and integrated after compatibility validation. The legacy-event fixture was adjusted so break-glass coverage remains meaningful after normal provider events became canonically terminal. |
| `docs/operations/BREAK_GLASS_EXECUTION_TERMINALIZATION.md`, `docs/evidence/factory-break-glass-force-terminalization-20260730/` | Break-glass operational evidence | Retained and integrated; no historical evidence was overwritten. |
| `docs/sprints/03f6bdb2-3a2d-40d7-8f39-2583866c1007-sprint-2-recovery-django-admin-s-k-telez-c-lrepo.md`, `docs/sprints/2a369c16-1679-4ffa-84e1-73e8ad4e095e-sprint-2-fix-lifecycle-lez-r-si-audit.md`, `docs/sprints/71f1d36b-0833-400f-927a-6583d0fc607d-sprint-2-mes-l-az-erd-django-admin-teljes-megval.md`, `docs/work-items/270e42be-6e10-46ee-8d04-587d20b180f9-cloud-sql-folyamatos-fut-s-nak-s-k-lts-g-nek-cs-.md` | Other project/work-item material | Out of scope and preserved unchanged. |

This record itself is the first scope-owned, uncommitted artifact. Subsequent
entries will bind implementation, runtime intervention, migration, validation,
and final per-file disposition to the final commit.

## Implemented integration

- Integrated PR #8's governed cancellation capability as a three-stage public
  MCP flow: `execution.prepare_cancel`, `execution.confirm_cancel`, then
  `execution.cancel`.  The request is durable, caller-bound, confirmation
  bound, and idempotent; the final operation requests provider cancellation or
  terminalizes an already-finished provider without restarting it.
- Added `ExecutionRun.CANCELLING` and durable `ExecutionCancellation`, with
  migration `0033_executioncancellation_executionrun_cancelling`.
- Made normal `PROVIDER_COMPLETED` / `turn.completed` ingestion atomically
  terminalize the run, job, and running contract.  A provider terminal state is
  now a canonical lifecycle outcome rather than a reason to leave a governed
  execution running.
- Made scheduled recovery inspect provider state even when a heartbeat or lease
  looks fresh: a verified `FINISHED` provider is terminalized, never restarted.
- Preserved the Product Owner-authorized local break-glass command as a narrow,
  workspace-preserving recovery route for legacy records.

## Migration, runtime deployment, and historical reconciliation

`python manage.py migrate` applied migration `0033` to the active local runtime.
The running Django service and the scheduled recovery reconciler share this
checkout, so the source reload plus migration is the deployed local runtime
state. Its configured public-host allowlist intentionally rejects an unlisted
`localhost`/`127.0.0.1` Host header with HTTP 400; this is not a health failure.

The target execution `c7c47b9e-6f3c-4932-9812-e2b6461bb4c4` was observed with
provider process `5500` in `FINISHED` state and a historical
`PROVIDER_COMPLETED` event. Reconciliation recorded event sequence `10819`,
`PROVIDER_TERMINAL_RECONCILED`, and produced this coherent terminal state:

| Record | Final state |
| --- | --- |
| Execution run | `BLOCKED_EXTERNAL_INPUT`, phase `PROVIDER_TERMINALIZED` |
| Queue job | `FAILED`, no active lease/recovery schedule |
| Execution contract | `CANCELLED`, closure `BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE` |

## Validation from final source state

| Gate | Result |
| --- | --- |
| Targeted lifecycle, cancellation, break-glass, workspace, and contract tests | `79 passed` |
| Full test suite | `188 passed` |
| `ruff check .` | pass |
| `mypy .` | pass, 139 source files |
| `python manage.py validate_scopes` | pass |
| `python manage.py makemigrations --check --dry-run` | pass; no changes detected |
| `git diff --check` | pass; line-ending warnings only |

## Final disposition

- **Retained and modified/integrated:** all changed `projects/*.py` and
  `projects/tests/*.py` files listed above, migration `0033`, the break-glass
  operation/evidence, and this record.
- **Preserved outside scope:** the three numbered sprint documents and the
  `270e42be...` work-item document listed in the intake table.
- **Discarded:** none.  No reset, deletion, history rewrite, or unverified
  overwrite was performed.

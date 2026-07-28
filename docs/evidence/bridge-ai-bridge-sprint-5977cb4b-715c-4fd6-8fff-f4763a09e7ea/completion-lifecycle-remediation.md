# Execution completion lifecycle remediation

- Scope: `bridge:ai-bridge:sprint:5977cb4b-715c-4fd6-8fff-f4763a09e7ea`
- Contract: `bridge:ai-bridge:contract:87bcd547-56ab-4e63-a052-30675b1117f1`
- Execution token: `f1e9efba-665d-41e8-878a-8c7c090e281e`
- Baseline: `6cc1f0ffb689347d2ed8d7e28fb1611ce4981896`

## Defect and cause

The governed `scope.complete_execution` path verified the completed provider,
Release Gate evidence, and final commit; it then completed the `ExecutionRun`,
`ExecutionContract`, and `ConversationOrchestration`. It did **not** transition
the already-approved `ExecutableScope` to `COMPLETED`. A separate
`scope.complete` operation did so, but it required a new approval. This created
an unnecessary manual Product Owner-review stop after an evidence-backed PASS.

The unrelated stale-PID `RUNNING` recovery defect is not modified by this
remediation.

## Corrected invariant

When `scope.complete_execution` has verified a stopped provider, all required
evidence files, non-empty changes, and PASS gate results, it atomically:

1. completes the execution run with terminal state `PASS`;
2. completes the issued execution contract using its immutable allowed closure
   state;
3. completes the approved executable scope and removes its execution
   authorization; and
4. completes the orchestration flow and records its audit event.

No new approval is created or required. If any of these durable transitions
fails, the database transaction rolls back.

The issued contract's historical `allowed_terminal_states` field still contains
`PASS — READY FOR PRODUCT OWNER REVIEW`; it is retained as an immutable
contract compatibility value. It no longer represents an actionable execution
state: the run is `PASS`, and the execution, contract, flow, and scope are
`COMPLETED`.

## Verification

Executed on the final working tree before commit:

- `pytest -q` — **PASS**, 131 passed
- `ruff check .` — **PASS**
- `mypy .` — **PASS**, 106 source files
- `python manage.py validate_scopes` — **PASS**
- `python manage.py makemigrations --check --dry-run` — **PASS**, no changes

Regression coverage: `test_evidence_backed_completion_closes_the_approved_scope_without_new_review`
constructs an approved scope and a RUNNING contract/run/flow, supplies real
evidence paths and all-PASS gates, and proves that the resulting run, contract,
flow, and scope are all `COMPLETED` while the Product Owner approval count stays
at one.

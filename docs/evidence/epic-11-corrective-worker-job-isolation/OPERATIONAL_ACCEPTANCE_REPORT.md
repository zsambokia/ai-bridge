# Epic #11 Corrective Work Item — Operational Acceptance Report

## Scope and authority

Product Owner decision dated 2026-07-29 authorized this narrowly scoped Epic
#11 corrective Work Item. The objective is **FAIL THE JOB, NOT THE WORKER**:
an immutable, invalid execution contract must be rejected without provider
startup or worker termination, while a following valid queue item remains
processable.

## Design evidence

| Requirement | Evidence |
| --- | --- |
| Contract validation remains strict | `start_run` still calls `validate_issued_execution_contract` before resolving or starting a provider. |
| Scope-binding mismatch is non-retryable | `is_non_retryable_execution_failure` classifies the exact `CONTRACT_INTEGRITY_FAILURE:` family at the worker boundary. |
| Failed job is durable and terminal | `reject_claimed_job` records `ExecutionJob.REJECTED`, clears lease fields, stores structured reconciliation evidence, and emits `EXECUTION_JOB_REJECTED`. |
| Run no longer blocks active execution | The rejection transitions the related run to `FAILED_GOVERNANCE` and records an explicit terminal reason. |
| Worker stays available | `run_execution_worker` rejects only classified non-retryable errors and continues its loop; unclassified errors still fail closed. |

## Required validation

The final operational evidence must record all of the following against the
deployed commit:

1. Repository release gate: full pytest, Django check, Ruff, Ruff format, and
   mypy.
2. Migration plan and applied migration `0029_executionjob_rejected`.
3. Smoke run with a malformed scope-bound contract followed by a valid contract
   in the same worker invocation.
4. Read-only confirmation that Run #27 retains its recovery-review audit trail
   and that Run #28 / Contract #40 were not rewritten.

## Result

Pending final deployed-runtime verification and smoke evidence.

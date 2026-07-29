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

## Validation results

| Check | Result | Evidence |
| --- | --- | --- |
| Repository release gate | PASS | `scripts.release_gate`: Django check PASS, 159 pytest tests PASS, Ruff PASS, Ruff format PASS, mypy PASS. |
| Migration validation | PASS | `makemigrations --check --dry-run` reported no changes; migration plan contained only `projects.0029_executionjob_rejected`; 0025 through 0029 are applied. |
| Worker continuation smoke | PASS | `test_worker_continues_from_rejected_contract_to_next_valid_job` invoked one worker on two malformed contracts followed by a valid contract. Both malformed jobs were rejected without provider start; the valid job was then started by that same worker. |
| Restart / reclaim safety | PASS | `test_invalid_contract_is_rejected_without_provider_or_reclaim` proves a rejected job is not reclaimable by a later worker. |
| Live Run #28 handling | PASS | Worker `stage-worker-1 --once` emitted `EXECUTION_JOB_REJECTED` for the exact scope-binding mismatch and exited successfully after the job-level decision. |
| Run #28 immutable evidence | PASS | Contract #40 remains hash `88d41ecfa42050ac0add0a7e19c4bb9b96a913fe02826821e5e7e3552ce9f055` and still lacks `approved_scope.proposal_hash`; it was not rewritten. |
| Run #27 audit preservation | PASS | Run #27 remains `BLOCKED_EXTERNAL_INPUT` / `RECOVERY_REVIEW_REQUIRED`, with its review-terminalization event retained. |
| Stage runtime | PASS | Stage service was restarted from repository commit `7c57cd1bcc80a77aaf24ebc7b1566b65da8bd49a`; `/health/` returned `{"status":"ok","service":"ai-bridge"}`. |

## Live state after acceptance

- Run #28 job: `REJECTED`; lease owner and expiry cleared.
- Run #28 lifecycle/phase: `FAILED_GOVERNANCE` / `CONTRACT_REJECTED`.
- Run #28 terminal state: `REJECTED — NON-RETRYABLE CONTRACT INTEGRITY FAILURE`.
- Run #28 provider execution identifier: empty; no provider was started.
- Structured rejection evidence records the exact failure, `retryable: false`,
  worker `stage-worker-1`, Contract #40 identity/hash, and
  `provider_started: false`.

## Result

**PASS — READY FOR PRODUCT OWNER REVIEW.** The corrective implementation
preserves validation strictness, fails immutable invalid jobs durably, and lets
the worker continue safely to subsequent queue work.

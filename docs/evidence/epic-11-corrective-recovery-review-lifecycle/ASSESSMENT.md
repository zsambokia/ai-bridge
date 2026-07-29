# Epic #11 Corrective Work Item — Assessment

## Authority and baseline

- Product Owner authority: `product-owner-decision-2026-07-29-epic-11-corrective-work-item`
- Repository: `zsambokia/ai-bridge`
- Branch: `main`
- Baseline: `09f49196206d2e934a7a60d0300b912d1ec871bf`
- Work item: `docs/work-items/e11-corrective-recovery-review-lifecycle.md`

## Finding

`projects.execution_recovery.reconcile_execution_jobs` already recorded an
unsafe recovery as `ExecutionJob.Status.RECOVERY_REVIEW_REQUIRED` with durable
evidence. It updated only `ExecutionRun.current_phase` and
`current_blocker`; it did not transition `ExecutionRun.lifecycle` out of
`projects.execution.ACTIVE_STATES`.

`projects.execution.start_run` correctly rejects any active same-project,
same-branch run with `CONFLICTING_ACTIVE_EXECUTION`. Therefore the missing
lifecycle transition, rather than the queue or active-execution guard, caused
the permanent block.

## Reuse and repair

The repair extends the canonical `reconcile_execution_jobs` controller. No
second recovery service, queue, provider path, migration, or lifecycle model
was introduced. The controller now has one idempotent terminalization helper
used for both new and legacy review-required decisions.

## Explicit exclusions

Runtime build-SHA exposure was identified separately during the prior
Operational Acceptance. It is not changed by this narrowly authorized
corrective Work Item.

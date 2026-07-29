# Epic #11 Operational Acceptance Report — 2026-07-29

## Outcome

`BLOCKED — BUSINESS DECISION REQUIRED`

The accepted Epic #11 revision was deployed to the stage runtime, its database
migrations are active, and the durable recovery controller made the required
non-fabricated decision for Run #27.  Operational acceptance cannot truthfully
be declared because the accepted revision leaves a recovery-review-required
run in the active `RUNNING` lifecycle.  It therefore still blocks Run #28.

## Deployed runtime evidence

- Repository branch: `main`
- Runtime source commit: `09f49196206d2e934a7a60d0300b912d1ec871bf`
- Epic acceptance commit: `44d23fcf9de6bbe0890e811ee04b65fe9f688e01`
- The Epic commit is an ancestor of the deployed commit (via merge commit
  `53bf6d718bc0594a6cc669959510e9bbd45d2a57`).
- The stage process was restarted from this checkout and `/health/` returned
  HTTP 200 on both localhost and the stage URL.
- Django migrations `0025_external_execution_reconciliation`,
  `0026_execution_recovery`, `0027_technicalremediationloop`, and
  `0028_executionjob_completed` are applied.
- A Windows Task Scheduler task named
  `AI-Bridge-Execution-Recovery-Reconciler` runs
  `manage.py reconcile_execution_jobs --once` every minute.  Its first
  supervised run returned exit code `0`.

## Governed Run #27 recovery evidence

At `2026-07-29T07:55:59.611079+00:00`, the reconciler observed:

- provider state: `FINISHED`
- expired lease: `2026-07-29T07:21:03.912506+00:00`
- no resumable checkpoint (`{}`)

It created durable recovery attempt `RECOVERY_REVIEW_REQUIRED` with reason
`provider unavailable and recovery cannot be verified safe`, wrote event 167
`RECOVERY_REVIEW_REQUIRED`, and set the job status to
`RECOVERY_REVIEW_REQUIRED`.  No completion record or fabricated final commit
was written.

## Blocking defect

`projects/execution_recovery.py` records the recovery-review-required job and
phase, but does not change `ExecutionRun.lifecycle` from `RUNNING`.  The
conflict check in `projects/execution.py` treats `RUNNING` as active, so Run
#28 remains blocked by `CONFLICTING_ACTIVE_EXECUTION`.

This is demonstrably present in the deployed source.  The recovery test asserts
the job state and phase, but does not assert a terminal/non-active run lifecycle
or queue progress for the next run.

There is also no runtime build identifier in the deployed `/health/` response;
the deployed commit was verified from the restarted process checkout rather
than exposed by the application.

## Required follow-up scope

A governed corrective change is required to define and test the lifecycle
transition after `RECOVERY_REVIEW_REQUIRED` and to expose a runtime build
identifier.  That is a code and acceptance-scope change, not a safe operational
configuration adjustment.  Until it is approved and deployed, do not manually
alter Run #27 or force Run #28 past the active-run guard.

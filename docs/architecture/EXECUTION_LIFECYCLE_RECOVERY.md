# Canonical execution lifecycle recovery

## Scope

This document defines the recovery invariants implemented for Sprint 016,
Canonical Execution Lifecycle Integrity and Autonomous Recovery. It applies to
the existing `ExecutionRun`, one-to-one `ExecutionJob`, and one-to-one
`ExecutionWorkspace` records; it does not introduce a second execution state
store or a parallel queue.

## Durable invariants

1. A worker may claim only a queued, expired-lease, or due-recovery job whose
   run is active. A terminal run is never dispatchable.
2. A claimed worker rechecks ownership and the run lifecycle in the same
   database transaction immediately before provider work begins. A concurrent
   terminal transition therefore cannot start a duplicate provider attempt.
3. A terminal run with an active job converges the job to a terminal status.
   An active run with a terminal job fails closed as
   `BLOCKED_EXTERNAL_INPUT` until a governed repair creates an explicit new
   path. Both decisions have an event, reconciliation evidence, and an
   append-only recovery attempt.
4. Recovery is bounded by the persisted attempt count. A missing checkpoint or
   exhausted retry limit leads to `RECOVERY_REVIEW_REQUIRED`, followed by the
   canonical terminal review lifecycle; it never loops indefinitely.
5. An `IN_USE` workspace whose locally recorded provider PID is no longer
   alive is reset to `READY` before recovery. A workspace attached to a
   terminal run is retained exactly once and its PID is cleared. Retention has
   a persisted policy reason as well as an expiry.
6. Every lease claim increments a persisted fencing token. A worker must
   present the token it was issued before it may heartbeat, start, reject, or
   fail work. An expired worker cannot write after a replacement claim.

All reconciliation decisions are idempotent: a subsequent pass sees the
converged state and makes no duplicate transition or audit record.

## Controller and recovery procedure

The deployment entry point is:

```text
python manage.py reconcile_execution_jobs --once
```

It inspects expired leases, provider status, checkpoint availability, local
workspace PID liveness, and run/job consistency. It either queues a safe
reattach, schedules a bounded checkpoint recovery, requests terminal review,
or records no action. The controller is safe to run repeatedly. Workspace
ownership cleanup is also included in `WorkspaceManager.reconcile_cleanup()`.

## Classification contract

`classify_execution_recovery()` derives a structured recovery decision solely
from durable run, job, workspace, contract, checkpoint, and provider-PID facts.
It returns a classification, factual inputs, evidence references, permitted
next actions, remaining retry budget, and an explicit statement that routine
technical recovery never needs Product Owner involvement. Reconciliation
persists the selected classification and permitted actions with its append-only
attempt evidence.

## Operations visibility

`ExecutionRun` administration exposes a read-only recovery summary with queue
state, lease expiry, heartbeat, recovery count/action, workspace status, and
whether a PID is recorded. The public `execution.get_run_status` MCP response
provides the same safe projection without exposing worker identifiers or PID
values. It also includes evidence root, final commit SHA, and terminal state.

## Verification

The Sprint 016 evidence package records fault injection for a dead worker,
missing workspace PID, run/job divergence, retry-limit review, duplicate
dispatch prevention, and the management-command recovery E2E path. The
repository-wide Release Gates remain the authoritative final verification.

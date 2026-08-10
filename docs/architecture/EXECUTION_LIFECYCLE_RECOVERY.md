---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

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

## Provider-completion finalization

`PROVIDER_COMPLETED` is provider activity evidence, not canonical completion
evidence. A terminal provider event therefore cannot directly cancel the
contract or classify a live run as `BLOCKED_EXTERNAL_INPUT`. The event handler
atomically moves the run and workspace to `VALIDATING`, clears the live PID
projection, and queues the same job with the
`FINALIZE_PROVIDER_COMPLETION` recovery action.

The finalization worker inspects the isolated repository (`HEAD` and porcelain
status) before it determines the next safe action. It records either a
distinct `NO_CHANGE` outcome or `CANONICAL_COMPLETION_MISSING` facts, retains
the workspace with a policy reason, and schedules bounded recovery from the
same accepted contract. It never invents a final SHA, delivery receipt,
deployment verification, or scope completion from a successful provider exit.
A duplicate terminal event observes the already-pending finalization and
creates neither a second recovery path nor a duplicate delivery path.

All reconciliation decisions are idempotent: a subsequent pass sees the
converged state and makes no duplicate transition or audit record.

## Pre-workspace provisioning recovery

A `STARTING` run has no provider identity while the worker is creating its
isolated checkout, virtual environment, application database, seed state, and
runtime bootstrap. Provider reconciliation cannot recover that interval.
`reconcile_execution_jobs` therefore separately examines leased, provider-free
provisioning jobs. An expired lease or stale heartbeat records an append-only
`WORKSPACE_PROVISIONING_RECOVERY_QUEUED` attempt, clears the lease, and queues
the same job for bounded recovery. An unexpected worker exception follows the
same path. After three attempts it records
`WORKSPACE_PROVISIONING_RECOVERY_EXHAUSTED` and the canonical external-review
state; it never leaves a quiet worker with an unclassified intermediate run.

## Sprint 7 autonomous technical remediation

Provisioning has a specialised recovery path because the provider does not yet
exist. Every other unexpected worker exception takes a different, durable
path: it is held as a technical-remediation incident rather than being silently
reclaimed, abandoned, or reported as a Product Owner decision. The worker
clears its lease, marks the durable job `FAILED`, and puts its parent run into
`REPAIRING` with the original lifecycle, phase, and blocker retained as a
resume checkpoint.

The remediation opening transaction records an incident, evidence references,
an ownership assessment, a bounded child work scope, and an Orki audit record.
Only a successful independent validation of the invalidated gate may close the
incident, publish its reviewable AKB lesson, restore that exact checkpoint, and
queue the same failed job with `RESUME_AFTER_TECHNICAL_REMEDIATION`. A failed
validation leaves the repair visible and does not resume work.

The same run and gate may open at most three distinct technical-remediation
loops. The next attempt is explicitly audited as
`AUTONOMOUS_REMEDIATION_LIMIT_EXCEEDED`; this is a bounded-loop safeguard, not
a hidden retry. A genuine business choice follows the separate, concise
`TechnicalRemediationEscalation` path and moves the run to
`BLOCKED_BUSINESS_DECISION`; routine implementation questions never use that
path. Django Admin and `execution.get_run_status` project these same durable
loop, validation, incident, and escalation records read-only.

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

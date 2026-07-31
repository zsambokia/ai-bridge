# Sprint 016 — Canonical Execution Lifecycle Integrity and Autonomous Recovery

**Status:** DRAFT — PRODUCT OWNER REVIEW REQUIRED
**Execution authority:** NONE
**Execution level:** SPRINT
**Task type:** RECOVERY
**Target branch:** `main`

## Purpose

Make the canonical execution lifecycle deterministic, convergent, and safe without routine Product Owner/operator intervention. This responds to the 2026-07-31 Factory Readiness Audit; it does not authorize runtime work until the normal scope, confirmation, approval, publication, contract, and execution flow completes.

## Preconditions and boundaries

- Bind to the approved Project Context, Constitution, workflow, exact approved scope, contract, baseline, and policy at execution time.
- Reuse `ExecutionRun`, `ExecutionJob`, workspace, provider, recovery, remediation, audit, and governed MCP boundaries; no parallel lifecycle or synthetic success path.
- Preserve immutable evidence, approvals, scope isolation, and idempotency; never rewrite stale records as success.
- Exclude unrelated features, credential changes, production-infrastructure changes, and weakening governance or Release Gates unless separately approved.

## Required implementation scope

1. Define and enforce lifecycle invariants across run, job, workspace, provider, contract, scope, evidence, and terminal state.
2. Detect/classify stale jobs, expired leases, dead provider PIDs, orphaned workspaces, missing checkpoints, and run/job terminal-state divergence.
3. Implement deterministic, idempotent reconciliation: safe reattach, bounded retry/resume, replacement worker, review-required terminalization, or explicit governed blocker. No duplicate provider starts, events, recovery records, or finalization.
4. Make worker survival explicit: bad job, known governance rejection, provider crash, or reload must not kill the worker or strand subsequent jobs; lease/heartbeat transitions stay atomic and observable.
5. Prevent duplicate execution across dispatch, reclaim, restart, and reconciliation, including conflicting active-scope ownership.
6. Align Django admin and governed API/MCP projections with canonical state and expose safe observability for lifecycle, recovery decision, provider liveness, lease, checkpoint, workspace, and idempotency evidence.
7. Add fault injection and real E2E proof for worker death, PID disappearance, lease expiry, reload, stale workspace, duplicate dispatch, provider interruption, retry exhaustion, successful recovery, and honest blocking. Evidence must include repository delivery and show no technical blocker remains before closure.

## Acceptance criteria

| Scenario | Required result |
| --- | --- |
| Worker dies after leasing work. | One replacement path reclaims/reconciles it; no duplicate provider run or lost audit trail. |
| Provider PID is absent. | Resume only from a safe checkpoint, otherwise honestly review-block/terminalize with durable evidence. |
| Run and job disagree. | Reconciliation converges them by explicit invariant and idempotent decision evidence. |
| Duplicate dispatch/retry arrives. | Return the original binding or fail closed; never create a second active execution. |
| Recovery limit is crossed. | Bounded retry stops, root cause persists, and legitimate canonical terminal/blocker state is reached. |
| Admin and MCP inspect one record. | Both show consistent lifecycle, lease, recovery, and evidence projections. |
| Real governed E2E recovery completes. | Repository delivery, fresh Release Gates, evidence binding, and operational acceptance are proven. |

## Required evidence and Release Gates

- lifecycle-invariant assessment; migration/compatibility assessment where persistence changes;
- focused recovery, worker, API/admin, and idempotency tests;
- fault-injection and real governed E2E acceptance evidence;
- `pytest`, `ruff check .`, `mypy .`, `python manage.py validate_scopes`, and all contract-resolved Sprint gates;
- final closure report, machine/acceptance results, AKB/roadmap synchronization, final commit binding, and Product Owner review handoff.

## Cross-links

- [Factory Readiness Audit](../evidence/factory-readiness-audit-20260731/FACTORY_READINESS_AUDIT.md)
- [AKB baseline](../akb/FACTORY_READINESS_MATURITY_BASELINE_2026-07-31.md)
- [Roadmap](../roadmap/ROADMAP.md)

**No implementation begins from this file until it is converted into a reviewed, approved, published canonical scope and receives a valid Execution Contract.**

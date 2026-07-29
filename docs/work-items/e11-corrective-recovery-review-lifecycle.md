---
schema: ai-bridge-work-item/v1
schema_version: '1'
scope_kind: WORK_ITEM
identifier: bridge:ai-bridge:work-item:e11-corrective-recovery-review-lifecycle
project_id: ai-bridge
title: 'Epic #11 corrective: terminalize recovery review lifecycle'
status: APPROVED
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: BUGFIX
task_type: RECOVERY
work_type: RECOVERY
intent: >-
  Repair the Epic #11 recovery-review-required lifecycle gap so an unsafe
  recovery decision preserves review evidence but no longer retains an active
  execution slot or blocks the next queued governed execution.
risk_modifiers:
  - durable-lifecycle
  - operational-recovery
policy:
  resolved_profile: product-owner-bootstrap-corrective-work-item
  required_release_gates:
    - repository-wide
    - targeted-recovery-regression
    - operational-acceptance
  required_documentation_updates:
    - behavior
    - operational-evidence
approval_reference: product-owner-decision-2026-07-29-epic-11-corrective-work-item
created_by: AI_BRIDGE
created_at: '2026-07-29T00:00:00+00:00'
updated_at: '2026-07-29T00:00:00+00:00'
content_hash: cb3fb08b8daaf727218be1139f9dfcd5408f6ff962f8ea53ea82fe007e592d71
---

# Epic #11 Corrective Work Item — Recovery Review Lifecycle

## Product Owner authority

The Product Owner authorized this corrective Work Item following Operational
Acceptance. It is a repair of the accepted Epic #11 implementation, not a new
Epic, Sprint, capability, or architecture change.

## In scope

- A `RECOVERY_REVIEW_REQUIRED` decision must transition the `ExecutionRun` out
  of every active lifecycle state.
- The review phase, blocker, recovery history, and execution evidence must
  remain durable and inspectable.
- The next queued execution for the same project branch must pass the active
  execution guard and be processable through the canonical worker.
- Existing review-required active runs must be reconciled through the same
  governed recovery controller, idempotently.

## Explicit exclusions

- No new recovery strategy, provider behavior, queue model, migration, or
  architecture.
- No fabricated execution completion or final commit.
- No runtime build-SHA exposure work; that separately identified deployment
  observability gap remains outside this corrective Work Item.

## Acceptance criteria

1. Missing or unsafe checkpoint creates durable review-required evidence and a
   non-active `BLOCKED_EXTERNAL_INPUT` run with terminal state
   `BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`.
2. The phase remains `RECOVERY_REVIEW_REQUIRED` and blocker evidence remains
   available after terminalization.
3. A subsequent same-branch governed start no longer raises
   `CONFLICTING_ACTIVE_EXECUTION` solely because of that review-required run.
4. A previously persisted active review-required run is terminalized by the
   reconciler exactly once, without retrying or fabricating completion.
5. Repository gates and a fresh operational acceptance scenario pass.

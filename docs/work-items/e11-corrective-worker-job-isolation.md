---
schema: ai-bridge-work-item/v1
schema_version: '1'
scope_kind: WORK_ITEM
identifier: bridge:ai-bridge:work-item:e11-corrective-worker-job-isolation
project_id: ai-bridge
title: 'Epic #11 corrective: fail the job, not the worker'
status: APPROVED
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: BUGFIX
task_type: RECOVERY
work_type: RECOVERY
intent: >-
  Repair the Epic #11 worker reliability gap: an immutable, non-retryable
  contract or governance failure must terminalize only its queued execution and
  must not stop the independent worker or block the following valid execution.
risk_modifiers:
  - durable-lifecycle
  - contract-integrity
  - operational-recovery
policy:
  resolved_profile: product-owner-bootstrap-corrective-work-item
  required_release_gates:
    - repository-wide
    - targeted-worker-regression
    - migration-validation
    - operational-acceptance
  required_documentation_updates:
    - behavior
    - operational-evidence
approval_reference: product-owner-decision-2026-07-29-epic-11-worker-job-isolation
created_by: AI_BRIDGE
created_at: '2026-07-29T00:00:00+00:00'
updated_at: '2026-07-29T00:00:00+00:00'
content_hash: 9a9fef164ea048c40e9993918d88dee7b73eae00dad9ac64ddec69a977117b3b
---

# Epic #11 Corrective Work Item — Fail the Job, Not the Worker

## Product Owner authority

The Product Owner authorized this corrective Work Item after the operational
incident involving Run #28. It repairs the accepted Epic #11 implementation;
it neither introduces a new Epic/Sprint nor loosens contract integrity.

## In scope

- Classify immutable contract and governance execution failures as
  non-retryable at the worker boundary.
- Persist a terminal `REJECTED` job, release its lease, and record structured
  rejection evidence and an append-only event.
- Move the associated run to the non-active `FAILED_GOVERNANCE` lifecycle with
  an explicit terminal reason.
- Continue the same worker to the next queued job without starting a provider
  for a rejected execution.
- Ensure rejected jobs cannot be reclaimed after worker restart.

## Explicit exclusions

- No mutation, repair, supersession, or fabrication of the rejected immutable
  contract (including Run #28 / Contract #40).
- No weakening of contract, scope, approval, or consumption validation.
- No new recovery strategy or provider behavior.
- No change to Run #27's `RECOVERY_REVIEW_REQUIRED` evidence or its governed
  non-active lifecycle.

## Acceptance criteria

1. `CONTRACT_INTEGRITY_FAILURE:SCOPE_BINDING_MISMATCH` starts no provider,
   persists a non-retryable rejected job, releases its lease, and terminalizes
   the run outside active lifecycle states.
2. The durable evidence includes the reason, classification, worker identity,
   contract identity/hash, retryability, and provider-started status.
3. The worker continues and claims a following valid job; multiple rejected
   jobs do not create a crash loop.
4. A rejected job is never reclaimed after a worker restart.
5. Unclassified failures still fail closed rather than being silently treated
   as safe job-level rejections.

---
approval_reference: conversation-confirmation:v1:326666e8d7207e9f165e24abca0dfa946114defa4ce830681044c5d9ea42277f
audit:
  acceptance_checks:
  - repeatable static scans
  - call graph and state-ownership matrix
  - queue and lifecycle inventory
  - gap register and rollback plan
  - architecture-test specification
  - explicit R20-00 in-scope and out-of-scope determination
  audit_questions:
  - Which components, calls, durable states, queues, workers, and provider boundaries
    currently implement or bypass the constitutional route?
  - What evidence-backed, non-duplicating mapping connects Operational Work Item,
    ExecutionRun, and ExecutionJob?
  - Which constitutional gaps, prohibited edges, ownership conflicts, migration dependencies,
    and rollback constraints block R20-01 through R20-05?
  audit_target: Runtime 2.0 Constitution v1.0.0 compliance of the AI Bridge repository
    at the recorded FDM baseline, including the Execution Request -> MSM -> Operational
    Foundation -> ExecutionRun -> Provider Gateway route.
  mutation_policy: READ_ONLY
  repair_rule: No repair or runtime-authority change is permitted. Record a separately
    governed follow-up scope or a constitutional-amendment request for every remediation
    need.
  required_classifications:
  - Constitution-compliant
  - Gap
  - Prohibited direct edge
  - Authority conflict
  - Migration dependency
  - Constitutional amendment required
  required_inventory:
  - component and authority inventory
  - static call and dependency graph
  - durable state, queue, worker, lease, retry, recovery, telemetry, outbox, and evidence
    lifecycle inventory
  - ExecutionRun, ExecutionJob, and Operational Work Item mapping
  - provider gateway and direct-provider boundary inventory
  - migration dependency and rollback inventory
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: 2ca1a0b26e9a843284575c1972656f47dcc4e5b94394c493c9d7b3070aedf297
created_at: '2026-08-09T18:46:46.307334+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:c763bb47-74fa-4120-85a5-f8cf745ec262
intent: 'R20-00 Runtime 2.0 Compliance Baseline Sprint: produce a fresh Constitution
  Compliance Baseline and authoritative component, call, dependency, durable-state,
  and migration map for the Runtime 2.0 Constitution route. Determine the non-duplicating
  mapping between Operational Work Item, ExecutionRun, and the existing ExecutionJob,
  or record a constitutional-amendment request when compliance cannot be established.
  This is an AUDIT-only, read-only scope: it must not change runtime authority, create
  a second queue/work-item table/worker/lifecycle, or implement any R20-01 through
  R20-05 migration.'
policy:
  child_contract_required: false
  omission_justifications: []
  profile_version: '1.0'
  required_assessment_depth: extended
  required_documentation_updates:
  - architecture
  - akb
  - roadmap
  required_evidence_artifacts:
  - acceptance-results
  - assessment
  - closure-report
  - machine-results
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: sprint-audit
  review_requirements: []
project_id: ai-bridge
proposal_hash: e793250d4c01cdb5ea175820a37a68dd7ac76e22cb7ba9a6a0ceb7963ac0a198
proposal_version: 1
risk_modifiers: []
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: AUDIT
title: R20-00 Runtime 2.0 Compliance Baseline
updated_at: '2026-08-09T18:48:00.683285+00:00'
work_type: AUDIT
---

# R20-00 Runtime 2.0 Compliance Baseline

## Intent

R20-00 Runtime 2.0 Compliance Baseline Sprint: produce a fresh Constitution Compliance Baseline and authoritative component, call, dependency, durable-state, and migration map for the Runtime 2.0 Constitution route. Determine the non-duplicating mapping between Operational Work Item, ExecutionRun, and the existing ExecutionJob, or record a constitutional-amendment request when compliance cannot be established. This is an AUDIT-only, read-only scope: it must not change runtime authority, create a second queue/work-item table/worker/lifecycle, or implement any R20-01 through R20-05 migration.

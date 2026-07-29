---
approval_reference: conversation-confirmation:v1:7c75ece03dc781c959bfae2c0b93eccab5793e1b52f926d187e48bc97cd64819
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: cc3e1b8c5b77b70201c8568c35a388d79806a5453f4f4c0e7cc7b16a3cd64797
created_at: '2026-07-29T16:55:02.948405+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:work-item:250f7297-d5e1-4ba4-831c-c8f0471a375e
intent: 'Sprint 1 technical remediation continuation for the failed governed self-development
  E2E of AI Bridge. Repair the canonical AI Bridge execution provider lifecycle, recovery,
  checkpoint, workspace, and activity-evidence paths exposed by original scope bridge:ai-bridge:sprint:72d1fc5b-8b70-432d-bbd1-1e11eb580f0e.
  Apply missing canonical host migrations, never manually manipulate DB; add regression
  coverage; then perform a clean governed isolated E2E through real MCP/API. Preserve
  Sprint 1 acceptance: MCP_TEST_API_TOKEN authorization, isolated worktree/venv, isolated
  DB migration plus deterministic seed, provider lifecycle/cleanup, ExecutionRunAdmin
  Run ID first data column. Use canonical recovery events and bounded auditable retry
  through existing events/JSON metadata only. No new persistent Django model and no
  Sprint 2 work.'
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
  resolved_profile: sprint-recovery
  review_requirements: []
project_id: ai-bridge
proposal_hash: f6c9a4f4631566c9c2870bdab3a30c99bb61d6b6c7aeeb317ff0abee2016858e
proposal_version: 1
risk_modifiers: []
schema: ai-bridge-work-item/v1
schema_version: '1'
scope_kind: WORK_ITEM
status: APPROVED
task_type: RECOVERY
title: Sprint 1 factory E2E technical remediation
updated_at: '2026-07-29T16:55:10.507194+00:00'
work_type: RECOVERY
---

# Sprint 1 factory E2E technical remediation

## Intent

Sprint 1 technical remediation continuation for the failed governed self-development E2E of AI Bridge. Repair the canonical AI Bridge execution provider lifecycle, recovery, checkpoint, workspace, and activity-evidence paths exposed by original scope bridge:ai-bridge:sprint:72d1fc5b-8b70-432d-bbd1-1e11eb580f0e. Apply missing canonical host migrations, never manually manipulate DB; add regression coverage; then perform a clean governed isolated E2E through real MCP/API. Preserve Sprint 1 acceptance: MCP_TEST_API_TOKEN authorization, isolated worktree/venv, isolated DB migration plus deterministic seed, provider lifecycle/cleanup, ExecutionRunAdmin Run ID first data column. Use canonical recovery events and bounded auditable retry through existing events/JSON metadata only. No new persistent Django model and no Sprint 2 work.

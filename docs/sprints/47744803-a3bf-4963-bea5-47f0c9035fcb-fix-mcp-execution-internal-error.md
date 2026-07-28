---
approval_reference: conversation-confirmation:v1:075ad0d6650562626806bf8d1363896490a14118d2c6074b0eb08b93e5293abe
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: d2d07c225cc9f1a88527191d7d397b5a59951064a20988e9d259b31cce1e0579
created_at: '2026-07-28T11:35:12.555534+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:47744803-a3bf-4963-bea5-47f0c9035fcb
intent: 'BUGFIX: Repair the AI Bridge execution subsystem in zsambokia/ai-bridge.
  The MCP tools execution.get_run_status, execution.get_activity_summary, execution.list_events,
  and execution.cancel currently surface -32603 Internal error for expected execution-token
  lookup failures. Repair their canonical execution path, validation, error mapping,
  cancellation robustness, tests, documentation and evidence. Deploy to stage and
  smoke-test the four tools. Do not reuse or mutate bridge-demo sprint authority;
  do not directly manipulate any execution records in the database.'
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
  - compatibility-validation
  - integration-validation
  - machine-results
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: sprint-bugfix
  review_requirements:
  - compatibility-validation
  - integration-validation
project_id: ai-bridge
proposal_hash: 6844d22795b10201d45dc2cb3438d47403c45b138778dfe07ddfbc14d3edd696
proposal_version: 1
risk_modifiers:
- EXTERNAL_INTEGRATION
- PUBLIC_API_OR_PROTOCOL
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: BUGFIX
title: Fix MCP Execution Internal Error
updated_at: '2026-07-28T11:35:26.429684+00:00'
work_type: BUGFIX
---

# Fix MCP Execution Internal Error

## Intent

BUGFIX: Repair the AI Bridge execution subsystem in zsambokia/ai-bridge. The MCP tools execution.get_run_status, execution.get_activity_summary, execution.list_events, and execution.cancel currently surface -32603 Internal error for expected execution-token lookup failures. Repair their canonical execution path, validation, error mapping, cancellation robustness, tests, documentation and evidence. Deploy to stage and smoke-test the four tools. Do not reuse or mutate bridge-demo sprint authority; do not directly manipulate any execution records in the database.

---
approval_reference: conversation-confirmation:v1:a692dffb5bbc0fb0f0b050c1f72bcb9e123ac46a0f56d145b83b5b6e312e3b61
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: b0c6b6176c7f69c5301f24be883b5a561844a7117e004b79d4dfc2310c48d74a
created_at: '2026-07-28T11:51:17.205032+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:b97d6773-17ea-4643-b2a5-61965eb4f57c
intent: 'BUGFIX for zsambokia/ai-bridge: when scope orchestration is BLOCKED at EXECUTION
  with CONFLICTING_ACTIVE_EXECUTION, return the conflicting active execution_token
  in scope.orchestration_status so the caller can invoke governed execution.cancel;
  preserve contract ownership and authorization. Add regression tests, documentation,
  and stage verification.'
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
  - authorization-validation
  - closure-report
  - compatibility-validation
  - machine-results
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: sprint-bugfix
  review_requirements:
  - authorization-validation
  - compatibility-validation
project_id: ai-bridge
proposal_hash: 828859b1f84f2a812b97dd94367db835f8cc50667b1fa5c531a8d75c577dcb6e
proposal_version: 1
risk_modifiers:
- AUTHENTICATION_OR_AUTHORIZATION
- PUBLIC_API_OR_PROTOCOL
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: BUGFIX
title: Expose Conflicting Execution Token
updated_at: '2026-07-28T11:51:20.718204+00:00'
work_type: BUGFIX
---

# Expose Conflicting Execution Token

## Intent

BUGFIX for zsambokia/ai-bridge: when scope orchestration is BLOCKED at EXECUTION with CONFLICTING_ACTIVE_EXECUTION, return the conflicting active execution_token in scope.orchestration_status so the caller can invoke governed execution.cancel; preserve contract ownership and authorization. Add regression tests, documentation, and stage verification.

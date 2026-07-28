---
approval_reference: conversation-confirmation:v1:7b2f111d91053dca3c1571c1a5e91bfc7ac6428ea874caa458315b04021bdf43
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: baa6f4872b3ba9777a47273e536c9bbe126bfc64ec2f4f0b2e9167306c1ca180
created_at: '2026-07-28T12:23:26.766438+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:e626a32e-b18a-415e-bfe2-5d2baf8bf1b2
intent: Repair the AI Bridge approval and execution recovery workflow so a browser
  refresh, ChatGPT tool-session change, MCP disconnect, or a missed affirmative reply
  can be recovered durably. Reuse the canonical GovernanceApproval and ConversationOrchestration
  records; expose safe scope recovery discovery and a version/hash-bound authenticated
  Product Owner resume confirmation. Do not create a parallel approval system. Add
  tests, documentation, evidence, and deploy to stage after all release gates pass.
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
proposal_hash: 8f8279a497ca950eee5b37b387516007620d0afa78ad73bebc56e2290909941c
proposal_version: 1
risk_modifiers:
- AUTHENTICATION_OR_AUTHORIZATION
- PUBLIC_API_OR_PROTOCOL
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: BUGFIX
title: Recover Interrupted Approval Sessions
updated_at: '2026-07-28T12:23:32.594941+00:00'
work_type: BUGFIX
---

# Recover Interrupted Approval Sessions

## Intent

Repair the AI Bridge approval and execution recovery workflow so a browser refresh, ChatGPT tool-session change, MCP disconnect, or a missed affirmative reply can be recovered durably. Reuse the canonical GovernanceApproval and ConversationOrchestration records; expose safe scope recovery discovery and a version/hash-bound authenticated Product Owner resume confirmation. Do not create a parallel approval system. Add tests, documentation, evidence, and deploy to stage after all release gates pass.

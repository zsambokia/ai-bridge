---
approval_reference: conversation-confirmation:v1:d39a1e013403bc73c75976f026babe882bc8fd8f50c5e55d5dff82a0a04b476d
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: 84a1a6fe9c535fd1f95bfa6fc4cc268a759f4d18715eb773c3f52b20b18f2ea6
created_at: '2026-07-28T07:28:10.107658+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:74dc801b-8295-4d96-9896-22e4dc37ad31
intent: 'Execute the approved Sprint 015 V2 specification from docs/sprints/SPRINT_015_REAL_TIME_DEV_EXECUTION_ACTIVITY_AND_CHECKLIST.md
  in zsambokia/ai-bridge. Continue from the existing preserved worktree changes from
  Sprint 015 V1, but do not assume they are correct: assess, reuse, repair, and validate
  them against V2. Implement near-real-time canonical execution activity, derived
  checklist projection, Django admin visibility, MCP/ChatGPT projection, console output,
  repair visibility, and Execution Heartbeat plus Stalled Detection derived exclusively
  from canonical progress events and run timestamps. Also implement the Product Owner
  scope-amendment UX as part of this Sprint: when a running governed execution receives
  a requested scope-changing addition, AI Bridge must present a concise approval prompt
  containing the proposed additions and a single Product Owner approval action, then
  use the existing governance flow to create a new proposal version and a fresh hash-bound
  Execution Contract. The provider must never self-approve or self-issue a contract.
  The UX may hide hashes and contract identifiers under technical details, but all
  governance artifacts must remain durable and auditable. Use no employee system,
  no fictional actors, no meeting threads, no parallel lifecycle, no fake progress,
  no fake blocker, and no fake failure. Produce evidence only after the fresh V2 contract
  is issued and all V2 acceptance criteria pass.'
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
  resolved_profile: sprint-self_development
  review_requirements:
  - compatibility-validation
  - integration-validation
project_id: ai-bridge
proposal_hash: b5785e80a6d80924d28275a19adf2ebdc68482a78530eb1c86e7f5b1b6d7f995
proposal_version: 1
risk_modifiers:
- EXTERNAL_INTEGRATION
- PUBLIC_API_OR_PROTOCOL
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: SELF_DEVELOPMENT
title: Sprint 015 V2 — Real-Time DEV Execution Activity, Checklist, Heartbeat and
  Stalled Detection
updated_at: '2026-07-28T07:29:19.397748+00:00'
work_type: SELF_DEVELOPMENT
---

# Sprint 015 V2 — Real-Time DEV Execution Activity, Checklist, Heartbeat and Stalled Detection

## Intent

Execute the approved Sprint 015 V2 specification from docs/sprints/SPRINT_015_REAL_TIME_DEV_EXECUTION_ACTIVITY_AND_CHECKLIST.md in zsambokia/ai-bridge. Continue from the existing preserved worktree changes from Sprint 015 V1, but do not assume they are correct: assess, reuse, repair, and validate them against V2. Implement near-real-time canonical execution activity, derived checklist projection, Django admin visibility, MCP/ChatGPT projection, console output, repair visibility, and Execution Heartbeat plus Stalled Detection derived exclusively from canonical progress events and run timestamps. Also implement the Product Owner scope-amendment UX as part of this Sprint: when a running governed execution receives a requested scope-changing addition, AI Bridge must present a concise approval prompt containing the proposed additions and a single Product Owner approval action, then use the existing governance flow to create a new proposal version and a fresh hash-bound Execution Contract. The provider must never self-approve or self-issue a contract. The UX may hide hashes and contract identifiers under technical details, but all governance artifacts must remain durable and auditable. Use no employee system, no fictional actors, no meeting threads, no parallel lifecycle, no fake progress, no fake blocker, and no fake failure. Produce evidence only after the fresh V2 contract is issued and all V2 acceptance criteria pass.

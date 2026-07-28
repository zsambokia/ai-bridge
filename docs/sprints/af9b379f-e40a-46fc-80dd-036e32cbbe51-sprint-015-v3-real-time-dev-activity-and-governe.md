---
approval_reference: conversation-confirmation:v1:574e7334d30f57ac6ef4b36b1ff4bc6ce25e84e573bcfc9f0ba288cdba425182
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: 85c74011b84fef44c9fbffba0c5bf2fbe78606583bb23119bc1b7410bcdc9bab
created_at: '2026-07-28T07:41:15.577924+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:af9b379f-e40a-46fc-80dd-036e32cbbe51
intent: Execute GitHub-issued Sprint 015 V3 exactly from commit 7f19fd78d1f2cf5db7f34edb67ad51c65c812c49
  and docs/sprints/SPRINT_015_REAL_TIME_DEV_EXECUTION_ACTIVITY_AND_CHECKLIST.md. This
  supersedes Sprint 015 V1/V2 authority. Preserve the current worktree and safely
  synchronize main only without reset, clean, or destructive checkout. Assess and
  classify existing V1/V2 work before reuse. Deliver real-time DEV execution activity
  and compact checklist using only canonical persisted execution events and timestamps;
  derived heartbeat/stalled semantics; read-only admin/MCP/console projections; repairable
  provider/MCP/console error states; governed scope-amendment approval UX; and a provider-independent,
  no-placeholder, idempotent end-to-end AI Bridge Product Owner-to-Codex handoff package.
  The handoff must provide real project_id, repository, sprint path, scope id, reviewed
  proposal version/hash, PO approval ref, contract id/hash, execution token, baseline
  SHA, branch, gates, evidence root/artifacts, execution status, and copyable Codex
  prompt. The provider must never create governance authority. Add V3 tests, run all
  resolved gates, generate evidence only under the V3 contract root, update docs/AKB,
  and commit only after all gates pass.
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
proposal_hash: f7113cb5272a2a0bb79a147afc8b68e32471db36e37d9a43d5a04e3e9c0de06c
proposal_version: 1
risk_modifiers:
- EXTERNAL_INTEGRATION
- PUBLIC_API_OR_PROTOCOL
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: SELF_DEVELOPMENT
title: Sprint 015 V3 - Real-Time DEV Activity and Governed Codex Handoff
updated_at: '2026-07-28T07:41:29.074700+00:00'
work_type: SELF_DEVELOPMENT
---

# Sprint 015 V3 - Real-Time DEV Activity and Governed Codex Handoff

## Intent

Execute GitHub-issued Sprint 015 V3 exactly from commit 7f19fd78d1f2cf5db7f34edb67ad51c65c812c49 and docs/sprints/SPRINT_015_REAL_TIME_DEV_EXECUTION_ACTIVITY_AND_CHECKLIST.md. This supersedes Sprint 015 V1/V2 authority. Preserve the current worktree and safely synchronize main only without reset, clean, or destructive checkout. Assess and classify existing V1/V2 work before reuse. Deliver real-time DEV execution activity and compact checklist using only canonical persisted execution events and timestamps; derived heartbeat/stalled semantics; read-only admin/MCP/console projections; repairable provider/MCP/console error states; governed scope-amendment approval UX; and a provider-independent, no-placeholder, idempotent end-to-end AI Bridge Product Owner-to-Codex handoff package. The handoff must provide real project_id, repository, sprint path, scope id, reviewed proposal version/hash, PO approval ref, contract id/hash, execution token, baseline SHA, branch, gates, evidence root/artifacts, execution status, and copyable Codex prompt. The provider must never create governance authority. Add V3 tests, run all resolved gates, generate evidence only under the V3 contract root, update docs/AKB, and commit only after all gates pass.

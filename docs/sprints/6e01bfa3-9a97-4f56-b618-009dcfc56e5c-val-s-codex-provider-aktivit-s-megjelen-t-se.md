---
approval_reference: conversation-confirmation:v1:8f29edb7d35ea4de69328c0a6e4c9d39aed29ed22faa59bb68a14b5b40d2d5a6
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: f37e4441aa7276003858a8c683e810d8d293eddc07a8657a7cce3b4e3afa0a44
created_at: '2026-07-29T09:21:35.995652+02:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: SPRINT
identifier: bridge:ai-bridge:sprint:6e01bfa3-9a97-4f56-b618-009dcfc56e5c
intent: 'Javítsd az AI Bridge Codex eseményláncát a subprocess stdout/stderr olvasásától
  a strukturált event parsingen, provider adapteren, persistence-en, worker logon,
  execution event API-n és admin/UI megjelenítésen át. Derítsd ki, hol veszik el a
  tényleges Codex-tartalom, majd biztosíts konkrét, redaktált, tartós, sorrendhelyes
  és idempotens eseményeket, valamint három külön nézetet: Activity, Provider Output
  és Raw Events. A végén futtasd a teljes gate-et, készíts evidence-et, commitolj
  és pusholj.'
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
  - machine-results
  - migration-plan
  - migration-validation
  - security-review
  - security-validation
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: sprint-feature
  review_requirements:
  - compatibility-validation
  - migration-plan
  - migration-validation
  - security-review
  - security-validation
project_id: ai-bridge
proposal_hash: 80a551e7ece8d79cfcb3ae3ecf8151b44f9e480db0ea67ea38578ae8bf3eecfb
proposal_version: 1
risk_modifiers:
- DATA_OR_SCHEMA_MIGRATION
- PUBLIC_API_OR_PROTOCOL
- SECURITY_RELEVANT
schema: ai-bridge-sprint/v1
schema_version: '1'
scope_kind: SPRINT
status: APPROVED
task_type: FEATURE
title: Valós Codex provider-aktivitás megjelenítése
updated_at: '2026-07-29T09:21:51.715394+02:00'
work_type: FEATURE
---

# Valós Codex provider-aktivitás megjelenítése

## Intent

Javítsd az AI Bridge Codex eseményláncát a subprocess stdout/stderr olvasásától a strukturált event parsingen, provider adapteren, persistence-en, worker logon, execution event API-n és admin/UI megjelenítésen át. Derítsd ki, hol veszik el a tényleges Codex-tartalom, majd biztosíts konkrét, redaktált, tartós, sorrendhelyes és idempotens eseményeket, valamint három külön nézetet: Activity, Provider Output és Raw Events. A végén futtasd a teljes gate-et, készíts evidence-et, commitolj és pusholj.

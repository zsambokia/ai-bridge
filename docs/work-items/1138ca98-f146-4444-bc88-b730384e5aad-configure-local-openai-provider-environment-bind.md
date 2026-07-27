---
approval_reference: conversation-confirmation:v1:74f8bdebbcc605e108afcbefe296065f79ef21142b822db4679a0bd1643cd638
clarification_questions: []
clarification_state: READY_FOR_CONFIRMATION
content_hash: 94d7152c8a2679d1c2ed1f88f152d37da35164b3dad240fb870437da904a0984
created_at: '2026-07-27T07:54:55.746722+00:00'
created_by: AI_BRIDGE
execution_authorization: APPROVED_PROVIDER_EXECUTION
execution_level: TASK
identifier: bridge:ai-bridge:work-item:1138ca98-f146-4444-bc88-b730384e5aad
intent: 'Configure local-only .env support for the OpenAI execution provider without
  persisting credentials: ignore .env, publish a secret-free .env.example, load local
  environment values safely before Django settings, document admin activation, and
  verify the provider uses only the OPENAI_API_KEY reference.'
policy:
  child_contract_required: false
  omission_justifications: []
  profile_version: '1.0'
  required_assessment_depth: standard
  required_documentation_updates:
  - behavior
  required_evidence_artifacts:
  - acceptance-results
  - assessment
  - closure-note
  - security-review
  - security-validation
  required_release_gates:
  - repository-wide
  - sprint-specific
  resolved_profile: task-configuration
  review_requirements:
  - security-review
  - security-validation
project_id: ai-bridge
proposal_hash: 64095231ba3cb89fa3e6eafd2c666f9187ebccd7782dad6a2db62f2e219efafd
proposal_version: 1
risk_modifiers:
- SECURITY_RELEVANT
schema: ai-bridge-work-item/v1
schema_version: '1'
scope_kind: WORK_ITEM
status: APPROVED
task_type: CONFIGURATION
title: Configure local OpenAI provider environment binding
updated_at: '2026-07-27T07:55:00.986922+00:00'
work_type: CONFIGURATION
---

# Configure local OpenAI provider environment binding

## Intent

Configure local-only .env support for the OpenAI execution provider without persisting credentials: ignore .env, publish a secret-free .env.example, load local environment values safely before Django settings, document admin activation, and verify the provider uses only the OPENAI_API_KEY reference.

---
status: PROPOSED
version: 0.1.0
---

# ADR Recommendation List

Recommended identifiers start after the existing ADR-019. They are proposals,
not accepted ADRs.

| Proposed ADR | Decision to make | Why it cannot be inferred | Blocks |
| --- | --- | --- | --- |
| ADR-020 | Constitution Book authority, chapter ownership and adoption process. | Existing documents have overlapping authority/status. | Book publication. |
| ADR-021 | Scope hierarchy and tenant-ready boundary: Organization, logical Workspace, Repository, Project, actor and authorization. | Conflicts with the Bridge Constitution preamble and existing `Project` model. | Tenant-ready data and API work. |
| ADR-022 | Unified Mission Intake Port and ingress adapter contract. | Conversation-only and external ingress have different identity, authorization and idempotency needs. | API/MCP/scheduler/webhook convergence. |
| ADR-023 | First-class Execution aggregate and its relation to `ExecutionRun`, job and recovery models. | Renaming an existing attempt record risks breaking recovery semantics. | Execution migration. |
| ADR-024 | Capability declaration, discovery/resolution and provider contract. | Engine/Tool/Provider/Agent substitution requires consistent policy and evidence rules. | Capability-first routing. |
| ADR-025 | Context Package canonical schema, storage, versioning, evidence manifest and retention. | Existing `KnowledgeContextPackage` is domain-specific. | Reproducible execution context. |
| ADR-026 | Localization architecture, canonical English, locale fallback and derived-content provenance. | UI translation does not resolve prompts, personas, knowledge or normative-document governance. | Localization rollout. |
| ADR-027 | Canonical event envelope, transactional outbox/replay and compatibility policy. | Existing event models have distinct lifecycles and ownership. | Event convergence. |
| ADR-028 | Reserved terminology for logical Workspace versus physical `ExecutionWorkspace`. | The same term otherwise creates model/API ambiguity. | Scope model and documentation. |

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
| ADR-024 | Capability declaration, discovery and resolution contract. | Engine/Tool/Agent implementation substitution requires consistent policy and evidence rules. Provider resources are resolved separately by ADR-029. | Capability-first routing. |
| ADR-025 | Context Package canonical schema, storage, versioning, evidence manifest and retention. | Existing `KnowledgeContextPackage` is domain-specific. | Reproducible execution context. |
| ADR-026 | Localization architecture, canonical English, locale fallback and derived-content provenance. | UI translation does not resolve prompts, personas, knowledge or normative-document governance. | Localization rollout. |
| ADR-027 | Canonical event envelope, transactional outbox/replay and compatibility policy. | Existing event models have distinct lifecycles and ownership. | Event convergence. |
| ADR-028 | Reserved terminology for logical Workspace versus physical `ExecutionWorkspace`. | The same term otherwise creates model/API ambiguity. | Scope model and documentation. |
| ADR-029 | Provider Architecture v2.0: Provider Integration and Provider Resolver, stateless Provider definition, Provider Executor lifecycle/pool, resource limits, pre-binding selection/fallback, immutable Provider Binding, same-Provider recovery, Kernel Profile and evidence policy. Provider Gateway is implementation-only. | Current hard-coded provider path and existing gateway do not determine the authority split, Executor persistence, capacity semantics, binding or recovery policy. | Multi-provider execution and provider-bound AI Kernel migration. |
| ADR-030 | Canonical Knowledge Object identity, type catalogue, lifecycle, immutable-version and typed-relationship model. | Current entries, engineering memory and revisions have overlapping but non-identical semantics. | Knowledge Object migration. |
| ADR-031 | Knowledge Lifecycle Management event, plan, synchronization, freshness, publication and representation-consistency contract. | The existing pipeline does not determine KLM ownership or asynchronous consistency guarantees. | Knowledge lifecycle implementation. |
| ADR-032 | Knowledge Reference contract, Context Package invalidation, retention and explicit stale-consumption policy. | Current packages persist source metadata but do not provide a generalized version-bound reference or invalidation contract. | Context convergence. |
| ADR-033 | AI Kernel boundary and terminology transition: the target Execution aggregate, Kernel Managers/Registries/Objects, legacy Runtime compatibility names and controlled mapping to existing runtime records. | A repository-wide rename would otherwise conflate the target Kernel with historical Runtime, `ExecutionRun` and provider-gateway behaviour. | Article III implementation and terminology retirement. |
| ADR-034 | `ExecutionJob` compatibility decision: retain it as an implementation term, map it to an `Execution Attempt`, or retire it after an auditable migration. | Its durable queue, lease, retry and recovery semantics cannot be safely inferred from the target Execution aggregate. | Execution/attempt lifecycle, queue and recovery migration. |

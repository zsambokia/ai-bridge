# Architecture Challenge Register

**Classification:** Architecture Convergence artifact preserved in a historical
mixed Phase 2.5 record. Its current governance is [Architecture and
Implementation Convergence
Governance](../ARCHITECTURE_IMPLEMENTATION_CONVERGENCE_GOVERNANCE.md).

## Decision method

Each challenge compares constitutional target architecture with repository
evidence, records viable alternatives, and identifies the Product Owner
decision. An accepted directive is recorded as such; remaining recommendations
are not constitutional amendments.

## AC-01 -- `ExecutionJob`

| Item | Assessment |
| --- | --- |
| Constitutional target | Operational Foundation owns delivery mechanics; AI Kernel owns one first-class Execution. |
| Repository evidence | `projects/models.py` and `projects/execution.py` describe `ExecutionJob` as a durable, lease-owned queue entry for `ExecutionRun`, including retry/recovery state. |
| Finding | This is a delivery envelope, not a Mission, Provider attempt or Kernel Execution. |
| Recommendation | Remove `ExecutionJob` from the canonical model. Its valid responsibilities become the delivery state of an Operational-Foundation-owned `OperationalWorkItem`. |
| Product Owner decision | Pending. |
| ADR | ADR-034 -- Canonical work-item and execution-attempt model. |

## AC-02 -- Canonical Execution Model

| Item | Assessment |
| --- | --- |
| Constitutional target | Kernel creates and owns one first-class Execution; Engine and Provider are capability providers and Provider Binding is immutable. |
| Repository evidence | `OrkiExecution` combines intake, planning and knowledge work; `ExecutionRun` is contract-bound dispatcher state; `ExecutionJob` owns queue/lease mechanics; provider calls traverse `provider_gateway.py`. |
| Finding | The current three-object model mixes Mission intake, operational delivery and Kernel execution. |
| Recommendation | Replace the three historical concepts with one Kernel-owned Execution. Do not introduce a first-class `ExecutionAttempt` initially; invocation, retry, checkpoint and recovery facts are events/evidence unless a separate lifecycle is justified. |
| Product Owner decision | Pending. |
| ADR | ADR-034 -- Canonical work-item and execution-attempt model. |

## AC-03 -- Identity, Scope and Ownership

| Item | Assessment |
| --- | --- |
| Constitutional target | Article VI defines the only logical Scope hierarchy as `Organization -> Workspace -> Project`. Every persistent domain object has exactly one direct Scope owner. Repository and Provider are Resources, never Scope types. |
| Repository evidence | `projects/scopes.py`, `projects/contracts.py`, `projects/workspace.py` and `projects/repository_lifecycle.py` show Project-bound scopes, physical execution workspaces and repository documents/snapshots, but no canonical Organization, logical Workspace or uniform Scope owner. |
| Finding | Project binding cannot safely represent tenant/scope ownership; a physical execution workspace must not be treated as the logical Workspace Scope. |
| Alternatives rejected | Project-only scope fails tenant/workspace readiness; Repository as Scope contradicts multi-repository Projects; optional Organization/Workspace metadata cannot ensure authorization or provenance. |
| Recommendation | Adopt direct Scope ownership under `Organization -> Workspace -> Project`. Repository, Provider, AKB supporting infrastructure, credentials and physical `ExecutionWorkspace` are Scope-owned Resources. Higher Scope information is derived; no redundant ancestor ownership fields are mandated. |
| Product Owner decision | **Accepted -- Product Owner Decision Alignment (2026-08-10).** Article VI records the hierarchy, Scope/Resource distinction, Mission rule and open inheritance boundary. |
| ADR | ADR-035 -- Canonical scope, resource and inheritance architecture. |

## AC-04 -- Minimum Canonical AKB Model

| Item | Assessment |
| --- | --- |
| Constitutional target | AKB stores versioned Knowledge Objects, not documents; stable identity, immutable versions, provenance, graph relationships and Knowledge References are required. KLM is independent of Kernel execution. |
| Repository evidence | `KnowledgeEntry`, `KnowledgeRevision` and `KnowledgeContextPackage` in `projects/models.py` and `projects/knowledge*.py` are entry/document-centric. |
| Finding | The current model is migration evidence, not the canonical uniform object model. |
| Recommendation | Start with `KnowledgeObject`, immutable `KnowledgeObjectVersion`, `KnowledgeRelationship`, `KnowledgeReference` and immutable `ContextPackage`; establish the minimum KLM publication/freshness/invalidation boundary. |
| Product Owner decision | Pending. |
| ADR | ADR-036 -- Minimum canonical AKB and knowledge lifecycle model. |

## AC-05 -- Localization Model

| Item | Assessment |
| --- | --- |
| Constitutional target | Article VII requires English canonical technical identifiers and multilingual capability for eligible semantic/user-facing content, including Knowledge, Persona communication and documentation. Original Evidence preserves its language/content; translations are derived, traceable representations. |
| Repository evidence | The reviewed application models expose no platform-wide locale, localized representation, translation provenance or fallback model. |
| Finding | UI-only localization is insufficient; translating every stored object or overwriting Evidence would compromise provenance and meaning. |
| Alternatives rejected | UI-only localization fails the target; translation that replaces source Evidence is prohibited; unrelated Knowledge identities for each translation break the Knowledge identity/version model. |
| Recommendation | Approve the constitutional boundary without selecting a representation data abstraction. Preserve `Knowledge identity -> Knowledge Version -> language representations`; select BCP 47 binding, representation model, fallback and lifecycle mechanics in ADR-037. |
| Product Owner decision | **Accepted -- Product Owner Decision Alignment (2026-08-10).** Article VII records the target; ADR-037 is intentionally open only for implementation-design mechanics. |
| ADR | ADR-037 -- Localization and canonical-language model. |

## AC-06 -- `ExecutionRun` and Operational Foundation Boundary

| Item | Assessment |
| --- | --- |
| Constitutional target | AI Kernel owns Execution; Operational Foundation owns queueing, scheduling, lease, retry, recovery and delivery mechanics. |
| Repository evidence | `ExecutionRun` is dispatcher-created before `ExecutionJob`; Operational Foundation documents still include `ExecutionRun` while Kernel documents use Execution. |
| Finding | The historical name couples delivery/recovery mechanics to Kernel state. |
| Recommendation | Remove `ExecutionRun` rather than blindly renaming it. Operational Foundation owns `OperationalWorkItem` delivery state; Kernel owns Execution state and communicates through immutable contracts. |
| Product Owner decision | Pending. |
| ADR | ADR-038 -- Operational Work Item / Kernel Execution ownership boundary. |

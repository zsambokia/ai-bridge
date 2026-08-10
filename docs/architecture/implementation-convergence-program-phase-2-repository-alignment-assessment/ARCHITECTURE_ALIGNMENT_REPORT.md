# Architecture Alignment Report

## Executive result

The repository has a substantial governed-runtime foundation, but it is **partially aligned** with the approved Constitution. Its most valuable migration assets are durable `FactoryMission`, contract-bound `ExecutionRun`/`ExecutionJob`, append-only execution events, provider audit records, and immutable persisted knowledge-context packages. The principal divergence is structural: these assets are split between the historical Runtime, ORKI runtime, dispatcher, workflow engine, and Provider Gateway rather than expressed as the target AI Kernel, Operational Foundation, Provider Integration, and Knowledge Object boundaries.

| Alignment band | Components |
| --- | --- |
| Ready | Mission Domain; UI Architecture (as a human-conversation adapter) |
| Partially Ready | AI Kernel; Operational Foundation; Provider; AKB; Event; Security; API & Integration |
| Not Ready | Identity & Scope; Multi-tenancy; Localization |

## Constitutional baseline consulted

- [Architecture Constitution](../ARCHITECTURE_CONSTITUTION.md)
- [Bridge Constitution](../../constitution/BRIDGE_CONSTITUTION.md)
- [AI Kernel Architecture Constitution](../AI_KERNEL_ARCHITECTURE_CONSTITUTION.md)
- [AKB Knowledge Object & Lifecycle Constitution](../AKB_KNOWLEDGE_OBJECT_AND_LIFECYCLE_CONSTITUTION.md)
- [Operational Foundation Constitution](../OPERATIONAL_FOUNDATION_CONSTITUTION.md)
- [Provider Architecture v2](../architecture-convergence-program-sprint-1/PROVIDER_ARCHITECTURE_V2.md)
- [Terminology Convergence Matrix](../architecture-convergence-program-sprint-3-ai-kernel-architecture/TERMINOLOGY_CONVERGENCE_MATRIX.md)

## Overall migration posture

Do not perform a name-only “Runtime → Kernel” rewrite. First introduce constitutional seams beside the durable legacy records, adapt existing entry points, demonstrate dual-read/one-write or projection compatibility where required, and only then retire transitional names. The dependency map and roadmap preserve the current governed execution path while this happens.

## Evidence method

Each component report cites source paths and relevant symbols. Representative evidence includes `projects/models.py` (durable domain records), `projects/execution.py` (queue/lease/dispatcher), `projects/orki_runtime.py` (runtime lifecycle), `projects/provider_gateway.py` and `projects/providers.py` (provider boundary), `projects/knowledge*.py` (AKB), `projects/runtime_api.py`, `projects/ui_urls.py`, `projects/scopes.py`, `projects/contracts.py`, and `bridge/settings/base.py`.

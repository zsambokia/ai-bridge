# Migration Roadmap

> **Status: SUPERSEDED FOR FUTURE IMPLEMENTATION PLANNING.** This Phase 2 roadmap remains historical repository-alignment evidence. Its compatibility-first migration assumptions are superseded by the Phase 2.5 [Revised Migration Strategy](../implementation-convergence-program-phase-2-5-architecture-decision-gate/REVISED_MIGRATION_STRATEGY.md). No implementation authority is changed by this status marker.

| Wave | Outcome | Strategy | Preconditions | Key risk |
| --- | --- | --- | --- | --- |
| 0 — Decisions | Approve scope model and ExecutionJob disposition | ADRs only | Product Owner decisions | incompatible persistence assumptions |
| 1 — Constitutional seams | Mission Intake, Kernel facade, provider integration interfaces | strangler; existing path remains authoritative | Wave 0 | duplicate lifecycle ownership |
| 2 — Durable execution | map existing run/job/lease/events to Kernel objects and OF work items | compatibility projections; no destructive rename | Wave 1 | recovery and fencing regressions |
| 3 — Knowledge convergence | Knowledge Object/reference publication and KLM change planning | additive versioned model; dual-read | Wave 1 plus AKB ADRs | stale-context behaviour |
| 4 — Scope platform | organization/workspace/repository ownership and authorization | additive scope columns/relations; explicit backfill | Wave 0 | tenant isolation / data migration |
| 5 — Intake and presentation | API/MCP/scheduler converge to Mission; UI uses neutral projections | adapter migration | Waves 1, 4 | client contract breakage |
| 6 — Retirement | deprecate Runtime/Gateway transitional surfaces | strangler removal after measured adoption | all prior waves | unsupported integrations |

No wave is implementation authority. Each must be decomposed into an approved, evidence-driven Sprint with explicit compatibility, migration, recovery, and release-gate criteria.

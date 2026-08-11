---
status: HISTORICAL
owner: Architecture
supersedes: []
superseded_by: Constitution Book navigation (planned adoption)
version: 1.0.0
---

# AI Bridge Architecture Map

> **Historical architecture snapshot (2026-08-10):** Preserved unchanged as
> evidence of the pre-Constitution-Book topology. Its Runtime and Provider
> Gateway labels are historical aliases, not canonical target terminology. Use
> the Constitution Book plan, Article III, and the [Visual Constitution](diagrams/README.md)
> for current target navigation.

This is the sole technical-architecture entry point. Read it before choosing a
component, changing a boundary, or interpreting an architecture document.

## Canonical hierarchy

```text
Bridge Constitution
        │
        ▼
Architecture Constitution
        │
        ├── Runtime 2.0 Constitution ── Mission authority and target route
        ├── Operational Foundation Constitution ── delivery handoff mechanics
        ├── Engine Constitution ── domain ownership and interaction
        └── State Machine Constitution ── lifecycle ownership and events
```

| Need | Canonical document |
| --- | --- |
| Repository governance, scope, release | [Bridge Constitution](../constitution/BRIDGE_CONSTITUTION.md) |
| Architecture-wide rule or conflict | [Architecture Constitution](ARCHITECTURE_CONSTITUTION.md) |
| Mission, Runtime, Work Item, provider route | [Runtime 2.0 Constitution](../runtime/runtime_2_0_constitution.md) |
| Queue, lease, retry, execution delivery | [Operational Foundation Constitution](OPERATIONAL_FOUNDATION_CONSTITUTION.md) |
| Domain-engine responsibility | [Engine Constitution](ENGINE_CONSTITUTION.md) |
| State-machine ownership or event handoff | [State Machine Constitution](STATE_MACHINE_CONSTITUTION.md) |
| Current implementation versus target | [Architecture Evolution](ARCHITECTURE_EVOLUTION.md) |
| A recorded architectural decision | [ADR index](adr/README.md) |

## Canonical execution boundary

```text
Domain Engine
  → immutable Execution Request
  → MSM authorization
  → immutable Operational Work Item
  → Operational Foundation
  → ExecutionRun → Provider Gateway → Provider
```

No direct Engine-to-Engine or Engine-to-provider route is canonical.

## Status legend

Each architecture document has front matter whose `status` is authoritative:
`CANONICAL` is binding, `SUPPORTING` elaborates it, `TRANSITIONAL`
describes an active migration, and `HISTORICAL` preserves prior context.
See the evolution register before treating an existing component as target
compliant.

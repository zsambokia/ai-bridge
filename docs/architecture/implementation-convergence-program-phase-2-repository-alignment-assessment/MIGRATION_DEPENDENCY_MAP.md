# Migration Dependency Map

```text
Identity & Scope ADR
        │
        ├── Multi-tenancy ──┬── Security authorization
        │                  ├── API / Integration scope propagation
        │                  └── Localization ownership and fallback
        │
Mission Intake ──► AI Kernel facade ──► Provider Integration
        │                 │                     │
        │                 └── Operational Foundation adapter
        │
        └── UI Conversation adapter

AKB Knowledge Object projection ──► Context references ──► Kernel context integration
Event envelope ──────────────────────────────────────────► Evidence and telemetry convergence
```

## Ordering rules

1. Resolve scope ownership and the `ExecutionJob` / Execution Attempt ADR before changing persistent execution or authorization contracts.
2. Establish common Mission intake before routing new API, MCP, scheduler, or webhook work.
3. Introduce Kernel and Provider Integration facades around—not in place of—the current dispatcher and gateway.
4. Migrate AKB references and event envelopes before enforcing stale-context and cross-component evidence invariants.
5. Retire adapters only after production-equivalent compatibility and recovery evidence exists.

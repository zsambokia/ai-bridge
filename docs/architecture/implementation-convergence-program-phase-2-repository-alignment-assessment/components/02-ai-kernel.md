# AI Kernel Assessment

## Target Architecture

The AI Kernel owns first-class Execution and Kernel Managers, Registries, Objects, Events, Evidence, recovery, leases, scheduling, telemetry, and immutable context integration. It coordinates; it does not make Mission business decisions.

## Current Repository

`OrkiExecution` and `OrkiRuntimeEvent` in `projects/models.py`, with lifecycle functions in `projects/orki_runtime.py`, provide a provider-neutral execution lifecycle. Separately, `ExecutionRun`, `ExecutionJob`, recovery attempts, progress events, and dispatcher functions in `projects/execution.py` implement governed delivery. `projects/runtime_api.py` exposes the former as “Runtime”.

## Gap Analysis

**Partial:** durable state, events, recovery, queue, lease, and user projection exist. **Missing:** a single Kernel-owned Execution object, Kernel service categories, explicit registry contracts, neutral event envelope, and normalized context binding. **Legacy:** Runtime/ORKI names and parallel execution models.

## Migration Strategy

Introduce a Kernel facade with read projections over existing records; make it the integration boundary before any storage consolidation. Map state transitions and evidence both directions, then select a canonical persistent Execution only after AC-02/ADR-034. Breaking changes are deferred behind versioned projections.

## Risks and Dependencies

Recovery semantics, leases, and delivery evidence are safety-critical. Depends on Mission mapping, Operational Foundation adapter, Provider Integration, and AC-01/02.

## Readiness

**Partially Ready.** Strong primitives exist, but no single constitutional owner exists yet.

## Evidence

`projects/models.py` (`ExecutionRun`, `ExecutionJob`, `OrkiExecution`, `OrkiRuntimeEvent`); `projects/execution.py`; `projects/execution_recovery.py`; `projects/orki_runtime.py`; `projects/runtime_api.py`.

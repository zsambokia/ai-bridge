# Operational Foundation Assessment

## Target Architecture

Operational Foundation is independent delivery infrastructure: it accepts only MSM-authorized immutable work, owns queue/schedule/lease/retry/recovery/heartbeat and durable delivery receipts, and cannot make Mission decisions.

## Current Repository

`projects/execution.py` creates `ExecutionJob` for a contract-bound `ExecutionRun`, claims it with fencing/lease/heartbeat, and dispatches provider work. `ExecutionWorkspace`, recovery attempts, and delivery records are durable model assets.

## Gap Analysis

**Partial:** most operational mechanics already exist. **Missing:** a named work-item boundary and strict separation from dispatcher/provider invocation/Execution ownership. **Transitional:** `ExecutionRun` is used as both delivery record and execution identity.

## Migration Strategy

Wrap the queue functions behind an Operational Foundation work-item interface. Retain the current worker record and fencing semantics; route Kernel-authorized work through the adapter. Defer storage changes until Execution mapping is approved.

## Risks and Dependencies

Do not break reconciliation, idempotency, fencing, or recovery. Depends on Kernel facade and ADR-034.

## Readiness

**Partially Ready.** Delivery infrastructure is mature but boundary ownership is not yet constitutional.

## Evidence

`projects/execution.py` (`enqueue_execution`, `claim_next_job`, `heartbeat_job`); `projects/models.py` (`ExecutionJob`, `ExecutionRecoveryAttempt`, `ExecutionDelivery`, `ExecutionWorkspace`).

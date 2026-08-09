# Operational Foundation Audit

**Status: PARTIAL PASS — reusable platform exists, but is not the single operational path.**

`ExecutionJob` is a durable, lease-owned queue (`models.py:1521`); `execution.py` supplies enqueue, claim, heartbeat, retry, recovery, scheduler and worker operations. Management commands and extensive execution/recovery tests provide evidence for the platform. The targeted suite passed 44 tests.

The gap is adoption and singular ownership. Factory Chat dispatch performs provider work through `WorkflowInstance` (`orki_runtime.py:1314`) rather than creating a governed `ExecutionRun` and queuing an `ExecutionJob`. Workflow retry and the broad `OrkiExecution` lifecycle also coexist with platform lifecycle concerns. Therefore there is no proof of one queue, one polling/worker lifecycle, one recovery path, and one retry authority for all Phase 1 operational work.

Required outcome: retain `ExecutionJob` as the sole operational substrate and migrate every provider-bound work item through an `ExecutionRequest → ExecutionRun → ExecutionJob` adapter. Do not add another queue, worker, scheduler, retry or lifecycle system.


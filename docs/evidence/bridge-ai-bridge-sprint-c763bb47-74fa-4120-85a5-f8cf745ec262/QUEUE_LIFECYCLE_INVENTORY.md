# R20-00 Queue and Lifecycle Inventory

`ExecutionJob` is the only observed durable execution queue. It carries a run,
status, lease owner/expiry, heartbeat/fencing, provider-attempt metadata,
checkpoint, recovery, and reconciliation state. `projects/execution.py` exposes
enqueue, claim, heartbeat, execute-claimed-job, recovery, reconciliation, and
worker/scheduler command paths. No second queue, worker, or outbox was found.

| Lifecycle layer | Durable component | Status |
| --- | --- | --- |
| Request/start | `ExecutionStartRequest` | exists, but does not establish the required immutable request contract |
| Run | `ExecutionRun` | exists |
| Queue/lease | `ExecutionJob` | exists |
| Worker/recovery | `projects.execution`; worker/reconcile commands | exists |
| Authorized work item | none | absent |
| MSM authorization before enqueue | none | absent |
| Factory Chat use of queue | direct synchronous adapter dispatch | bypassed |

R20-02 must reuse this queue and worker. It must not introduce another queue,
lease mechanism, or provider lifecycle.

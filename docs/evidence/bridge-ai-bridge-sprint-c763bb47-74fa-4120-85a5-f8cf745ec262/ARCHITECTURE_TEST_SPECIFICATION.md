# R20-00 Architecture Test Specification

These are acceptance requirements for later approved implementation scopes;
they are not implemented in this read-only audit.

1. An Engine emits an immutable, durable request with request ID, origin, type,
   version, and idempotency key; mutation is rejected.
2. Only MSM can authorize creation of an operational work item; no conversation,
   PSM, WSM, Engine, or provider adapter can create one directly.
3. A work item cannot enqueue a run before mission state is authorized; planning
   cannot begin before durable `MISSION_READY_FOR_PLANNING`.
4. Every work item maps to one existing `ExecutionRun`/`ExecutionJob` lifecycle;
   duplicate queue/worker creation is rejected.
5. Factory Chat's route reaches the provider only through the Provider Gateway
   after Foundation claim/lease evidence exists.
6. Static forbidden-edge checks reject Conversation/Runtime/WSM direct provider
   calls and direct `execute_task_adapter` provider lambdas.
7. Recovery/replay preserves request, mission authorization, run, job, fence,
   provider-attempt, and evidence provenance.

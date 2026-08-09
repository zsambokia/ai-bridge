# Phase 1 / Sprint 1 — Operational acceptance

## Intended runtime

Local Django Runtime/Factory Chat execution on `main`, using the existing
provider adapter configuration. Sprint 1 does not introduce a daemon, worker
process, external scheduler, or infrastructure dependency.

## Migration and recovery readiness

- Migration `projects.0067_operationalworkitem_operationalworkevent` creates the
  Foundation-owned work and event records.
- The Foundation retry state is durable and evented; a future worker can claim
  the already-queued work-item contract.
- Existing `ExecutionRun`/`ExecutionJob` recovery remains unchanged and is not
  claimed by the new Factory Chat path.

## Runtime smoke

The `test_factory_chat_runtime_integration` scenarios execute the actual Runtime
dispatch boundary with a deterministic provider adapter mock. The tests prove a
work item is created, the provider response returns through the Gateway, and
the normal Runtime mission flow reaches its expected waiting/planning outcome.

See `VALIDATION.md` for the executed command and result.

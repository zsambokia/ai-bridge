# Phase 1 / Sprint 1 — Migration evidence

## Changed boundary

Before Sprint 1, `dispatch_factory_chat_execution` delegated to a Workflow
helper that imported provider implementations and synchronously invoked the
selected model.

After Sprint 1:

1. Runtime creates an `OperationalWorkItem` with mission, correlation, payload,
   context reference, retry policy and evidence fields.
2. Workflow records only its WSM task transition and task evidence.
3. The Operational Foundation moves the work item through `CREATED → QUEUED →
   RUNNING → COMPLETED`; failures become `FAILED → RETRY` when policy permits.
4. Only `provider_gateway.py` imports the provider implementation and invokes a
   model.
5. Runtime consumes the resulting evidence and continues its existing
   observation, planning and approval flow.

## Preserved compatibility

Factory Chat remains synchronous at this migration seam, but it now uses the
durable Foundation work-item contract. A future worker/scheduler can consume
the same contract without reintroducing a Workflow queue or provider call.

## Regression proof

- `projects.tests.test_operational_foundation`: common lifecycle, retry evidence
  and prohibited direct Runtime/Workflow provider imports.
- `projects.tests.test_factory_chat_runtime_integration`: Factory Chat behavior
  through the migrated route.
- `projects.tests.test_orki_runtime_mission_e2e`: mission/OESM behavior remains
  intact.

The concrete command outcomes are recorded in `VALIDATION.md`.

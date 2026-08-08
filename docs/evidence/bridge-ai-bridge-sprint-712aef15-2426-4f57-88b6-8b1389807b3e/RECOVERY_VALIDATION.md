# Recovery validation

Runtime recovery is bounded coordination: it appends `RECOVERY_REQUESTED`; only `WAITING_EXTERNAL` is reassessed to `PLANNING` with `RECOVERY_REASSESSMENT_STARTED`. It does not resume a worker, lease a job or mutate `ExecutionRun` recovery.

`test_recovery_reassesses_external_wait_only` passed and proves the persisted transition and audit event.

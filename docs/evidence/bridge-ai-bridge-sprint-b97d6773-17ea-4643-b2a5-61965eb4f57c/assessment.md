# Assessment

## Root cause

`start_run` detects active runs by project and branch, not by the requesting
contract. On `CONFLICTING_ACTIVE_EXECUTION`, orchestration recovery looked only
for a run belonging to the new contract. Because the active run belonged to a
different contract, that lookup was empty and `scope.orchestration_status`
reported a resumable block without the token required by `execution.cancel`.

## Repair decision

The orchestration keeps its `run` relation empty and records the separately
owned active run's UUID and lifecycle in the failure detail. The public status
projection promotes those two values for a caller that needs to act. This
preserves ownership and delegates cancellation to the existing contract-bound
authorization path.

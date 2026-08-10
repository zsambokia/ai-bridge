# R20-00 State Ownership Matrix

| Required state / authority | Evidence | Owner now | Verdict |
| --- | --- | --- | --- |
| Immutable, durable Execution Request with identity, origin, type, version, idempotency | `projects/decision_contract/framework.py` `ExecutionRequest` is frozen but has no durable model/identity; `ExecutionStartRequest` is durable but start-oriented | split | GAP |
| Mission state and mission-only work authorization | `FactoryMission`; no `MissionStateMachine`, `MISSION_READY_FOR_PLANNING`, or MSM transition set found | mixed Factory Mission / runtime dispatch | GAP |
| Authorized Operational Work Item | no `OperationalWorkItem` model; `test_operational_foundation.py` explicitly forbids the class | absent | GAP |
| Execution run mechanics | `ExecutionRun` model and `projects/execution.py` | Operational Foundation candidate | PARTIAL |
| Queue, lease, heartbeat, retry, recovery | `ExecutionJob`, `enqueue_run`, `claim_next_job`, heartbeat/reconcile worker functions | Operational Foundation candidate | PARTIAL |
| Provider boundary | `invoke_factory_chat_model` invoked from a Workflow adapter lambda | Factory Chat / runtime compatibility path | FAIL |
| Plan lifecycle | `FactoryPlan`, `OrkiExecution` paths; no durable `MISSION_READY_FOR_PLANNING` gate | historical/Orki runtime | GAP |

`PARTIAL` means a reusable component exists but is not connected under the
constitutional authority route. It is not a compliance claim.

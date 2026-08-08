# Orki Runtime Mission E2E Validation

## Authority and boundary

This is the Product Owner-authorized **Factory Development Mode** acceptance Sprint for the Orki Runtime Foundation. It validates the approved Runtime architecture without changing Governance, approval ownership, queueing, `ExecutionRun`, `ExecutionJob`, or Cognitive State ownership.

The canonical executable proof is `projects.tests.test_orki_runtime_mission_e2e`. It is mandatory whenever Runtime, Planning, Goal, Plan, OESM, or their state graph changes.

## Mission timeline

| Step | Runtime-owned outcome | Evidence |
| --- | --- | --- |
| Knowledge | Cognitive `FACT` is recorded | `COGNITIVE_CONTEXT_REFERENCED` references only its ID |
| Reasoning | Cognitive `OPERATIONAL_REASONING` is recorded | provenance links it to knowledge |
| Planning | Cognitive `PLAN`, FactoryPlan and OrkiPlan are selected | plan references, no copied content |
| Approval | Existing `approve_plan` creates canonical approval | `APPROVAL_OBSERVED` |
| Waiting | Runtime enters `WAITING_FOR_USER`; pause/resume preserves it | `USER_INPUT_REQUESTED`, `PAUSED`, `RESUMED` |
| Execution | Runtime calls a real isolated operation that writes and reads `README.md` | `EXECUTION_OPERATION_STARTED` / `COMPLETED` |
| Closure | OESM succeeds; Plan is completed and Goal is achieved | `GOAL_ACHIEVED`, derived progress 100 |

## Recovery, retry, and cancellation

The second mission intentionally raises two real exceptions. Each attempt becomes `WAITING_EXTERNAL`; the first wait is paused/resumed, then `recover_execution` returns to `PLANNING`. The third invocation writes and verifies a real README and reaches `SUCCEEDED`. A separate approved execution is cancelled exclusively through `cancel_execution`, producing `EXECUTION_CANCELLED` and `GOAL_CANCELLED`.

## State-transition timeline

```text
CREATED -> PLANNING -> WAITING_APPROVAL -> WAITING_GOVERNANCE
-> DISPATCHING -> RUNNING -> WAITING_FOR_USER -> PAUSED
-> WAITING_FOR_USER -> RUNNING -> SUCCEEDED

RUNNING -> WAITING_EXTERNAL -> PAUSED -> WAITING_EXTERNAL
-> PLANNING -> DISPATCHING -> RUNNING -> WAITING_EXTERNAL
-> PLANNING -> DISPATCHING -> RUNNING -> SUCCEEDED

WAITING_GOVERNANCE -> CANCELLED
```

All transitions are emitted by OESM services. The test does not assign Runtime state, goal completion, progress, or events.

## Release-gate evidence

| Gate | Result |
| --- | --- |
| Actual business outcome | PASS: isolated `README.md` is written, read and exact-content verified |
| Goal completion | PASS: OrkiPlan `COMPLETED`, OrkiGoal `ACHIEVED`, execution `SUCCEEDED` |
| Event evidence | PASS: strictly monotonic event sequence; every event has evidence references |
| Approval and Shadow Mode | PASS: existing approval is observed; `execution_run_id` remains null |
| Recovery and retry | PASS: two induced failures, recovery reassessment and third-attempt success |
| Waiting / pause / resume | PASS: `WAITING_FOR_USER` and paused restoration are persisted |
| Cancellation | PASS: cancellation is an OESM transition with goal cancellation event |
| Migration rollback | PASS: migration test targets the full 0056 state |

## Lessons applied

The first E2E run exposed two missing integration details: user waiting had to cause a Runtime dispatch before entering `WAITING_FOR_USER`, and repeated Factory test missions needed distinct planning titles because the existing Knowledge candidate has a uniqueness constraint. Both fixes are covered by the canonical test and did not alter canonical ownership boundaries.

# R20-00 Architecture and Call Map

## Constitutional target

```text
Domain Engine -> immutable Execution Request -> MSM
-> authorized Operational Work Item -> Operational Foundation
-> ExecutionRun -> Provider Gateway -> Provider
```

## Observed Factory Chat route

```text
Factory Chat -> factory_missions.receive_conversation_event
-> start_factory_chat_execution -> orki_runtime.dispatch_factory_chat_execution
-> workflow_engine.execute_task_adapter
-> lambda: factory_chat.invoke_factory_chat_model -> Provider
```

This is a prohibited bypass: the route has no durable immutable request, MSM
authorization, authorized work-item boundary, or `ExecutionJob` enqueue/claim
before provider invocation.

## Existing components and ownership

| Component | Observed role | Constitution classification |
| --- | --- | --- |
| `ExecutionRequest` (`decision_contract/framework.py`) | frozen in-memory decision projection | partial; not durable, request-identified, or MSM-authorized |
| `ExecutionStartRequest` | durable authorization/start record | reusable supporting record; not the canonical request/work item |
| `ExecutionRun` | durable execution/evidence projection | reusable Operational Foundation run mechanic |
| `ExecutionJob` + `execution.py` | sole lease, retry, heartbeat, recovery queue | reusable Operational Foundation mechanic, bypassed by Factory Chat |
| `FactoryMission` / `factory_missions.py` | conversation/mission-oriented state and dispatch | partial ingress; not a dedicated MSM |
| `workflow_engine.py` | workflow/task retry and synchronous adapter execution | WSM-domain implementation with forbidden provider path |
| `OrkiExecution` | Orki runtime lifecycle projection | separate historical/runtime projection; not an Operational Work Item |

The target does not justify a second queue, worker, or lifecycle. The existing
`ExecutionRun` and `ExecutionJob` foundation is the candidate mechanics layer;
the R20-01/R20-02 design must determine the single authorized work-item mapping
and migrate ingress to it.

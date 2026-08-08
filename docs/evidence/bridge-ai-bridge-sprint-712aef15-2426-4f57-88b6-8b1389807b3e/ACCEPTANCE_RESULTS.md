# Acceptance results

| Definition of Done | Result |
| --- | --- |
| Goal model | PASS — `OrkiGoal` records Runtime intent and can reference, not copy, Cognitive State |
| Plan model | PASS — versioned `OrkiPlan` is attached to a Runtime Goal and existing Factory Plan |
| Runtime/OESM | PASS — `OrkiExecution` persists state, state version, waits and pause origin; coordinator enforces transitions |
| Runtime event stream | PASS — ordered append-only `OrkiRuntimeEvent` captures actor, payload and evidence references |
| Factory Chat via Runtime | PASS — Factory planning uses the Shadow Mode adapter |
| Shadow Mode | PASS — approval is observed and handoff recorded without a contract, ExecutionRun, job, queue or provider call |
| Evidence compatibility | PASS — existing scope and approval identifiers are retained as event evidence references |
| Governance and ExecutionRun unchanged | PASS — no modification to their models, lifecycle services, or API ownership |
| Cognitive State unchanged | PASS — Runtime holds only optional reference foreign keys |

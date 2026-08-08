# Shadow Mode comparison

| Concern | Existing Factory flow | Runtime Foundation Shadow Mode |
| --- | --- | --- |
| Plan ownership | `FactoryPlan` and its existing scope/approval flow | unchanged; Runtime references the Factory Plan |
| Cognitive State | existing knowledge owner | not copied; optional reference fields only |
| Approval | existing `GovernanceApproval` | observed after the existing approval succeeds |
| ExecutionRun / jobs / provider | existing owner and lifecycle | no object, queue item or provider call is created |
| Runtime result | none | persisted Goal, Plan, Execution and audit event stream |
| Handoff | normal legacy flow remains available | recorded as `shadow_only`, never dispatched |

The focused Factory Chat and Runtime test suite verifies that a Factory Chat plan
creates an `OrkiExecution` in `SHADOW` mode and leaves `execution_run_id` empty
before and after approval.

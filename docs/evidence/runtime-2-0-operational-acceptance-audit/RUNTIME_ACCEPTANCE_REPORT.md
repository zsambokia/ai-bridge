# Runtime 2.0 Operational Acceptance Report

**Overall status: FAIL — not ready for Product Owner acceptance.**

The repository has real, tested components, but they have not converged into the required Runtime 2.0 operating model. The decisive counterexample is the live Factory Chat path:

```text
Conversation HTTP → Factory Missions → Orki Runtime → Workflow adapter → Provider Gateway → provider
```

`factory_missions.py:11-16,101-110` imports and synchronously calls Runtime entry points; `orki_runtime.py:1314-1324` invokes `execute_task_adapter` and the provider gateway. It does not create an `ExecutionRequest → ExecutionRun → ExecutionJob` path. The Runtime source itself records that this migration is still required before Phase 1 can pass.

| Area | Result | Evidence |
| --- | --- | --- |
| Operational Foundation | PARTIAL | Durable `ExecutionJob` queue/lease/recovery exists (`models.py:1521`, `execution.py`), but Chat bypasses it. |
| Mission Resolution / MSM | FAIL | `FactoryMission` exists, but no isolated MSM/resolution sequence; it calls Runtime directly. |
| Planning Engine / PSM | FAIL | `planning_engine.py` stores a cognitive artefact only; no planning session/PSM/question loop. |
| Workflow / WSM | PARTIAL | Explicit WSM exists (`workflow_engine.py:38-63`), but Runtime invokes its steps. |
| Conversation Layer | FAIL | UI delegates correctly in places, but it starts authority-bearing paths and contains workspace actions. |
| AKB / Repository / Semantic | PARTIAL | Bootstrap-to-AKB-to-index chain exists; Planning does not consume it as mandatory mission resolution. |

No Sprint may be accepted separately. The only coherent acceptance condition is **Sprint 1 PASS AND Sprint 2 PASS AND Overall Runtime 2.0 PASS**; this repository is currently FAIL.


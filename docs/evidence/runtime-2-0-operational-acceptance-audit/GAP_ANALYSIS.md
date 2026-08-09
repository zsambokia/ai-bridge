# Prioritized Gap Analysis

| Priority | Missing capability | Current state | Root cause | Proposed Sprint |
| --- | --- | --- | --- | --- |
| P0 | One canonical end-to-end runtime route | Chat directly dispatches Runtime → WSM → Gateway | Legacy Orki Runtime is the integration hub | Convergence baseline |
| P0 | Isolated MSM and Mission Resolution Layer | `FactoryMission` delegates to Runtime | No mission command/event boundary or evidence-source sequence | Sprint 2 architecture |
| P0 | Independent PSM | Planning states live in `OrkiExecution` | Planning Engine only persists cognitive plans | Sprint 2 planning |
| P0 | Conversation presentation-only boundary | UI/mission services can start dispatch and repository actions | HTTP ingress is coupled to Runtime services | Sprint 2 conversation |
| P0 | Runtime-free WSM execution | Runtime calls `execute_task_adapter` | Workflow is used as an in-process provider adapter | Sprint 1 convergence |
| P1 | Single operational lifecycle adoption | `ExecutionJob` exists but chat bypasses it | Platform migration incomplete | Sprint 1 convergence |
| P1 | Mandatory AKB/repository/semantic resolution | Components exist but are not Planning inputs | Missing orchestration policy in MSM/PSM | Sprint 2 planning |
| P1 | Explicit behaviour/decision layer | Behaviour resides in prompt text | No provider-independent decision model | Sprint 2 experience |
| P1 | Acceptance scenario suite | 44 targeted tests pass; no 20-scenario planning proof | Tests verify components, not acceptance journeys | Acceptance hardening |


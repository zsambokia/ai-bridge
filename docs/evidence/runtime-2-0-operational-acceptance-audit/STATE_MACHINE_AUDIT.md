# State Machine Audit

**Status: FAIL — state ownership overlaps.**

`OrkiExecution` has a broad transition table spanning understanding, semantic search, gap analysis, question generation, user wait, planning, approval/governance, dispatch/running, verification/reflection, knowledge integration, retry and recovery (`orki_runtime.py:59-181`). This is not a narrowly operational runtime state machine.

`FactoryMission` additionally holds delivery phases (`models.py:627`), while `WorkflowInstance` has WSM state (`models.py:2174`; `workflow_engine.py:38-63`), and `ExecutionJob` owns queue lifecycle (`models.py:1521`). These state stores overlap in responsibility and are connected by direct synchronous calls.

Target ownership:

```text
Conversation (events/projections only)
  → MSM (mission resolution, work-item decisions)
  → Operational Work Item / ExecutionRequest
  → ExecutionRun / ExecutionJob
  → Planning PSM or Workflow WSM
  → Provider Gateway
```

No provider may modify mission state, no engine may call another engine as an execution shortcut, and each state transition needs one owner plus an event/projection boundary.


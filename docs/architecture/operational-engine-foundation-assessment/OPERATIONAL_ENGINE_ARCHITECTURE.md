---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Operational Engine Foundation — target architecture

## Decision

The existing Orki Runtime remains the authoritative **mission lifecycle coordinator**. It must not become the implementation home for planning, workflow execution, knowledge retrieval, reflection, repository work, or provider invocation. Those concerns are independently deployable and recoverable Operational Engines which operate on durable state and evidence.

This is an incremental target architecture. It does not replace the current Runtime Foundation and does not change its present behaviour.

## Target shape

```text
Conversation Layer -> Runtime Foundation -> durable mission state
                                      |             |
                                      v             v
                         Operational Engine Queue   Evidence / State Store
                                      |
          +---------------------------+---------------------------+
          | Planning | Workflow | Knowledge | Repository | Reflection |
          +---------------------------+---------------------------+
                                      |
                               Provider Gateway
```

The Runtime creates intent, applies governance transitions, publishes work, and projects status. An engine consumes one bounded work item, persists its own progress and evidence, publishes a state/event result, then becomes idle. An engine never synchronously calls another engine.

## Engine catalogue

| Engine | Purpose | Input | Output / evidence | State owner |
| --- | --- | --- | --- | --- |
| Planning | turn a mission into an approval-ready plan only after gaps close | mission, context package, knowledge, repository facts | understanding, questions, plan package | Planning Session |
| Workflow | select and progress an approved execution workflow | approved plan, workflow template, tasks | workflow/task events and completion receipt | Workflow Instance / Task |
| Knowledge | retrieve, index and qualify knowledge | retrieval/index request | ranked, attributable knowledge receipt | Knowledge Pipeline Run |
| Repository | bootstrap, inspect, index and report repository facts | repository request | repository snapshot/index receipt | Repository Lifecycle Run |
| Reflection | evaluate a finished result and produce learning candidates | execution and evidence | reflection receipt, learning proposal | Reflection Run |
| Learning | promote approved learning into governed knowledge | approved reflection | knowledge promotion evidence | Learning Promotion |
| Deployment | execute an approved release workflow through governed ports | approved release task | release evidence | Deployment Workflow |
| Documentation | generate or synchronize approved documentation tasks | approved documentation task | document/evidence receipt | Documentation Workflow |

## Runtime responsibilities retained

The Runtime alone remains responsible for mission identity and lifecycle, authorization and approval gates, contract binding, canonical project state, ExecutionRun/ExecutionJob governance, operator-visible runtime projections, and safe terminal-state reconciliation. It may request engine work but does not own an engine's internal state machine.

## Current-state evidence

`projects/orki_runtime.py` already owns mission-state transitions, cognitive state publication, approvals and `ExecutionRun` coordination. The existing `projects/workflow_engine.py` proves durable workflow, step and task records are feasible, but currently also contains a chat-provider adapter. That is a transitional implementation seam, not the target provider boundary.

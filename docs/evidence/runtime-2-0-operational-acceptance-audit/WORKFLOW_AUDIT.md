# Workflow Engine Audit

**Status: PARTIAL PASS.**

The Workflow Engine is comparatively well bounded in isolation: `workflow_engine.py` defines an explicit WSM transition map (`:38-63`), creates workflow/step/task records and owns task retry. Its module contract says it must not import Runtime or transition mission state.

The required separation fails at the caller boundary. `orki_runtime.py` imports `execute_task_adapter` and calls it for Factory Chat work (`:50,1314`). Therefore Runtime directly executes a Workflow step rather than creating a work item for an independently scheduled Workflow Engine. `WorkflowInstance` also links to `OrkiExecution` (`models.py:2174`), reinforcing shared lifecycle coupling.

Acceptance requires WSM ownership of workflow steps/tasks only, execution via the operational foundation, and no Runtime → Workflow direct execution call.


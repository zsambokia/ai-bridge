# Operational Acceptance — Workflow Engine Foundation & Task Model

## Acceptance mapping

| Sprint criterion | Evidence |
| --- | --- |
| Runtime and Engine are separate ownership contexts | `workflow_engine.py` has no `orki_runtime` import; Runtime calls Engine adapters only. |
| WSM and first-class Task are durable | Migration 0066 and model assertions in `test_orki_runtime_mission_e2e.py`. |
| Existing Runtime route remains operational through an adapter | Factory chat, shadow execution and structured decision target tests; full suite PASS. |
| Retry and recovery are Engine-owned | Mission recovery test verifies two failed retries then successful completion and emitted Task evidence. |
| Workflow can sequence more than one Task | `test_workflow_engine_can_sequence_multiple_tasks_before_completion`. |
| Reflection produces a learning candidate, not an active template | Successful mission test verifies `WorkflowCandidate.GENERATED`; selection test excludes `CANDIDATE`. |
| Only approved templates can be selected | `test_unapproved_workflow_template_is_never_selected`. |

## Canonical flow demonstrated

`Mission/OESM → WorkflowInstance → WorkflowStep → Task → Runtime reflection → WorkflowCandidate`

`ExecutionRun` remains an optional foreign-key association on `Task` for
existing governed execution records. It is intentionally not a new workflow
record and the Engine does not alter its provider, governance or queue
lifecycle.

## Exclusions honored

- No HTTP/gRPC Workflow Service Interface.
- No change to ExecutionRun, provider registry, approvals, governance or queue
  ownership.
- No automatic promotion of generated candidates to templates.

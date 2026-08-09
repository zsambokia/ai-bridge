# Workflow Engine Foundation & Task Model — Execution Record

Date: 2026-08-09
Execution profile: Product Owner-authorized Factory Development Mode
Branch: `main`
Baseline: `bf6f886bb5a08187eafb9cccd02b662ff9856f66`

## Authorized scope

Implement the Workflow Engine bounded context and first-class Task model for
AI Bridge. The Engine owns workflow selection, workflow-state-machine (WSM),
steps, task lifecycle, retry evidence and adapter dispatch. Orki Runtime keeps
mission/OESM, planning, verification, reflection and knowledge ownership.

No Workflow Service Interface, provider/governance/approval/queue rewrite, or
unapproved-template activation is included.

## Delivered work

- Added durable `WorkflowTemplate`, `WorkflowInstance`, `WorkflowStep`, `Task`,
  `WorkflowEvent`, `WorkflowSelectionRecord` and `WorkflowCandidate` records.
- Added migration `0066_workflowinstance_workflowcandidate_workflowstep_task_and_more`.
- Added `projects.workflow_engine`, including WSM transitions, append-only
  Engine events, task retry handling, approved-template selection evidence and
  provider/tool adapter dispatch.
- Routed the existing Runtime shadow, structured-decision and factory-chat
  paths through Engine Tasks without changing their public Runtime contract.
- Linked Runtime reflection to a generated workflow candidate; generated and
  unapproved candidates remain ineligible for template selection.
- Added Mission → Workflow → Step → Task → Reflection → Candidate integration
  assertions, retry/recovery coverage, multiple sequential task coverage and
  unapproved-template exclusion coverage.

## Boundary decisions

- A `Task` may reference an existing `ExecutionRun`, but does not create or
  replace it. The existing Factory chat Runtime path has no `ExecutionRun`, so
  its Task correctly retains a null reference.
- Engine retry is bounded by `Task.max_retries` (default 2), recorded on the
  Task and in an append-only `WorkflowEvent` before Runtime recovery is
  surfaced.
- Vector retrieval produces selection evidence and only an `APPROVED`
  `WorkflowTemplate` is eligible for use. A generated `WorkflowCandidate`
  cannot be selected or activated.

## Modified Sprint artifacts

- `projects/models.py`
- `projects/migrations/0066_workflowinstance_workflowcandidate_workflowstep_task_and_more.py`
- `projects/workflow_engine.py`
- `projects/orki_runtime.py`
- `projects/tests/test_orki_runtime_mission_e2e.py`
- `docs/architecture/CANONICAL_WORKFLOW_ENGINE_ARCHITECTURE.md`
- `docs/architecture/WORKFLOW_ENGINE_INTEGRATION_PLAN.md`
- this evidence directory

Unrelated pre-existing worktree changes were preserved.

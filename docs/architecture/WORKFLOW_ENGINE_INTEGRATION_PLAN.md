# Workflow Engine Integration Plan

## Scope and guardrails

This is a staged refactor plan proposed by the Architecture Assessment Sprint.  It
does not authorize implementation.  It preserves the Runtime Foundation and all
approved governance/provider/knowledge boundaries.  Every phase must use the normal
approved scope, contract and Release Gates before mutation.

## Incremental migration plan

| Phase | Change | Files/APIs principally affected | Compatibility and proof |
| --- | --- | --- | --- |
| 0 — characterization | Freeze current behavior with focused tests and event snapshots | `projects/tests/test_orki_runtime_mission_e2e.py`, `test_factory_acceptance_suite.py`, Factory Chat tests | Existing no-mock real-file and temporary-git E2Es remain the baseline. |
| 1 — contracts | Introduce `projects/workflows/` domain interfaces, schemas and typed event/result contracts; no caller swap | New module and contract tests only | No database or API behavior change. |
| 2 — persistence | Add versioned templates, instances, step runs and engine events with migrations | `projects/models.py`, new migration, admin/API serializers as separately approved | Runtime foreign-key/reference is additive; old executions continue unchanged. |
| 3 — shadow adapter | Implement `CallableExecutor` and make the current shadow operation pass through an engine instance | `projects/orki_runtime.py`, new engine service, mission E2Es | Preserve function signature initially; assert Runtime receives engine events, not a direct callable result. |
| 4 — mission projection | Add Runtime-to-engine start adapter and engine-to-Runtime summary projection | Runtime service/API, event tests | OESM remains mission owner; no step state copied into `OrkiExecution`. |
| 5 — provider migration | Replace Factory Chat direct provider call with an AI-step executor; delegate governed delivery to existing `ExecutionRun`/`ExecutionJob` | `dispatch_factory_chat_execution`, provider/Factory Chat tests | Correlation IDs, retry responses and user-visible waits stay compatible. |
| 6 — retrieval/templates | Add approved workflow template indexing and selection record; turn `required_workflows` into evidence-addressable selected versions | semantic/knowledge integration, tests | Existing semantic vector store and Knowledge Pipeline are reused, not forked. |
| 7 — learning | Submit workflow candidates after reflection through review/promotion | candidate validation/pipeline, governance tests | Never auto-activate or embed unreviewed candidates. |
| 8 — deprecation | Remove direct Runtime callable/provider execution only after parity evidence and migration window | Runtime adapters and docs | Keep a compatibility adapter until all supported callers migrated; remove via explicit approved scope. |

## API direction

Runtime receives a narrow port, not an Engine implementation detail:

```text
start_workflow(mission_ref, selection, inputs, correlation_id) -> WorkflowInstanceRef
get_workflow_summary(instance_ref) -> WorkflowSummary
resume_workflow(instance_ref, input_reference) -> WorkflowSummary
cancel_workflow(instance_ref, reason) -> WorkflowSummary
```

The Engine emits typed summaries (`INSTANCE_STARTED`, `STEP_WAITING_HUMAN`,
`PROGRESS_CHANGED`, `INSTANCE_FAILED`, `INSTANCE_COMPLETED`) with event/evidence
references.  Runtime projects them to its existing event stream and public progress
shape.  It must not infer a step transition from a provider response.

## Test strategy and retained E2Es

| Existing asset | Retain because | Required evolution |
| --- | --- | --- |
| `OrkiRuntimeMissionE2ETests` | Proves goal-to-verified-completion, waits, recovery, cancellation and append-only evidence with real filesystem work | Route the supplied operation through `CallableExecutor`; assert a workflow instance and separate event stream. |
| `CanonicalFactoryAcceptanceSuiteTests` | Proves a temporary Git change, build/retest recovery, plan graph and reflection ordering | Use a selected workflow template or an explicit generated-instance fixture; keep real Git/build assertions. |
| Factory Chat/provider tests | Covers ingress correlation, provider failure and visible waiting | Assert Runtime starts an engine instance; executor owns provider selection/call. |
| Semantic and Knowledge Pipeline tests | Protect embedding evidence and review-before-promotion | Add approved-workflow filter, version pinning and candidate-not-retrievable tests. |

## Migration risks and controls

| Risk | Control |
| --- | --- |
| Duplicate lifecycle authority | Single-writer rule: Runtime writes mission state only; Engine writes workflow/step state only. |
| Existing callers break | Start with adapters and preserve public Runtime command signatures until cutover evidence passes. |
| Lost auditability | Immutable template versions, idempotency keys, append-only Engine events and Runtime event references. |
| Engine bypasses Governance | Engine start is allowed only after Runtime’s existing approval/governance gate. |
| Workflow learning self-activates | Candidate/review/promotion/index lifecycle remains Knowledge Pipeline owned. |
| Scope becomes a rewrite | Execute one phase per approved Sprint; retain and rerun the Foundation E2Es after each state-boundary change. |

## Explicit non-changes

No change is proposed to `ExecutionContract`, approval confirmation, provider secret
handling, `ExecutionRun`/`ExecutionJob` ownership, Cognitive State, AKB activation,
or the user-facing meaning of `COMPLETED`, `FAILED`, waits, cancellation and recovery.
The migration is complete only when direct Runtime execution has no supported caller
and the retained E2Es prove equivalent or stronger behavior through the Engine.

## Foundation delivery record — 2026-08-09

Phases 2 through 5 have an adapter-first foundation in the approved `Workflow Engine
Foundation & Task Model` Sprint: additive persistence and migration, the WSM and
first-class Task model, shadow/structured-decision adapters, and the Factory Chat AI
Task adapter. This is deliberately not a Workflow Service Interface and does not
deprecate public Runtime commands.

The selection and learning foundation also records top-N retrieval evidence,
approved-template-only selection, and generated review-only candidates after
reflection. Template indexing/promotion and an external Workflow Service remain
separate approved-scope work.

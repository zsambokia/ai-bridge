# Phase 1 / Sprint 1 — Architecture assessment

## Scope and baseline

- Authority: Product Owner Factory Development Mode authorization in the active
  conversation; it explicitly permits implementation without a Bridge-issued
  Execution Contract.
- Scope: AI Bridge Runtime 2.0, Phase 1 / Sprint 1 only.
- Baseline: `43ebb3e638d855abc53a5dc22fb4013e6da1b237` on `main`.

## Component mapping

| Area | Assessment | Sprint 1 disposition |
| --- | --- | --- |
| Runtime (`OrkiExecution`) | Owns mission/OESM, governance and completion coordination. | Retained as Mission Orchestrator; now submits operational work rather than invoking provider work. |
| Workflow Engine | Owns `WorkflowInstance`, steps, tasks and WSM evidence. | Retained as domain-state owner; provider prompt and invocation code removed. |
| `ExecutionRun` / `ExecutionJob` | Contract-bound governed development execution with one-to-one job linkage. | Reused unchanged for its existing governed execution purpose; not repurposed for Factory Chat. |
| Provider adapter registry | Existing provider implementation boundary. | Reached only through the new `provider_gateway` module. |
| Recovery | Existing execution recovery serves `ExecutionRun` / `ExecutionJob`. | Preserved; Foundation implements independent, work-item-scoped retry state. |
| Evidence and AKB | Runtime records provider-result evidence then invokes the existing Cognitive State candidate flow. | Preserved; no operational component writes active AKB state. |

## Coupling and duplicate-lifecycle findings

1. The old `WorkflowEngine.execute_chat_provider_task` assembled prompts, chose a
   provider and invoked it. This crossed the Workflow-to-Provider boundary.
2. `ExecutionJob` cannot be the common Engine queue: it requires a governed
   `ExecutionRun` and is intentionally specific to the contract-bound worker.
3. There was no common durable work contract for future domain engines. The
   Foundation therefore adds `OperationalWorkItem`; it does not replace or
   duplicate the governed `ExecutionJob` lifecycle.
4. Workflow retry remains a *domain policy/evidence* state. Operational attempt
   retry, queue state and event evidence move to the Foundation.

## Architecture challenge and adopted clarification

The approved Sprint wording contains the shorthand chain `Domain Engine →
ExecutionRun → Provider Gateway → Provider`. The Runtime 2.0 Constitution is
stricter: domain work is authorized by the Mission State Machine, materialized
as an Operational Work Item, and executed by the Foundation before reaching the
Provider Gateway. Sprint 1 implements the constitutional chain:

```text
Runtime / Mission State Machine
  → authorized OperationalWorkItem
  → Operational Foundation
  → Workflow domain task evidence
  → Provider Gateway
  → Provider
```

`ExecutionRun` remains on its governed-development path. This is a documented
architectural clarification, not an expansion of business behavior.

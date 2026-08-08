# Canonical Factory Acceptance Suite

This is the permanent, provider-neutral release gate for changes to Orki Runtime, Goal, Plan, OESM, Planning, Repository/Execution integration, Factory Chat integration, or Factory Development Mode. It is deterministic and repeatable. It does not redesign Governance, approvals, queueing, providers, `ExecutionRun`, or Cognitive State.

## Three acceptance levels

| Level | Canonical proof | Required result |
| --- | --- | --- |
| 1. Runtime Mission | `projects.tests.test_orki_runtime_mission_e2e` | Goal, referenced cognitive context, planning, execution, waits, pause/resume, retry/recovery, cancellation, verification, reflection, evidence and Completed are all OESM-derived. |
| 2. Engineering Mission | `CanonicalFactoryAcceptanceSuiteTests.test_level_2_engineering_mission_repairs_retries_builds_and_retests` | A real temporary Git repository is changed; a build failure is repaired, then build and regression test pass before goal completion. |
| 3. Factory Mission | `CanonicalFactoryAcceptanceSuiteTests.test_level_3_factory_goal_persists_plan_graph_evidence_and_reflection_before_knowledge` | A business Goal yields a persisted plan-derived mission graph, actual repository change and verification evidence, then reflection and governed candidate submission. |

The Factory plan is the persisted planning artifact; the mission graph is derived from its approved acceptance checks, not a test-set terminal state or a provider-specific workflow. Future semantic planners may replace that graph with richer reasoning/decomposition while retaining the same evidence contract.

## Goal Integrity and knowledge boundary

Goal Integrity Validation compares the original Factory Plan outcome and checks against repository-change evidence, build status, regression status and observed outcome. A failed comparison enters recovery; it cannot complete the Goal.

No execution, planner, provider, tool, job, or OESM step may write Cognitive State or active AKB knowledge. Reflection is persisted first. Only Knowledge Integration may create a candidate, and only existing AKB Governance may accept, activate, or embed it. The acceptance suite proves the ordering and proves no `embedding.generated` event appears while the entry is a candidate.

## Evidence layout

Release evidence is written under these durable roots:

- `docs/evidence/runtime/` — OESM timeline, state transitions, waits and recovery.
- `docs/evidence/engineering/` — repository diff, build, test and regression proof.
- `docs/evidence/factory/` — Goal, Plan, mission graph, reflection, knowledge decision and Factory-level pass/fail.

Each package identifies Goal/Plan/Execution IDs, planning version, timestamp, repository changes, verification outcomes, Runtime events and evidence references. Backend suite execution is mandatory; UI validation is an extension point and does not replace it.

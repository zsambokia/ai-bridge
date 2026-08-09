# Runtime 2.0 Phase 1 - Architecture Convergence Compliance Audit

Status: **FAIL - not ready for Product Owner acceptance**  
Audit baseline: `43ebb3e638d855abc53a5dc22fb4013e6da1b237` on `main`  
Authority: Product Owner Factory Development Mode, Phase 1 Architecture Convergence & Baseline Sprint  
Sprint source hash: `fb6acedebccb4996ddca4985a2a074838381eaa54e96194d479d0217edbf9078`

This is an acceptance audit, not a code review. Sprint 1 and Sprint 2 form one architectural unit. A partial component result never closes either Sprint.

## Verified convergence evidence

| Check | Result | Evidence |
|---|---|---|
| Parallel `OperationalWorkItem` / `OperationalWorkEvent` model and `operational_foundation.py` absent | PASS | Static scan; the parallel model, migration, and synchronous lifecycle implementation were removed. |
| Canonical operational queue remains `ExecutionJob` | PASS | `projects/models.py`; `projects/execution.py` contains `claim_next_job`, `heartbeat_job`, and `execute_claimed_job`. |
| Runtime, Workflow and Execution avoid direct `.providers` imports | PASS | Static scan; `projects/execution.py` now consumes `projects/provider_gateway.py`. |
| Focused validation | PASS | `makemigrations --check`, focused Django regression tests, focused Ruff, and `git diff --check` all passed; latest Conversation/Mission/Foundation suite: 44 tests. |

These repairs are necessary but do not prove the target architecture is complete.

## Sprint 1 - Operational Engine Foundation

| Requirement | Status | Repository evidence / gap |
|---|---|---|
| One operational queue, worker, claim, polling, retry, recovery and lifecycle foundation | PARTIAL | `ExecutionJob` is the surviving durable queue. `projects/orki_runtime.py::dispatch_factory_chat_execution` remains synchronous and `projects/workflow_engine.py::execute_task_adapter` owns immediate task execution/retry behavior. |
| Runtime is mission orchestrator only | FAIL | `projects/orki_runtime.py::start_factory_chat_execution` creates/transitions `OrkiGoal`, `OrkiPlan`, and `OrkiExecution`; its dispatch invokes Gateway and Workflow itself. |
| Workflow has WSM domain behavior only | FAIL | `projects/workflow_engine.py::execute_task_adapter` carries execution/retry behavior besides WSM domain state. |
| Engine -> immutable ExecutionRequest -> ExecutionRun -> Gateway -> Provider | FAIL | Factory Chat reaches `invoke_factory_chat_model` synchronously from Runtime; required request fields and canonical `ExecutionRun` handoff are absent for this route. |
| Gateway is the sole provider boundary | PARTIAL | Direct imports were removed from Runtime, Workflow and Execution. The Gateway no longer imports Conversation or Mission code; it receives request-domain context/prompt/decoder functions explicitly. The synchronous Runtime dispatch still prevents PASS. |
| No Engine-to-Engine calls | FAIL | Runtime directly invokes the Workflow task adapter. |

**Sprint 1 result: FAIL.**

## Sprint 2 - Planning and Conversation Layer

### Conversation Layer compliance

| Requirement | Status | Repository evidence / gap |
|---|---|---|
| Presentation/input/event/approval projection only | PARTIAL | Message, approval, manual-plan and repository-lifecycle endpoints delegate through `projects/factory_missions.py`. The receiving Mission module still synchronously delegates to Runtime/Foundation-incomplete code, so this is not yet the required event-only boundary. |
| No Runtime, Workflow, Planning, Mission State or business authority | PARTIAL | `factory_chat.py` no longer directly starts/dispatches Runtime work, observes approval, creates a plan, or constructs repository lifecycle services. It still imports Runtime projection helpers and the delegated mission implementation lacks the required MSM/PSM/Foundation separation. |
| Read-only side panels | NOT PROVEN | The direct endpoint authority already prevents acceptance; every panel must be checked after the boundary exists. |
| Chat is Planning experience, not a Planning controller | FAIL | Chat controls operational dispatch instead of forwarding an event to MSM. |

### Planning and Mission Resolution compliance

| Requirement | Status | Repository evidence / gap |
|---|---|---|
| Dedicated Planning State Machine | FAIL | No `MISSION_READY_FOR_PLANNING` transition exists; planning is split across `factory_missions.py`, `factory_orki.py`, and `orki_runtime.py`. |
| Planning Engine owns analysis, evidence, gaps, synthesis and approval state | FAIL | `factory_missions.py::apply_understanding` / `create_plan_when_sufficient` mutate planning flow; `factory_orki.py::record_runtime_cognitive_observation` triggers them. |
| Mission Resolution exhausts internal sources before owner question | FAIL | No ordered AKB/repository/bootstrap/configuration/semantic/previous-mission resolution layer or evidence exists. |
| Product Owner receives business-only questions | FAIL | Required Mission Resolution gate does not exist and the Conversation still exposes technical execution authority. |

**Sprint 2 result: FAIL.**

## End-to-end architecture audit

| Relationship | Status | Evidence |
|---|---|---|
| Conversation -> Runtime business call absent | PARTIAL | `factory_chat.py` delegates all four known action endpoints to `factory_missions`; the Mission ingress still calls Runtime synchronously. |
| Conversation -> Workflow call absent | FAIL | Conversation reaches Mission ingress, then Runtime, which calls `execute_task_adapter`. |
| Conversation -> Planning call absent | PARTIAL | Conversation delegates plan creation and approval; the Mission implementation still owns planning flow rather than a dedicated PSM. |
| Planning -> Provider call absent | NOT PROVEN | Planning is not isolated enough to demonstrate this. |
| Workflow -> Provider call absent | PASS (static) | `workflow_engine.py` has no direct `.providers` import. |
| Engine -> Engine calls absent | FAIL | Runtime directly invokes Workflow. |
| Provider -> Mission State mutation absent | NOT PROVEN | Re-audit after MSM boundary introduction. |
| One queue/polling/lifecycle/retry infrastructure | PARTIAL | Duplicate new work-item system is gone, but synchronous Runtime dispatch and Workflow execution/retry remain outside Foundation ownership. |

## Required convergence sequence

1. Make the existing Conversation endpoints input/event adapters and projections; remove direct Runtime dispatch, mission mutation, and repository lifecycle ownership.
2. Consolidate mission authority behind one MSM using existing durable mission data, with Mission Resolution before any Product Owner question.
3. Normalize the existing Foundation handoff around immutable ExecutionRequest and ExecutionRun; route Factory Chat, Planning, and Workflow work through existing `ExecutionJob` infrastructure, without a second queue or worker.
4. Move Planning state and analysis from conversation/cognitive helpers into a PSM/Planning Engine; emit requests only through MSM/Foundation.
5. Reduce Workflow to WSM domain behavior and retry policy; Foundation owns operational retry/claim/recovery.
6. Move Runtime's remaining Conversation-owned semantic helpers into Mission Resolution, then re-audit all direct calls/imports.
7. Run repository-wide release gates, migration evidence, AKB/documentation synchronization, and repeat this audit.

## Acceptance decision

```text
Runtime 2.0 Readiness

Sprint 1:               FAIL
Sprint 2:               FAIL
Conversation Layer:     FAIL
Operational Foundation: PARTIAL
Planning Engine:        FAIL
Workflow Engine:        FAIL
Overall Runtime 2.0:    FAIL
```

No Sprint is accepted separately. The only acceptable final state is **Overall Runtime 2.0: PASS** with no PARTIAL, FAIL, or NOT PROVEN result.

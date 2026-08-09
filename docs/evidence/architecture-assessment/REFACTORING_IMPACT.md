# Refactoring Impact — Orki Runtime + Workflow Engine

## Impact conclusion

The recommendation is a **medium-to-high structural refactor with low immediate
behavioral risk only if delivered in adapters-first slices**.  It is justified by a
clear responsibility defect, but it must not be treated as a cleanup-only rename or a
big-bang replacement.

## Change inventory

| Area | Current artifact | Proposed impact | Compatibility requirement |
| --- | --- | --- | --- |
| Runtime service | `projects/orki_runtime.py` | Replace direct operation/provider execution with Workflow Engine port calls and event projection | Preserve Runtime command/API results during adapter phase. |
| Persistence | `projects/models.py` | Add templates, instances, step attempts/events and migrations | Do not alter historical `OrkiExecution` meaning or foreign keys. |
| Provider delivery | `ExecutionRun`, `ExecutionJob`, provider modules | New AI step adapter delegates to them | No credential, queue or approval ownership transfer. |
| Semantic retrieval | `projects/semantic/intelligence.py` | Add typed filter/index metadata for approved workflow template documents | Keep vector provider-neutral and retrieval-only. |
| Knowledge governance | `projects/knowledge_pipeline.py` | Admit reviewable workflow candidates and approved template promotion | Never index/activate draft or mutable execution state. |
| Factory Chat | `dispatch_factory_chat_execution` and UI tests | Start workflow instead of performing provider call | Preserve correlation, error/wait and idempotency behavior. |
| Tests | Runtime/Factory acceptance suites | Retain real operational effects through test executor | Add state ownership and event-correlation assertions. |
| Documentation | Runtime baseline/architecture/evidence | Amend only in implementation Sprints after evidence exists | This assessment does not silently rewrite current baseline claims. |

## Required proof per implementation phase

1. Model migration forwards and backwards on representative data; existing Runtime
   records remain readable.
2. Unit tests establish that Runtime cannot write workflow state and Engine cannot
   write mission state.
3. The current mission E2E and Factory acceptance remain real operational tests while
   traversing `CallableExecutor`.
4. Idempotency/recovery tests cover duplicate engine start, engine event replay,
   retry/backoff and Runtime restart projection.
5. Factory Chat/provider integration proves the provider is called by an Engine
   executor, while Runtime retains lifecycle/audit events.
6. Workflow selection tests prove top-N evidence, explicit reasoning choice, template
   version pinning and no-match behavior.
7. Learning tests prove candidate → review → approval → index and forbid automatic
   activation.

## Retention and deletion policy

Keep `execute_shadow_operation` and `execute_structured_decision` as compatibility
facades only until their callers migrate.  Their direct callable implementation may be
deleted only after all supported calls are routed through the Engine and the retained
E2Es pass with equivalent evidence.  Keep `ExecutionRun`/`ExecutionJob`; they are not
an obsolete implementation of the proposed Engine.  Do not extend deprecated
`OrkiKnowledgeIntegration`.

## Migration cost and sequencing

The new models/event store and the first shadow adapter are the highest-risk parts
because they define the state ownership seam.  Workflow retrieval and learning should
follow only after that seam is proven, since they otherwise select/learn concepts with
no durable execution target.  An external workflow framework should be re-evaluated
only after the embedded contract demonstrates unmet scale/durability requirements.

## No-change determination

The assessment found no evidence that Goal, Planning, mission verification,
Reflection, Knowledge Pipeline governance, vector retrieval primitives or the
provider-neutral `ExecutionRun` boundary are incorrect.  Refactoring them now would
increase migration cost and undermine the Foundation without addressing the direct
step-execution ownership defect.

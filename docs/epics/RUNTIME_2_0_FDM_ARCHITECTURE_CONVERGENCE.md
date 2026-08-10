# Runtime 2.0 FDM Architecture Convergence Program

## Authority and status

**Status:** canonical program scope; not an executable hierarchy level.

**Product Owner authority:** Factory Development Mode for AI Bridge self-development, granted on 2026-08-09. It explicitly permits local Codex work without an AI Bridge-managed provider run, active provider heartbeat, or Bridge-issued Execution Contract while the managed runtime is not proven stable.

**Binding target:** [Runtime 2.0 Constitution](../runtime/runtime_2_0_constitution.md), version 1.0.0. The target route is:

```text
Domain Engine -> immutable Execution Request -> MSM -> authorized Operational Work Item -> Operational Foundation -> ExecutionRun -> Provider Gateway -> Provider
```

Conversation is an ingress and projection boundary to MSM. PSM and WSM are independent domain engines, not consecutive stages in the execution route.

This document is an FDM program/decomposition boundary. It deliberately does not claim `EPIC` as an executable scope kind and does not grant provider execution authorization. Each child below must be proposed, reviewed, approved, and published by the canonical AI Bridge scope lifecycle as a `SPRINT` or `WORK_ITEM` before implementation starts. The Product Owner FDM authorization remains sufficient for the present scope-definition work only.

## Baseline and problem statement

Baseline: `main` at `8f23f0bad865d676258b3d48895894159f402687`.

The latest independent Runtime 2.0 acceptance material reports an overall FAIL: Conversation/Mission ingress still reaches synchronous Runtime and WSM work, there is no dedicated MSM or PSM, Mission Resolution is incomplete, and the existing durable `ExecutionJob` foundation is bypassed. See the [Phase 1 compliance audit](../evidence/runtime-2-0-phase-1-baseline/COMPLIANCE_AUDIT.md) and the [operational acceptance gap analysis](../evidence/runtime-2-0-operational-acceptance-audit/GAP_ANALYSIS.md).

An apparent historical conflict must be resolved by evidence before migration: the Constitution requires an authorized Operational Work Item, while the surviving durable operational queue is `ExecutionJob` bound to `ExecutionRun`. This program does not authorize a duplicate queue, work-item table, worker, or lifecycle. The first child scope must define and prove the compliant mapping or escalate a constitutional amendment where one is genuinely required.

## Program invariants

- MSM is the only Mission authority. It authorizes, creates, merges and cancels operational work; it does not execute domain engines or provider work.
- Only the Operational Foundation creates/tracks `ExecutionRun` mechanics and invokes the Provider Gateway. The Provider Gateway is the only provider boundary.
- No Conversation, MSM, PSM, WSM, or other engine may call another engine, `ExecutionRun`, the Gateway, or a provider directly.
- Mission Resolution searches AKB, repository, bootstrap, memory, semantic, configuration, prior-mission, provider, and environment evidence before a Product Owner business question. Missing technical data is not a business question.
- Planning begins only after durable `MISSION_READY_FOR_PLANNING`; PSM emits immutable Execution Requests, never provider work.
- Foundation owns queueing, polling, leasing, retry, recovery, telemetry, outbox, evidence, and operational projections. WSM owns only workflow domain state and retry policy.
- Each migrated path preserves correlation, idempotency, policy snapshot, authorized work-item identity, Mission identity, and retained evidence.

## Ordered executable-scope packet

The following are exact child-scope specifications for canonical publication. They are intentionally ordered; a later child cannot begin until its listed entry conditions are evidenced. A child may be split into narrowly scoped Work Items only through the same canonical lifecycle.

| Order | Proposed kind and type | Required outcome | Entry condition | Exit / acceptance evidence |
| --- | --- | --- | --- | --- |
| R20-00 | SPRINT / AUDIT | Produce a fresh Constitution Compliance Baseline and authoritative component, call, dependency, durable-state, and migration map. Decide the non-duplicating mapping between Operational Work Item, `ExecutionRun`, and `ExecutionJob`; record an amendment request if the Constitution cannot be met. | None. | Repeatable static scans, call graph, state-ownership matrix, queue/lifecycle inventory, gap register, rollback plan, and architecture-test specification. No runtime-authority change. |
| R20-01 | SPRINT / MIGRATION | Establish MSM and Mission Resolution; convert Conversation to input/event/approval adapters and read-only projections. | R20-00 accepts the authority/mapping decision. | MSM-only Mission/work authorization tests; ordered resolution provenance; business-only question tests; negative tests for Conversation-to-Runtime/Workflow/PSM/provider authority; durable `MISSION_READY_FOR_PLANNING`. |
| R20-02 | SPRINT / MIGRATION | Normalize the existing operational foundation around immutable Execution Request, authorized operational work, `ExecutionRun`, existing `ExecutionJob`, and Provider Gateway. Migrate Factory Chat work from synchronous dispatch. | R20-01 MSM boundary passes. | One queue/worker/recovery lifecycle only; no Engine-to-Gateway/Provider/ExecutionRun edge; authorized-work-item and idempotency checks; lease/retry/recovery/replay evidence; rollback evidence. |
| R20-03 | SPRINT / MIGRATION | Establish PSM as the sole planning domain owner after MSM readiness and ordered Mission Resolution. | R20-01 and R20-02 pass. | PSM owns analysis, gaps, options, plan revision and approval state; planning-gate tests; AKB/repository/bootstrap/memory/semantic provenance; immutable request emission only through MSM/Foundation. |
| R20-04 | SPRINT / MIGRATION | Reduce Workflow to a Runtime-free WSM and move operational execution/retry mechanics to Foundation. | R20-02 passes; R20-03 is compatible with the shared contracts. | No `execute_task_adapter` operational dispatch path; WSM state/retry-policy-only tests; no engine-to-engine calls; Workflow work follows the foundation handoff and recovery path. |
| R20-05 | SPRINT / AUDIT | Integrate, remove or isolate superseded paths, and independently certify the final Runtime 2.0 architecture. | R20-01 through R20-04 each pass their acceptance gates. | Constitution L1/L2/L3 audit PASS; required 20-scenario acceptance suite; migration and rollback evidence; documentation/AKB/roadmap synchronization; no PARTIAL, FAIL, or NOT PROVEN finding. |

## Boundaries and exclusions

In scope are only the Runtime 2.0 convergence activities listed above: Conversation, MSM/Mission Resolution, Operational Foundation, PSM, WSM, Execution Request/Run/Gateway integration, evidence, migration, and removal of the directly superseded paths.

Out of scope unless a later approved child says otherwise: a second queue or worker architecture; a second governance or scope lifecycle; a new provider boundary; unrelated AKB semantic redesign; product features unrelated to the Runtime 2.0 route; production/destructive operations; and a silent Constitution change. A significant authority or state-machine change requires the Constitution Compliance process and an approved constitutional amendment.

## Required gates for every child

Every published child scope resolves its own policy, but must include at least:

- repository-wide tests, lint/format, type checks, migration checks, and `python manage.py validate_scopes`;
- scope-specific positive and negative architecture tests;
- final-state assessment, machine results, acceptance results, migration and rollback evidence, closure report, and exact branch/commit binding;
- documentation and AKB synchronization; and
- a rerun of all affected gates after any repair.

The only final program acceptance is `PASS - READY FOR PRODUCT OWNER REVIEW` after R20-05 independently establishes Overall Runtime 2.0 PASS. Until then, this program is a governed convergence plan, not a claim that the current implementation conforms to Runtime 2.0.

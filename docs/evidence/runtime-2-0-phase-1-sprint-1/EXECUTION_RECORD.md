# Runtime 2.0 — Phase 1 / Sprint 1 execution record

**Status:** complete — ready for Product Owner review  
**Execution mode:** Product Owner Factory Development Mode  
**Task type:** MIGRATION  
**Scope:** Operational Engine Foundation & Workflow Migration

## Authority and baseline

The Product Owner authorized this Sprint in the active conversation on
2026-08-09. The authorization explicitly permits AI Bridge self-development
without a Bridge-issued Execution Contract or managed provider execution. It
is limited to Runtime 2.0 Phase 1 / Sprint 1 and permits necessary internal
architectural improvements that remain consistent with the Sprint objectives;
material deviations must be documented with their justification.

The approved Sprint source is the supplied attachment
`C:\Users\User\.codex\attachments\b2308c90-de51-4e5c-8a1a-e4f58832775d\pasted-text.txt`
with SHA-256
`fb6acedebccb4996ddca4985a2a074838381eaa54e96194d479d0217edbf9078`.

| Item | Recorded value |
| --- | --- |
| Repository | `zsambokia/ai-bridge` |
| Execution branch | `main` |
| Baseline commit | `43ebb3e638d855abc53a5dc22fb4013e6da1b237` |
| Execution level | `SPRINT` under Factory Development Mode |
| Binding governance | `AGENTS.md`, Bridge Constitution v1.3, Evidence-Driven Sprint Workflow, Runtime 2.0 Constitution v1.0.0 |

## Pre-existing unrelated working-tree state

The following paths existed before this Sprint and are preserved without
modification by this execution:

- `docs/akb/CURRENT_STATE.md` (modified)
- `docs/evidence/runtime-2-0-constitution-phase-0/` (untracked)
- `docs/runtime/` (untracked)

Two other worktrees also existed and are not touched:
`agent/factory-development-lifecycle` and
`agent/governed-execution-cancellation`.

## Assessment findings and implementation direction

- `ExecutionRun` with its one-to-one `ExecutionJob` is the existing governed
  execution queue. It is contract-bound and therefore cannot be repurposed as
  a generic domain-work queue without changing its governance semantics.
- A Foundation-owned `OperationalWorkItem` is consequently the bounded,
  reusable operational envelope. It complements rather than duplicates the
  governed `ExecutionJob`; it has its own lifecycle, event stream, retry
  policy, correlation, context, evidence, and parent linkage.
- `WorkflowInstance`, `WorkflowStep`, `Task`, and `WorkflowEvent` are the
  Workflow Engine's bounded domain state and evidence. They remain Workflow
  ownership; their domain retry policy is not an Operational Foundation queue.
- `workflow_engine.execute_chat_provider_task` currently selects and invokes a
  provider directly, while `orki_runtime.dispatch_factory_chat_execution`
  invokes that Workflow function synchronously. This is the Sprint's primary
  boundary migration target.
- The Runtime 2.0 Constitution clarifies the Sprint's provider-chain shorthand:
  an Engine emits an Execution Request to the MSM; the MSM authorizes a durable
  Operational Work Item; only the Foundation reaches `ExecutionRun`, the
  Provider Gateway, and the provider. This preserves the Constitution's
  prohibition on Engine-to-provider and Engine-to-`ExecutionRun` calls.

## Completed steps

1. Read repository governance, workflow, supplied Sprint, Runtime 2.0
   Constitution, roadmap, architecture baseline, recovery contract, and
   existing Operational Engine assessment.
2. Recorded `main` baseline, worktree state, attachment hash, and unrelated
   changes.
3. Located the governed execution path and the Workflow / Runtime
   provider-boundary breach; recorded the architecture challenge in
   `ARCHITECTURE_ASSESSMENT.md`.
4. Added Foundation-owned `OperationalWorkItem` and `OperationalWorkEvent`,
   including durable lifecycle states, retry policy, context/evidence payloads,
   correlation, parent linkage, and ordered event evidence.
5. Added the Operational Foundation lifecycle service and the sole Provider
   Gateway boundary for Factory Chat.
6. Migrated Runtime dispatch to create and coordinate an Operational Work Item;
   Workflow now retains task/WSM/domain evidence and no longer invokes a
   provider directly.
7. Added architecture/lifecycle tests, generated migration `0067`, and wrote
   architecture, migration, operational-acceptance, validation, and closure
   evidence.

## Validation status and hand-off

See `VALIDATION.md` for exact commands and outcomes. The implementation-specific
checks, full test suite, Django checks, migration drift check, repository-wide
Ruff/format gates, and full mypy check pass. The Release Gate exposed baseline
formatting drift in six tracked paths; it was repaired with non-functional Ruff
formatting and revalidated. No commit or push was made because neither was
requested.

Final binding: branch `main`, baseline commit
`43ebb3e638d855abc53a5dc22fb4013e6da1b237`, with the final working-tree
implementation and evidence ready for Product Owner review.

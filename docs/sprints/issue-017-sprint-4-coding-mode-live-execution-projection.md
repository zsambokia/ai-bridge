# Issue #17 — Sprint 4: Coding Mode and Live Execution Projection

## Authority and boundary

- Authority: Product Owner Factory Development Mode for Issue #17, following the accepted Sprint 1 interaction contract.
- Branch and baseline before mutation: `main` at `ee3c8160ccfdcdc24ce9be7983655aa7afcb7e8b`.
- Scope: read-only Coding Mode projection of an existing canonical `ExecutionRun`.

## Delivered behaviour

- Coding Mode classifies canonical lifecycle states in plain Hungarian and shows current work progress.
- Sprint checklist progress is derived from `activity_summary`; Epic progress aggregates only durable executions whose immutable contract payload names the same Epic.
- Verification instructions, evidence path, final commit when available, Product Owner action/no-action state, recent events, and optional diagnostics are server-rendered.
- A business-decision blocker is the only state that asks for a Product Owner decision. The view starts neither a provider nor a new execution.

## Explicit exclusions

This Sprint does not create, approve, start, modify, or reconcile executions. It introduces no parallel lifecycle, browser-owned progress record, or browser-to-provider call.

## Acceptance and validation

The targeted integration tests verify the Coding Mode empty state and the Product Owner business-decision state. Repository gates and independent audit evidence are in `docs/evidence/issue-017-sprint-4-coding-mode-live-execution-projection/`.

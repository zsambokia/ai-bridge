# Factory Development Mode execution record — Sprint 016

## Authority and implementation boundary

- Product Owner instruction: current Codex conversation, 2026-07-31.
- Repository: `zsambokia/ai-bridge`.
- GitHub tracking issue: [#15](https://github.com/zsambokia/ai-bridge/issues/15).
- Exact implementation boundary: `docs/sprints/SPRINT_016_CANONICAL_EXECUTION_LIFECYCLE_INTEGRITY_AND_AUTONOMOUS_RECOVERY.md` only.  No later Factory Readiness sprint is in scope.
- Execution profile: Product Owner Factory Development Mode.  The local Codex process owns execution while the managed runtime is being repaired; normal scope, evidence, test, and Release Gate requirements remain in force.

## Pre-mutation binding

- Branch: `main` (main-only development is configured).
- Baseline commit: `ff3cf82dee9f580da83c215fb25f7636b2b5fa22`.
- Baseline recorded: 2026-07-31, Europe/Budapest.
- Existing unrelated untracked files were present before this record and are excluded from this Sprint's changes and commits.
- The canonical Epic specification, `docs/epics/factory-readiness-remediation.md`, was synchronized from upstream commit `9c60129aa8df9823cf826fb817bc4f9c720ccb97` before final verification. Its Sprint 1 title and the exact Sprint 016 document match, so the approved Factory Mode instruction remains bounded to this Sprint.

## Completed work

1. Read repository governance, Constitution, evidence workflow, Sprint 016, architecture context, Factory readiness audit, roadmap, AKB baseline, and GitHub Issue #15.
2. Recorded the baseline and preserved unrelated work.
3. Ran the baseline focused lifecycle regression suite: `63 passed`.
4. Identified concrete Sprint-1 gaps: terminal run/job divergence could remain claimable, recovery did not treat a missing provider PID or orphaned workspace as a deterministic signal, and governed read-only lifecycle visibility lacked one canonical projection.

5. Implemented transactional active-run checks before worker dispatch;
   persisted fencing tokens for every lease claim; deterministic run/job
   convergence; structured recovery classification; bounded recovery using the
   existing checkpoint model; local workspace-PID loss handling; and idempotent
   orphan-workspace retention with persisted policy reason.
6. Added focused fault-injection, old-worker fencing, worker-race, idempotence,
   Admin, governed MCP, recovery-classification, and management-command E2E
   coverage.
7. Added the lifecycle operations architecture document and synchronized the
   roadmap and AKB with the implementation.
8. Ran the configured repository-wide gates from the final working state:
   `pytest` (`197 passed`), `ruff check .` (PASS), `mypy .` (PASS; 141 source
   files), and
   `python manage.py validate_scopes` (PASS), plus Django system and migration
   drift checks.
9. Ran `python manage.py reconcile_execution_jobs --once` against the local
   durable state. It completed successfully and reported `0` further jobs to
   reconcile.

## Compatibility and recovery assessment

- Two additive, reversible persistence migrations record the job lease-fencing
  token and workspace retention reason. Existing run, job, workspace,
  recovery-attempt, progress-event, and evidence records remain the canonical
  source of truth.
- A terminal run can no longer be claimed. A worker also rechecks the durable
  lifecycle under lock immediately before provider work, closing the
  claim-to-dispatch race.
- Every automated correction writes append-only event/recovery evidence and a
  subsequent reconciliation observes the converged state without a duplicate
  correction.
- The exact delivery commit and push result are recorded by the final
  main-branch delivery operation; no unrelated pre-existing untracked files
  are staged.

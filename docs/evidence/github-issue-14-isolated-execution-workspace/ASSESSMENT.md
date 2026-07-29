# Issue #14 implementation assessment

## Authority and boundary

This assessment is governed by the explicit Product Owner Factory Development
Mode instruction bound to GitHub Issue #14. It is intentionally not an
implementation of the historical, differently scoped `SPRINT_014` document.

## Existing components reused

- `ExecutionRun`, `ExecutionJob`, durable execution events, worker leases, and
  the reconciliation pattern remain the control-plane source of truth.
- The existing provider registry and local Codex adapter remain responsible for
  provider identity, readiness, and lifecycle messages.
- The existing local settings profile supplies the managed runtime's isolated
  SQLite database through `AI_BRIDGE_RUNTIME_DB`.

## Extensions and new canonical boundary

- `RuntimeBootstrapProfile` is the canonical Project-owned runtime recipe. It
  declares the database profile, optional deterministic seed command, ordered
  optional services, and non-secret environment; workers do not hard-code a
  project recipe.
- `ExecutionWorkspace` is the one durable workspace record for each execution;
  it records lifecycle, baseline, paths, interpreter, environment, database
  profile, migration/seed/service state, dependency fingerprint, retention,
  cleanup manifest, and failures.
- `WorkspaceManager` is the sole provisioning, verification, reuse, retention,
  and cleanup boundary. It creates token-scoped directories outside the control
  plane, uses a repository mirror, checks out the immutable baseline, creates a
  venv, installs dependencies, creates and migrates the isolated application
  database, deterministically applies or skips seed data, starts declared
  services, and validates the result before returning `READY`.
- Provider launch now receives the sanitized runtime descriptor only after
  `WORKSPACE_PREFLIGHT_PASSED` and `WORKSPACE_READY`. The worker terminalizes a
  provisioning failure for that execution and continues processing later jobs.
- The reconciliation command retains failed/recovery evidence and safely cleans
  only expired token-scoped paths, with an idempotent persisted manifest.

## Operational contract

The workspace lifecycle is `REQUESTED -> PROVISIONING -> READY -> IN_USE ->
VALIDATING -> RETAINED -> CLEANUP_PENDING -> CLEANED`; failures persist as
`FAILED` and are retained. Completed runs retain workspaces for three hours,
failed workspaces use the configured 24-hour default, and blocked or recovery
review runs are retained indefinitely. Django admin exposes read-only sanitized
workspace metadata; no workspace is exposed as a writable execution API.

The regression suite covers provider ordering, runtime bootstrap lifecycle
events (including deterministic skipped seed/service states), failed-workspace
worker isolation, and token-scoped idempotent cleanup. Final machine-gate
evidence is recorded in `CLOSURE_REPORT.md`.

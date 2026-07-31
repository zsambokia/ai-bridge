# Operational Acceptance — Sprint 016

**Date:** 2026-07-31 (Europe/Budapest)  
**Repository:** `zsambokia/ai-bridge`  
**Execution profile:** Product Owner Factory Development Mode  
**Acceptance runtime:** isolated local Django runtime at `127.0.0.1:8017`  
**Code revision under test:** `546bde6a66eaf645ddc0f3e047b5ed5c238f4847`

## Revision binding and repair history

The original Engineering Acceptance revision was
`5bd60c4024c0ae27fcef837b5883a0fbcf03d730`. A real dead-provider-PID fault
injection against an isolated runtime created from that exact revision found a
Windows-specific defect: `os.kill(pid, 0)` treated a terminated PID as live,
so reconciliation terminalized the run as external input instead of recovering it.

That result is negative evidence, not a PASS. The Sprint-scoped repair uses a
Windows process handle and `GetExitCodeProcess` in
`projects.execution_recovery.provider_pid_is_alive`, with a regression test for
a nonexistent PID. It was committed and pushed as
`546bde6a66eaf645ddc0f3e047b5ed5c238f4847`.

The acceptance server was started directly from a detached worktree whose
`git rev-parse HEAD` was that SHA. Its Python command line named that
worktree's `manage.py`; the isolated SQLite database was migrated through
`projects.0035_executionworkspace_retention_reason`. `GET /health/` returned
`200 {"status":"ok","service":"ai-bridge"}`.

The shared stage endpoint was intentionally excluded from this claim: its
health response does not expose a revision/build identifier, so it cannot prove
that it runs either `5bd60c4` or `546bde6`. This report therefore proves the
declared Factory acceptance runtime, not an unverified stage deployment.

## Runtime recovery smoke

Two durable runs were created in the isolated, migrated database with consumed
contract metadata, a real `ExecutionJob`, an `ExecutionWorkspace`, checkpoints,
and a separate real OS provider sentinel process.

| Scenario | Controlled fault / action | Observed canonical result | Result |
| --- | --- | --- | --- |
| Live-provider reattach | Expired worker lease while the provider sentinel PID remained live; then `run_execution_worker --once --worker-id operational-acceptance-worker --lease-seconds 60` | The worker acquired a new fenced lease, emitted `WORKER_LEASE_ACQUIRED`, `WORKER_HEARTBEAT`, and `WORKER_REATTACHED_TO_PROVIDER_EXECUTION`; run remained `RUNNING / IMPLEMENTING`. | PASS |
| Dead provider / stale workspace | Expired lease, stale workspace heartbeat, then controlled termination of the provider sentinel PID | `reconcile_execution_jobs --once` emitted `Workspace Provider Pid Missing` and `Recovery Checkpoint Queued`; workspace became `READY` with no provider PID, job became `RECOVERING` with `RESUME_FROM_CHECKPOINT`, and run became `STARTING / RECOVERING`. | PASS |
| Canonical completion | `complete_run` with final SHA, gate result, evidence manifest, changed-files list, and failure classification | Independent run became `COMPLETED / COMPLETED / PASS`, with final commit `546bde6a66eaf645ddc0f3e047b5ed5c238f4847`. | PASS |

The worker and reconciliation command are production code paths, not unit-test
mocks. The provider process was deliberately a harmless OS sentinel; no
external Codex task was launched, so this evidence does not claim a paid or
repository-mutating provider execution.

## Admin, application API, and MCP projection

The dead-provider run was inspected through all supported read surfaces:

- an authenticated Django Admin session returned HTTP 200 and contained
  `STARTING`, `RECOVERING`, and `READY`;
- `invoke_public_tool("execution.get_run_status", ...)` returned the canonical
  projection; and
- an authenticated JSON-RPC request to `/mcp/` returned the same projection.

After excluding the dynamic observation timestamp only, the stable projection
was byte-for-byte equal across the application API and MCP:

```text
status=STARTING
phase=RECOVERING
queue.status=RECOVERING
queue.fencing_token=1
queue.recovery_attempts=1
queue.recovery_action=RESUME_FROM_CHECKPOINT
workspace.status=READY
workspace.provider_pid_present=false
```

Admin renders this same canonical lifecycle projection as its read-only
recovery summary. The runtime has no competing REST lifecycle endpoint; MCP
uses the public application-tool invocation boundary.

## Release gates after the repair

| Gate | Result |
| --- | --- |
| `pytest` | PASS — 198 passed |
| `ruff check .` | PASS |
| `mypy .` | PASS |
| `python manage.py check` | PASS |
| `python manage.py makemigrations --check --dry-run` | PASS |
| Migration of isolated acceptance database | PASS |
| `git diff --check` | PASS |

## Operational decision

**Engineering Acceptance:** PASS (superseded code revision repaired and revalidated).  
**Operational Acceptance:** PASS for the declared isolated Factory acceptance
runtime at `546bde6a66eaf645ddc0f3e047b5ed5c238f4847`.

No assertion is made about the externally shared stage until it exposes a
verifiable runtime revision and is separately exercised. Sprint 2 was not started.

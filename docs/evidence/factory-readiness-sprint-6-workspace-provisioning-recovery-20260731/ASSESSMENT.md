# Sprint 6 workspace-provisioning recovery assessment

## Scope

This assessment records the repair and local-runtime verification for execution
`218cb756-807c-46d5-8e82-dc19ac210f08`, within Sprint 6: End-to-end
Operational Acceptance. It does not substitute local evidence for the required
ChatGPT Business UI to Remote MCP proof.

## Initial durable facts

The run was `STARTING` at `WORKSPACE_PROVISIONING_STARTED`; its job was
`LEASED` by `stage-worker-1`, with an expired lease and no later heartbeat.
There was no `ExecutionWorkspace`, workspace identifier, or provider execution
identity. Events 1--6 ended at `WORKSPACE_PROVISIONING_STARTED`.

Consequently the last successful persisted operation was
`WORKSPACE_PROVISIONING_STARTED`. The first missing successful transition was
`WORKSPACE_REPOSITORY_READY`; the required alternative missing transition was a
durable provisioning failure/recovery record. No durable evidence supports a
claim that checkout, venv creation, database initialization, seed, bootstrap,
or provider start happened in the interrupted original attempt.

## Root cause and repair

The prior reconciler considered provider-stage `RUNNING` work but excluded an
expired provider-free `STARTING` lease. When its worker disappeared, no process
was left to reclaim that lease and the run could remain quiet indefinitely.

`workspace_provisioning_recovery.py` now independently detects that condition,
records append-only recovery evidence, clears the lease, and queues bounded
recovery. The worker routes unexpected pre-provider exceptions through the
same logic. After three attempts it records the deterministic canonical review
state rather than silently remaining intermediate.

## Exact execution verification

Running `reconcile_execution_jobs --once` produced event 7,
`WORKSPACE_PROVISIONING_RECOVERY_QUEUED`, with the stale lease/heartbeat facts.
The same execution then reclaimed its lease and recorded events 13--26 in
order: repository ready, venv ready, dependencies ready, workspace database
ready, application database created, migrations applied, seed skipped, runtime
services skipped, preflight passed, workspace ready, provider started, executor
started, execution activity started, and worker dispatch completed.

The resulting workspace was isolated at
`.ai-bridge-workspaces/218cb756-807c-46d5-8e82-dc19ac210f08`, with its own
checkout, venv, and SQLite runtime database. A continuously running worker
later reported a live provider and fresh heartbeats. A subsequent provider
terminalization was independently persisted as events 27--28; it is not a
provisioning silence and remains distinguishable from this repair.

## Acceptance boundary

The repair, regression suite, and local operational recovery proof pass. The
full Sprint 6 Operational Acceptance is still not demonstrated: this Codex
environment has no controllable ChatGPT Business browser session (`Browser is
not available: iab`), so no user-visible Business UI request, in-UI Product
Owner confirmation, Remote MCP ingress, deployment, retrieval, or feedback
loop could be honestly executed here. Static HTTP authentication was not used
as a substitute.

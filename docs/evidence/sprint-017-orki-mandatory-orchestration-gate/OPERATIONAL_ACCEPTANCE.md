# Sprint 2 operational acceptance

This acceptance ran against an isolated local Factory runtime, not a unit-test
database. The runtime was started at `2026-07-31 13:05:42` on
`127.0.0.1:8018` from `4b8f59f19f8f215993811973f88d4f71374e08b7` (the final
implementation revision before this documentation-only closure commit).

## Normal governed request and recovered completion

The ChatGPT-facing streamable HTTP MCP surface accepted a harmless,
workspace-only request and persisted the full Orki trace:

| Record | Durable value |
| --- | --- |
| Scope | `bridge:ai-bridge:work-item:edf5b67e-a3ed-4339-b869-385321927c6b` |
| Conversation orchestration | `77e4362f-5f84-4509-83b7-ce8da4d0a834` |
| Orki session | `f7ef47ae-5de2-4d1a-bee5-2bdbae899abd` |
| Contract | `bridge:ai-bridge:contract:4941c438-e99b-4790-87d2-b1374ec8be62` |
| Execution run | `e023fe82-bc62-4e6c-a8c4-947a14080cbf` |
| Ownership / policy | `ENGINEERING`, confidence `1.0`, `ALLOW` |
| Provider / runtime binding | `codex-cli` / `231014b4f36881302e7bf1ad16f2a0d0f6775c298413401d3d48df65ace1dc34` |
| Final state | scope, contract and run: `COMPLETED`; evidence terminal state: `PASS` |

The real worker provisioned the isolated workspace, initially encountered the
Codex readiness defect, released the job for recovery, and later reprovisioned
it. Events 24--43 show the recovered lease, workspace reuse and preflight,
Codex process `22280`, provider activity, and dispatch. After the provider
exited, `execution.complete` accepted the actual isolated-workspace final
commit `e331187bc600acb80cc365a22f08caa05a043f7c`; MCP then returned
`COMPLETED` for the run, contract, and scope.

## Fault injection and recovery evidence

A second harmless run
`84ead39d-def0-476c-9f15-e4476a5fce5b` was used for controlled provider-loss
injection. Once its provider PID disappeared, reconciliation emitted
`Workspace Provider Pid Missing` and `Recovery Retry Queued`. A deliberately
concurrent recovered run then produced `EXECUTION_BRANCH_CONFLICT_DEFERRED`,
which released the worker lease rather than crashing the worker. The competing
run was cancelled through the normal confirmation/cancellation lifecycle;
the first run then recovered and completed. This is a live dead-provider,
recovery, and protected-branch-conflict proof.

## Admin, API, and MCP consistency

An isolated-runtime Django superuser logged in over HTTP. Both
`/admin/projects/executionrun/1/change/` and
`/admin/projects/orchestrationsession/1/change/` returned `200` and displayed
the exact run/session tokens and `COMPLETED`. The versioned HTTP MCP API
(`tools/call`) simultaneously returned the same Orki session, project,
repository, hashes, provider profile, contract, run, and `COMPLETED`
lifecycle through `execution.get_run_status` and
`scope.orchestration_status`. The service status endpoint reported protocol
`2025-03-26`, tool surface `2026-07-31.2`, and the single ready `ai-bridge`
project.

## Honest failed attempts retained

- The first confirmation request used a non-ASCII literal through Windows
  PowerShell and was rejected as malformed JSON before it could create a
  conversation. The ASCII retry was accepted normally.
- The initial provider dispatch revealed the real readiness defect repaired in
  iteration 4 above; it is not represented as a passing unit-test-only claim.
- A completion request with the control-plane revision was rejected as
  `RUN_FINAL_COMMIT_MISMATCH`. The subsequent request used the actual
  workspace baseline recorded by the run and completed successfully.

No production system, credential, or unrelated user work was modified. The
isolated database, retained workspaces, and server logs remain locally under
`.sprint2-operational-runtime/` as reproducible raw evidence and are excluded
from the repository commit.

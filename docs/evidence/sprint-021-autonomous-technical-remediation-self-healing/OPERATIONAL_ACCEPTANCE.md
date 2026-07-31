# Operational Acceptance — Sprint 7

Date: 2026-07-31

## Isolated live runtime proof

An isolated local runtime database was migrated through projects migration
`0042_sprint7_independent_validation` and a local HTTP server was started with
a test-only bearer value supplied only to the process environment. Neither a
credential nor its value is committed or reproduced here.

| Check | Result |
| --- | --- |
| Migration to current schema | PASS |
| `GET /health/` | PASS (HTTP 200) |
| Authenticated MCP `initialize` | PASS (HTTP 200; opaque session issued) |
| Authenticated MCP `tools/list` | PASS (HTTP 200; 83 tools) |
| `execution.get_run_status` offered by runtime | PASS |
| Isolated runtime database | PASS |

The first attempt deliberately supplied an empty inherited `MCP_API_TOKEN` to
a child process and was rejected with HTTP 401. Diagnosis: the child process
did not retain the empty environment value, so the local `.env` precedence was
used. The retry explicitly supplied the test-only token as `MCP_API_TOKEN`;
it passed. This failed attempt is retained because it confirms fail-closed MCP
authentication rather than being treated as a successful proof.

## Lifecycle fault proof

The persisted worker fault/resume scenario is exercised against Django's real
database and worker command in the targeted integration suite. It verifies:

```text
leased job + unknown worker exception
-> FailureIncident / ownership / child scope / checkpoint persisted
-> job FAILED and lease released
-> run REPAIRING and MCP-visible remediation state
-> independent validation PASS
-> same job requeued and original run checkpoint restored
```

The MCP projection test proves the canonical remediation and validation chain
is visible on `execution.get_run_status`; the Admin classes use the same model
records read-only. No ChatGPT Business UI assertion is made by this Sprint.


# Sprint A acceptance results

| Acceptance check | Evidence |
| --- | --- |
| The web/governed path persists, rather than starts, the execution | `enqueue_run` creates `ExecutionRun(REQUESTED)` and `ExecutionJob(QUEUED)`; governed conversation and remediation dispatch use it. |
| Independent worker starts the provider | `run_execution_worker --once` claims the durable job and starts it outside the request process. |
| Worker ownership is durable | Claim state records worker identity, expiry, heartbeat, attempt metadata and append-only events. |
| Worker interruption can recover | A second worker atomically reclaims an expired lease for the same job and run. |
| Django reload cannot orphan an in-memory execution | Queue state is database-backed and no provider is launched by the normal Django/MCP dispatch path. |
| Governance remains unchanged | Existing contract validation, provider identity selection, consumption receipt and event model are reused; no new scope or contract was created. |

Focused validation before repository-wide gates:

```text
pytest projects/tests/test_execution.py projects/tests/test_remediation.py projects/tests/test_governed_mcp.py -q
48 passed

manage.py makemigrations --check --dry-run --settings=bridge.settings.test
No changes detected
```

# Sprint A engineering assessment

## Authority and boundary

- Canonical scope: `bridge:ai-bridge:sprint:df759a70-284b-4da0-95db-eb7ede717609`
- Proposal: version `1`, SHA-256
  `156313cb5e6d55400e1d3808c3f276ea6cb9d9193d77981610eb506fe251841c`
- Execution mode: the Product Owner's explicit Factory Development Mode
  bootstrap authority for this repository's self-development.

No Bridge confirmation, Bridge-managed provider execution, alternate scope, or
alternate execution contract was created. This evidence records the approved
Sprint A implementation only. Sprint B, C, and D are explicitly outside this
change.

## Design assessment

The existing `ExecutionRun` and append-only `ExecutionProgressEvent` models
remain canonical for authorized execution and history. A one-to-one
`ExecutionJob` is the minimum durable hand-off needed to prevent an HTTP/MCP
request or Django autoreloader from owning provider startup. The existing
contract validation and provider selection are reused by the worker; no new
authority path or provider fallback was introduced.

The worker uses a database transaction and `select_for_update` to claim a
queued or expired lease. It persists owner, expiry, heartbeat, safe attempt
metadata and events before dispatch. A new worker can reclaim an expired lease
without creating a second run. This satisfies the Sprint A queue/worker
separation while deliberately leaving broader reconciliation and remediation
policy to the ordered later Sprints.

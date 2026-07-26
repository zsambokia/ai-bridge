# Sprint 005 assessment

**Contract:** `bridge:ai-bridge:sprint_005_tiered_execution_contracts_and_cloudflare_host_repair:e0676db2-b7b4-47c2-9ba0-bf3cce45470c`  
**Preflight baseline:** `ffdd62e7ff43952266cbc2fd89216a8b32ed38ca` on `main`  
**Repository:** `zsambokia/ai-bridge`

## Existing canonical components

| Concern | Existing component | Sprint 005 decision |
| --- | --- | --- |
| Durable contracts | `projects.models.ExecutionContract` | Extend the existing lifecycle record and preserve issued-payload immutability. |
| Contract generation and validation | `projects.contracts` | Add level, task-type, risk, and policy resolution here. |
| MCP boundary | `projects.mcp` | Extend the registered canonical operations rather than introducing another API. |
| Project/baseline resolution | `projects.execution_context` and `projects.services` | Reuse its project-definition, branch, gate, and repository checks. |
| Django host policy | `bridge.settings.base` | Add a named, parsed environment setting with an exact safe default. |

## Scope and risks

The contract generator currently has a single implicit profile, accepts arbitrary
task-type text, and exposes only generation through rendering.  It needs a
deterministic policy resolver, level-aware validation, lifecycle completion
operations, and tests.  The Django base settings contain an empty
`ALLOWED_HOSTS`, which causes the reported Cloudflare Tunnel rejection.

The repair will use only the two approved fully-qualified host names as the
production-safe default.  An environment variable may add explicitly named
hosts; it cannot introduce `*`.  Test settings retain `testserver`.

## Boundaries

In scope are tiered contract governance, its documentation and evidence, and
the two Cloudflare host names.  The existing root route has no product UI and
the approved sprint explicitly excludes login/authentication UI, so no login
screen is added in this execution.

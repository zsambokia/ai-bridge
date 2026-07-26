# Bridge MCP tool reference

The remote `POST /mcp/` endpoint exposes a deterministic versioned registry.
All calls require `Authorization: Bearer <MCP_API_TOKEN>`. Results are bounded
JSON; the server never exposes arbitrary files, shells, SQL, credentials, or
raw Django mutation APIs.

| Group | Tools | Class | Next step |
| --- | --- | --- | --- |
| Discovery | `factory.get_status`, `factory.list_capabilities` | read-only | choose a project tool |
| Project | `project.list`, `project.resolve`, `project.continue_resolution`, `project.get`, `project.get_context` | read-only / preparatory | inspect context or AKB |
| Accepted knowledge | `akb.search`, `akb.get_document` | read-only | prepare execution |
| Preparation | `execution.prepare`, `execution.get_status`, `execution.continue`, `execution.render_handoff` | preparatory state / read-only | generate a contract |
| Lifecycle | `contract.generate`, `contract.validate`, `contract.issue`, `contract.consume`, `contract.complete`, `contract.supersede`, `contract.revoke`, `contract.get_status`, `contract.render_handoff` | preparatory, approval-required, lifecycle mutation | use only returned identifiers |
| Execution boundary | `execution.request_start`, `execution.cancel` | execution boundary | start or cancel an owned run |
| Execution observability | `execution.get_run_status`, `execution.list_events`, `execution.evidence_summary` | read-only | monitor the returned execution token |
| Canonical scope | `scope.classify`, `sprint.propose`, `work_item.propose`, `scope.validate`, `scope.approve`, `scope.publish`, `scope.get`, `scope.contract.generate`, `scope.complete`, `scope.cancel`, `scope.supersede` | canonical planning and lifecycle | bind approval and publish before contract generation |

`project.resolve` returns `PROJECT_RESOLVED`, `USER_INPUT_REQUIRED`, or
`PROJECT_NOT_FOUND`; never select an ambiguous project silently.
`execution.prepare` accepts a canonical `scope_identifier` only, returns
`EXECUTION_PREPARED`, and cannot issue or consume a contract. A provider must
supply its identity, the expected contract hash, baseline, schema version and
idempotency key to `contract.consume`; the resulting durable receipt is
required by `execution.request_start`. The start operation writes the authorization and dispatch audit
record before it launches the configured canonical Codex CLI provider, then
returns an `execution_token`. A successful response therefore means a provider
process was started, not merely that a request was queued. `execution.list_events`
returns bounded, ordered, secret-filtered progress records; it never returns
provider stdout, stderr, or credentials.

State-changing calls require an idempotency key. Lifecycle-changing calls and
the execution boundary also require a durable, non-revoked Product Owner
approval reference scoped to the project and action. A Bearer token alone is
not an approval.

Example user requests: “Find the ai-bridge project and show its current
context”, “Search accepted knowledge for release gates”, and “Prepare Sprint
007; tell me which durable approval is required next.” Avoid asking the model
to invent identifiers, hashes or approvals: it must use values returned by prior
tools.

## Canonical scope authority (Sprint 010)

Internal Bridge operations are `scope.classify`, `sprint.propose`,
`work_item.propose`, `scope.validate`, `scope.approve`, `scope.publish`,
`scope.get`, and `scope.contract.generate`; `sprint.*` and `work_item.*`
validate/approve/publish/get aliases route to the same canonical authority.
Approval is durable and mandatory before a scope can authorize execution.
Canonical document validation is available through `python manage.py
validate_scopes`. `scope.complete`, `scope.cancel` and `scope.supersede` make
the scope terminal; no terminal scope can generate, issue, consume or start a
new contract. `contract.complete` requires final commit, allowed closure state,
execution result, non-empty gates and evidence manifest, changed files and a
failure classification from a matching terminal execution run.

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
| Conversational review | `scope.review`, `scope.answer_clarifications`, `conversation.confirm`, `scope.confirm_and_execute`, `scope.orchestration_status`, `scope.complete_execution` | review, execution boundary, and read-only status | review the exact version; one confirmation drives the bounded lifecycle |

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

## `execution.prepare` input contract

The published `tools/list` schema and the runtime validator both consume the
same governed registry declaration. `execution.prepare` requires exactly
`project_id`, `scope_identifier`, and `idempotency_key`; it does not accept a
natural-language `request`, a legacy `sprint_path`, or a Markdown document as
authority. Send natural language to `work_item.propose` or `sprint.propose`,
then validate, bind durable approval, publish, and pass the returned canonical
scope identifier to preparation. Invalid calls identify the specific missing
or unknown property, type, or enum violation.

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

## Conversational confirmation (Sprint 011, repaired in Sprint 012)

`scope.review` returns the complete pending proposal, immutable version and
SHA-256 hash, policy, acceptance checks, and Release Gates. Clarification
answers are recorded through `scope.answer_clarifications`; a material answer
creates a new version and hash. For an eligible review it also returns
`next_tool: conversation.confirm` and `required_user_input:
["confirmation_text"]`. `conversation.confirm` is the high-level
conversational approval entry point: it accepts the Product Owner's documented
affirmative phrase and derives its authenticated caller binding, durable
confirmation reference, and deterministic retry key server-side. It binds the
exact current review.

`scope.confirm_and_execute` is the explicit structured orchestration entry
point for clients that have already displayed and submit the exact version and
hash plus their durable identity/reference/retry values. `scope.approve` is a
lower-level approval-binding operation and requires an already-existing durable
approval reference; it is not a fallback for conversational confirmation.
Stale versions, unresolved clarification, and unbound confirmation are
rejected.

The orchestrator records separate approval, publication, preparation, contract,
consumption, and run records. `scope.orchestration_status` is read-only.
`scope.complete_execution` requires a stopped provider, all-PASS gates,
non-empty evidence manifest, changed files, and final commit SHA before it
returns the evidence-backed completion message `Főnök, kész!`.

## Audit work type and provider boundary (Sprint 013)

`AUDIT` is accepted as `task_type` and `work_type` by the canonical proposal
tools. It remains attached to a `SPRINT` or `WORK_ITEM`; it does not create a
third executable scope kind. Audit proposals carry their target, questions,
required inventory and classifications, mutation policy, repair rule, and
acceptance checks in the normal proposal payload.

The current operational provider inventory contains exactly `codex-cli`.
Contract generation records it as `selected_provider_identity` and the sole
eligible identity. `contract.consume` rejects a different identity, and
execution resolves the receipted identity for start, status, and cancellation.
Names that appear only in documentation are not advertised as operational
providers.

## Provider visibility

The read-only public tools `provider.list`, `provider.get`,
`provider.capabilities`, and `provider.health` expose provider identity, role,
capabilities, status, and safe health state. They never return configuration,
credential bindings, secret values, or raw external responses.

# MCP Execution Context and Remote Server

Sprint 004 extends the canonical `projects` domain; it does not create a
second Registry, Context store, or AKB system.

```text
Project Registry + Project Context + .bridge/project.yaml + approved Sprint
                                 ↓
                         Execution Context
                                 ├── MCP response
                                 ├── Codex execution package
                                 ├── Markdown contract (future rendering)
                                 ├── audit record (future persistence)
                                 └── future agent context
```

The canonical `projects.mcp` operation registry remains an internal service
surface for Project resolution, execution-context construction, and contract
lifecycle work. It is not a public HTTP protocol and is deliberately not
exposed as a ChatGPT tool surface.

Sprint 006 replaces the public proprietary adapter at `POST /mcp/` with a
stateless, JSON-RPC 2.0 MCP server using the 2025-03-26 protocol version and

Sprint 007 keeps the HTTP layer as a thin adapter and routes `tools/list` and
`tools/call` through `projects.governed_mcp`. The registry owns stable schemas,
annotations, authorization classification, bounded output and audit/idempotency
hooks; canonical project, execution-context and contract services remain the
only domain implementations.
Streamable HTTP transport. It supports `initialize`, `notifications/initialized`,
`tools/list`, and `tools/call`. Every protocol failure is a JSON response; the
endpoint is CSRF-exempt because Bearer authentication, rather than browser
cookies, is the security boundary. It returns `Cache-Control: no-store, private`
and never redirects to a login page.

The public registry currently contains exactly one least-privilege tool:
`factory.get_status`. It reads real `Project` state and returns a deterministic
summary. The tool has no input and cannot mutate Bridge state, repository state,
or execution-contract lifecycle records. Write-capable governance operations
remain internal until an approved Sprint defines their authorization model.

At the Cloudflare boundary, Django accepts only configured hosts, trusts
`X-Forwarded-Proto: https` for secure-request handling, and may use the
forwarded host. `MCP_PUBLIC_BASE_URL`, `MCP_AUTH_MODE=bearer`, and
`MCP_API_TOKEN` are deployment configuration; the token is never stored in the
repository. The public staging URL and operator procedure are documented in
`docs/integrations/CHATGPT_MCP_CONNECTION.md`.

`resolve_project` only searches active, ready Registry records. A single match
returns `PROJECT_RESOLVED`; multiple matches return `USER_INPUT_REQUIRED` with
candidate records and a UUID continuation token. The candidates are persisted
in `ProjectResolutionContinuation`; `continue_project_resolution` consumes the
same record only when the caller selects one of its candidate IDs.

`generate_execution_context` requires explicit `project_id` and
`approved_sprint_path`. It validates the Project, valid Project Context, static
definition, repository identity, and approved Sprint marker. Its structured
response exposes `execution_context` and `codex_execution_package` as two
names for the very same canonical object. It includes the target repository
and branch, Context source commit as the exact baseline, binding governance
paths, release gates, deterministic evidence root, allowed terminal states,
and an execution ID. No value comes from chat memory or an inferred active
project/sprint.

`ExecutionContract` is the durable canonical handoff record. Generation resolves
the current repository baseline, bindings and hashes; validation re-resolves
those inputs; issuance makes the payload immutable and rejects evidence-root
collisions. Repository-stored issued contracts use the deterministic
`DESCENDANT_OF` baseline rule: publishing the contract itself necessarily makes
the repository `HEAD` a descendant of the generation baseline, while preserving
the exact immutable baseline SHA. `EXACT` remains available when an artifact is
not committed into the governed repository. Human-readable handoff Markdown is
rendered only from stored data, so it cannot drift from the issued contract.

Sprint 005 makes the contract policy tiered and deterministic. Each contract
stores a `HOTFIX`, `BUGFIX`, `TASK`, `SPRINT`, or `EPIC` execution level, task
type, explicit risk modifiers, and a resolved policy profile. The profile binds
assessment depth, Project-resolved Release Gates, evidence, documentation and
review obligations. Risks add requirements only. `EPIC` contracts require child
contract identifiers and cannot be consumed for code changes. The transport now
also exposes `consume_execution_contract`, `complete_execution_contract`,
`supersede_execution_contract`, and `revoke_execution_contract`; completion
durably binds final commit SHA and the allowed closure state.

Sprint 009 adds a single execution ownership model rather than a second
dispatcher. `ExecutionRun` binds the consumed contract, requested repository,
branch, baseline, contract hash, Bridge workspace, external provider workspace,
provider execution ID, audit event and evidence root. Its lifecycle is
`REQUESTED → STARTING → RUNNING → VALIDATING → REPAIRING → DOCUMENTING →
CLOSING → COMPLETED`, with explicit business/external/governance blocks and
`CANCELLED` terminal paths. Bridge persists preflight and audit ownership before
calling the provider, and emits ordered, bounded, secret-filtered progress
events afterwards. The initial provider is a fixed-argument `codex exec`
adapter; it does not persist credentials or raw provider output.

Routine failures are classified deterministically (migration, lint/type,
repository/implementation) and enter `REPAIRING`; unavailable providers and
reserved Product Owner decisions do not masquerade as automatic repairs. A
future gate runner may extend this controller, but it must preserve the same
contract, event, retry, evidence and terminal-state ownership.

## Sprint 010 canonical scope authority

`ExecutableScope` is the only authority for new executable Sprints and
standalone Work Items. It stores canonical machine data, lifecycle state,
policy, approval reference, publication path and content hash. The Bridge MCP
operations classify, propose, validate, approve, publish and retrieve scopes;
`sprint.*` and `work_item.*` aliases make the ownership explicit. Free-text
Markdown and legacy status headings are read-only historical material and are
rejected as new authority.

Approved, published scopes generate schema `2.0` execution contracts issued by
AI Bridge. A provider must consume the exact hash under its identity, cannot
self-issue or self-authorize, and receives a durable consumption receipt. The
Bridge rechecks approval, scope state and exact publication at validation,
issue, consume and start. Completion accepts only a matching terminal run at
the checked-out final commit with non-empty gates and evidence manifest;
Markdown is never an authorization input.

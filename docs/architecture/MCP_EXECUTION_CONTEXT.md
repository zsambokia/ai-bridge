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

The public registry is a versioned least-privilege surface. It includes
discovery, Project and AKB reads, deterministic scope and contract lifecycle
operations, and Sprint 011's constrained conversational review operations.
Each write schema is validated by the same registry used for `tools/list`;
idempotency and audit records are enforced at the public boundary. A Bearer
token alone is never execution authority.

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

Sprint 011 adds `ConversationOrchestration`, a durable coordinator rather than
a replacement lifecycle. A review exposes the exact proposal version and hash.
One Product Owner confirmation binds those values and advances canonical
approval, publication, preparation, contract, consumption, and dispatch
services. Every transition remains separately auditable; retries resume the
same orchestration, contract, and run. Completion requires a stopped provider,
all Release Gates, and recorded evidence.

Sprint 012 confirms that this is the sole conversational approval architecture:
`conversation.confirm` is the high-level entry point and derives an auditable
binding, confirmation reference, and deterministic retry key from the
authenticated MCP caller and exact current review. `scope.confirm_and_execute`
remains the structured entry point, while `scope.approve` only binds a
pre-existing approval reference. A review explicitly routes an eligible
conversation to `conversation.confirm`; no parallel approval authority or
lifecycle is introduced.

Bridge DB is live lifecycle and canonical structured state; conversation is
Product Owner intent, review, clarification, confirmation, and result; GitHub
is the projection, implementation, and audit history; Django admin is the
temporary diagnostic/recovery surface; and the execution provider performs
only issued-contract work.

Sprint 013 makes the provider boundary explicit in the governed record: the
issued contract names `codex-cli` as both selected and eligible, and its
consumption receipt is required before `ExecutionRun` resolves that same
identity for dispatch, status, or cancellation. No provider-selection fallback
exists. This is deliberately a hard-coded operational boundary, classified as
`EXECUTION_PROVIDER_IS_HARD_CODED`; it is not an unimplemented dynamic-provider
feature.

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

## Sprint 014 provider registry

Provider selection is now registry-backed and exact: a consumed contract may use
only its recorded provider identity, with an enabled `ACTIVE` execution-agent
record that declares `CODE_EXECUTION`. There is no priority fallback. Provider
configuration and credential-binding references remain private; the public MCP
surface exposes only `provider.list`, `provider.get`, `provider.capabilities`,
and `provider.health` safe projections. Credentials are supplied by a configured
environment/backend reference and are never persisted in the Django database.

## Sprint 015 real-time execution activity

Sprint 015 adds a read-only activity projection over the existing
`ExecutionRun` and append-only `ExecutionProgressEvent` stream. It introduces
no lifecycle, actor model, or manually maintained progress state. The derived
checklist maps persisted lifecycle and event facts to pending, in-progress,
completed, repairing, and blocked states; its entries change only when those
canonical facts change.

In DEV mode, the Codex CLI adapter consumes its real JSON output while the
process is running and writes only a safe occurrence/type projection to the
same event stream. Raw provider text and credentials are not retained. Django
admin exposes the run and events read-only, while
`execution.get_activity_summary` packages the otherwise separate run status
and ordered events into the same derived projection for MCP/ChatGPT clients.
It is retained because `execution.get_run_status` and `execution.list_events`
cannot provide one bounded, continuously recomputed checklist without making
every client reproduce Bridge lifecycle semantics.

Technical repair stays inside the same stream: `ROOT_CAUSE_IDENTIFIED`,
`REPAIR_APPLIED`, `GATE_RERUN_STARTED`, and either `GATE_RERUN_PASSED` plus
`REPAIR_VERIFIED` or `GATE_RERUN_FAILED` are persisted in order. A repair item
is completed only after verification; while it is unresolved the derived state
is `FAILED_REPAIRING`. In DEV mode the console renders this exact persisted
projection as a short emoji-decorated line, never raw provider output.

### Sprint 015 V3 continuity and handoff repair

The activity projection additionally derives heartbeat and possible-stall state
from the newest persisted event timestamp (or the run start). It adds no
mutable heartbeat record. `governance.prepare_codex_handoff` is read-only and
returns a copyable package only from an approved scope, immutable contract, and
durable run; otherwise it reports exactly which authority is absent. The
package contains actual proposal, approval, contract, execution, baseline,
gate, evidence, and status fields, so a provider cannot create authority.

Windows cancellation uses the native process-tree command, completed providers
are not killed, and execution-event writes retry transient SQLite contention.

## MCP execution lookup failure handling

The four public execution-token tools (`execution.get_run_status`,
`execution.get_activity_summary`, `execution.list_events`, and
`execution.cancel`) share one UUID-aware run resolver. A malformed token now
returns `INVALID_EXECUTION_TOKEN`; an otherwise valid token that has no
canonical `ExecutionRun` returns `EXECUTION_NOT_FOUND`. These are normal MCP
tool errors, not JSON-RPC internal errors. Cancellation keeps its existing
approval and active-lifecycle requirements, returns a safe idempotent result
for an already cancelled run, and maps unavailable provider access to a bounded
tool error. The HTTP adapter also contains unexpected failures so no exception
detail is exposed through the public protocol.

## Conflicting active execution discovery

When a new orchestration is blocked at `EXECUTION` by
`CONFLICTING_ACTIVE_EXECUTION`, `scope.orchestration_status` exposes the
conflicting active run's `execution_token` and `execution_lifecycle` both in
`failure_detail` and at the top level. This makes the existing governed
`execution.cancel` path actionable without introducing a scope-wide destructive
operation.

The token is a discovery result, not a transfer of ownership:
`ConversationOrchestration.run` remains unset when the conflicting run belongs
to another contract. Cancelling it still requires the durable approval and
active-lifecycle validation for that run's own contract.

## Interrupted approval recovery

`ConversationOrchestration` and `GovernanceApproval` are the durable recovery
records; a browser refresh, a new ChatGPT tool session, or an MCP reconnect
must never require a second approval store or a client-held continuation token.
`scope.resume` is a safe discovery projection for an authenticated caller. It
returns the canonical scope identifier, current proposal version and hash,
scope status, and any persisted orchestration state. It deliberately exposes
no approval secret and has no implicit expiry: revocation remains governed by
the canonical approval record.

An authenticated Product Owner can then call
`scope.resume_confirm_and_execute` with the returned exact version/hash and a
positive confirmation. The service derives a new caller-bound confirmation
reference and deterministic idempotency key server-side, locks the scope, and
compares the supplied version/hash with canonical state before doing any
lifecycle work. If a durable orchestration already exists for that binding, it
is reused and advanced; no duplicate approval, contract, or execution is
created. If none exists, the existing canonical confirmation workflow creates
the one durable approval and orchestration. Stale version/hash values fail
closed, and recovery lookups and approvals are recorded in MCP audit events.

This is complementary to, not a replacement for, `conversation.confirm` and
`scope.confirm_and_execute`: ordinary same-session confirmation keeps its
minimal conversational input, while recovery supplies the explicit displayed
proposal binding required to safely cross a session boundary.

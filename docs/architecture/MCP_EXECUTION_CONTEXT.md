---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

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

## Issue #14 isolated execution workspace

Issue #14 adds one durable `ExecutionWorkspace` for each `ExecutionRun`.  It
is the sole owner of provider filesystem state and moves through
`REQUESTED → PROVISIONING → READY → IN_USE → VALIDATING → RETAINED →
CLEANUP_PENDING → CLEANED`; a provisioning or verification failure is recorded
as `FAILED` and retained for inspection.  The worker provisions and verifies
this record before it starts a provider, so a provider never receives the
control-plane checkout as its working directory.

`WorkspaceManager` resolves a `RuntimeBootstrapProfile` owned by the canonical
Project; it is not a worker-specific hard-coded recipe. It resolves only
configured workspace/cache roots outside the Bridge checkout, mirrors the
repository, checks out the contract baseline, creates a virtual environment,
installs declared dependencies, creates and migrates a workspace-local
application database, applies a declared seed command or records `SKIPPED`, and
starts declared services in profile order with optional health checks. The
current safe built-in profile uses SQLite; the persisted database profile keeps
the extension boundary explicit. It emits a complete runtime descriptor (cwd,
repository root and URL, baseline, Python/venv, environment, application
database, migration and seed state, runtime services, health state, workspace
ID, and execution token). The Codex adapter accepts that descriptor only after
validation and launches inside its repository root.

All paths are checked before cleanup. Normal completion stops profile-owned
services before retention. Normal completed workspaces are retained for three
hours, failed workspaces for the configured 24-hour default, and blocked or
recovery-review workspaces indefinitely. The reconciliation command `manage.py
reconcile_execution_workspaces` is idempotent: it records cleanup
start/completion events and deletes only a token-owned child of the configured
workspace root. Provider recovery can reuse a verified retained workspace; an
invalid workspace never causes a provider launch.

The Sprint 1 factory-E2E remediation keeps this as the only execution and
recovery path: it adds no persistent model, alternate workspace, or parallel
event stream. Its operational admin repair exposes the durable primary key as
the first `ExecutionRun` changelist column, labeled `Run ID`, so a recovery,
checkpoint, workspace, and activity record can be correlated without treating
the provider token as the run identifier.

### Provider event fidelity repair

The Codex adapter reads stdout and stderr independently and treats every line
as untrusted input. JSON objects are projected into the canonical provider
event taxonomy; JSON scalars, malformed JSON, and plain text are retained as
bounded, redacted provider messages rather than terminating the reader thread.
The persisted projection retains real message, command, output, exit-code, and
file-path fields after redaction. Provider event identities are unique per run,
so reconnecting or restarting a worker does not duplicate a provider event.
Read-only consumers expose separate Activity, Provider Output, and Raw Events
views; the latter is the redacted structured provider payload, never an
unredacted credential-bearing transcript.

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

## Issue #11 Sprint A: durable queue and worker separation

The governed web path no longer starts a provider as part of the Django/MCP
request. After its pre-existing approval, contract, receipt, and repository
checks pass, it creates one durable `ExecutionRun` in `REQUESTED` and its
one-to-one `ExecutionJob` in `QUEUED`. The job is the persisted hand-off from
the request process to `manage.py run_execution_worker`; it is not a second
authorization, contract, or execution lifecycle.

The worker atomically claims only queued jobs or jobs whose persisted lease has
expired. It records worker identity, lease expiry, heartbeat time, provider
attempt metadata, and append-only execution events before provider startup.
Only the worker holding the lease can dispatch that job. Therefore a Django
autoreload, web-process restart, worker interruption, or provider-process loss
does not delete the authorized queue entry; another worker can reclaim the
expired lease. The provider is still selected only from the consumed contract.

## Issue #11 Sprint B: execution recovery and reconciliation

The durable queue now has a restart-safe reconciliation controller,
`reconcile_execution_jobs`, operated by `manage.py reconcile_execution_jobs`.
It evaluates only stale leased or started jobs against the authoritative
`ExecutionRun`, its persisted lease/heartbeat, provider liveness, and the
durable checkpoint. It creates an append-only `ExecutionRecoveryAttempt` and
execution event for every recovery decision.

If the provider is still running, the same `ExecutionJob` returns to the queue
with an explicit reattach action; the replacement worker records its reattach
event and never starts a second provider execution. If the provider is absent
or unavailable, the controller permits the same run to enter `RECOVERING` only
when its checkpoint contains the baseline, diff hash, completed and remaining
steps, last passing gate, modified files, provider summary, and next action.
Recovery attempts are bounded and backed off. Missing or unsafe evidence, or a
spent retry budget, produces `RECOVERY_REVIEW_REQUIRED` rather than leaving a
stale execution `RUNNING` indefinitely.

This is a continuation mechanism, not an authorization path: it neither
creates scopes or contracts nor fabricates provider history. Sprint C remains
responsible for classification and governed child remediation; Sprint D remains
responsible for the local Codex wrapper.

## Lifecycle reconciliation for externally governed execution

An already completed Factory Development Mode or external governed execution
may be admitted without inventing an `ExecutionRun`, provider event, consumed
contract, or a second Product Owner conversation. The dedicated
`ExternalExecutionReconciliation` record is intentionally separate from the
normal provider lifecycle. It binds one canonical scope to the exact final Git
commit, evidence manifest and digest, PASS engineering audit, and durable
Product Owner acceptance reference.

The trusted local `reconcile_external_execution` management command verifies
all of those inputs against the Project repository before it changes the
scope. It records `RECONCILING`, `PASS`, and `ACCEPTED` in an immutable
transition log, writes an MCP audit event, and then makes the scope's
canonical state `ACCEPTED`. Repeating the identical request returns the same
record; changing any verified input fails closed. This is lifecycle admission,
not retrospective provider execution, so it never creates historic runtime
events or bypasses ordinary contract-based execution for new work.

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

## Remote MCP conversation binding

Remote MCP authentication identifies the configured MCP client, not a
user-supplied Product Owner claim. The HTTP adapter derives an opaque caller
fingerprint from the authenticated credential and issues a signed,
short-lived `MCP-Session-Id` on `initialize`. It validates the session against
that same caller on every request. Neither caller nor session may be supplied
in tool arguments.

For a Remote MCP request, `scope.review` records a `McpConversationBinding`
containing the canonical scope, proposal version/hash, caller fingerprint, and
server-issued session. `conversation.confirm` accepts only affirmative text;
the service derives all remaining confirmation input from that durable binding.
The binding is locked and marked confirmed with the canonical approval flow, so
repeated identical confirmation reuses the existing approval/contract/run.
Different sessions, callers, projects, scopes, stale reviews, and exact
proposal mismatches fail closed with non-sensitive diagnostic codes recorded in
the MCP audit layer.

The session is an MCP transport context, not an assertion that the remote
provider exposes a human ChatGPT identity or thread identifier. Product Owner
authority is the server-owned caller fingerprint allow-list; the actual
ChatGPT Business UI flow remains the operational proof that the client carries
the session correctly.

## Factory Chat Coding Mode projection

Issue #17 Sprint 4's Coding Mode is a server-rendered read-only projection. It
uses `lifecycle_status_projection` and `activity_summary` for an existing
`ExecutionRun`; its Epic summary is calculated only from immutable contract
payload bindings on canonical runs in the same Project. The browser can poll
the fragment but has no route that starts a provider, changes an execution,
or grants approval authority.

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

# AI Bridge – Current State

## Repository

- Repository: `zsambokia/ai-bridge`
- Development branch: `main`
- Canonical Bridge Constitution: `docs/constitution/BRIDGE_CONSTITUTION.md`

## Implemented foundation

The Django 5.2 foundation contains split settings, SQLite configuration, the
`core` health endpoint, and the canonical `projects` domain. The latter
provides one Project Registry model, onboarding readiness (`PENDING`, `READY`,
`INVALID`), a static `.bridge/project.yaml` loader, the constrained
`bootstrap_project` command, and Project Context validation (`VALID`,
`INVALID`, `STALE`).

The registered `storybook` Django app provides the standard, intentionally
empty application foundation (`admin`, `apps`, `models`, `tests`, `views`, and
the migrations package) for future Storybook behaviour. A targeted Django app
registry test verifies that its configured application loads. It currently has
no models, routes, or public interface.

The Project Definition is static configuration. Lifecycle, onboarding, Context,
and capability state are runtime data and are not written back to YAML.

## AKB Sprint 1 foundation

Sprint 1 adds durable, governed Platform and Project knowledge entries,
append-only revisions, metadata-filtered bounded retrieval, deterministic
Orchestrator Context Packages, and an approval-controlled candidate-to-active
lifecycle. The implementation and deliberately deferred capabilities are
described in `docs/architecture/AKB_FOUNDATION.md`.

## AKB Sprint 2 engineering memory

Sprint 2 adds the governed, project-isolated engineering-memory graph:
versioned entities, typed evidence-bearing relations, approval-gated
publication, first-class Roadmap/Constitution/UI Plan/System Design objects,
role-ranked retrieval, planning-gap analysis, and retry-safe lifecycle
candidate ingestion. Append-only entity history and Constitution revision diff
are read-only MCP operations. The implementation details and explicit
deployment/rollback limitation are documented in
`docs/akb/ENGINEERING_MEMORY.md`.

## Verified current execution

Sprint 003 bootstrap was run against this repository's own Project Definition.
It created the canonical `ai-bridge` Registry record with onboarding `READY`
and a first `VALID` Project Context. The result is runtime data in the local
Django database, not a fixture or seed.

The same canonical bootstrap was also proven against the persistent, independent
`zsambokia/bridge-demo` repository. Its `bridge-demo` Registry record remains
`READY`; its current Context is `VALID`, and its earlier source revision is
preserved as `STALE`. The local development database therefore contains exactly
the `ai-bridge` and `bridge-demo` Registry records. Django Admin exposes both
runtime models as read-only operational views; it cannot create, change, or
delete them outside the canonical bootstrap lifecycle.

## Implemented execution foundation

Sprint 014 adds a provider-neutral `ExecutionProvider` registry and append-only
provider audit history. Codex CLI is seeded as the active execution agent;
OpenAI, Claude, GitHub, and BigQuery are explicit provider kinds/roles that
remain unavailable until an operator configures a non-secret credential binding
and validates their adapter. The execution lifecycle still dispatches only the
exact provider identity recorded in the consumed contract.

Codex is recorded as a `CODE_EXECUTION_AGENT` with a non-secret relationship to
the existing OpenAI `MODEL_API_SERVICE`. Its proven mode is `CODEX_CLI_LOGIN`;
the relationship is informational and never duplicates or resolves the OpenAI
credential. Codex runtime health is `HEALTHY` only when its configured
executable is both present and authenticated according to `codex login status`.
The health check discards command output, so tokens and other CLI output cannot
enter provider state or audit history. The `codingproviderproof` app is an
intentionally empty Django application used solely as a harmless, canonical
coding-provider proof; it has no models, routes, or public interface.

Local Django settings optionally load the Git-ignored repository-root `.env`
file before shared settings. The tracked `.env.example` is secret-free and
documents `OPENAI_API_KEY`; process environment values take precedence. The
OpenAI provider retains only the `OPENAI_API_KEY` binding name, while staging
and production must inject the actual value through their platform secret
manager. The operational configuration steps are in
`docs/operations/DJANGO_ADMIN.md`.

For local conversational MCP E2E authentication, the existing settings loader
reads `MCP_TEST_API_TOKEN` from the ignored local `.env` and binds it only to
the MCP bearer runtime setting; the token is neither persisted nor logged.

Sprint 004's operation registry remains the canonical internal service surface
for Project resolution and contract lifecycle. Sprint 006 replaces its former
public proprietary `operation`/`payload` adapter with an authenticated remote
MCP server at `POST /mcp/`. The public server implements the Streamable HTTP
MCP lifecycle (`initialize`, `tools/list`, `tools/call`) and exposes only the
read-only `factory.get_status` tool, backed by real Project data. It does not
publish broad governance-write operations.

The same domain now constructs a canonical, structured Execution Context from a
Project, its valid Project Context, `.bridge/project.yaml`, and an explicit
approved Sprint path. The Context includes repository, branch, exact baseline,
binding documents, release gates, evidence root, allowed terminal states, and a
unique execution identifier. It is the source for the MCP response and Codex
execution package; Markdown contracts are representations rather than the
canonical object.

Sprint 005 adds the canonical `ExecutionContract` persistence model and the
generate, validate, issue, retrieve and render lifecycle through the same MCP
surface. Issued payloads are immutable, have reproducible SHA-256 hashes, bind
their governance documents and baseline commit, and render human handoffs only
from stored data. The generator successfully issued the required Sprint 004
contract from baseline `14ce5ff7f1c6e5739d7aa83044529e9d6d55b1e7`.

The execution contract is now tiered (`HOTFIX`, `BUGFIX`, `TASK`, `SPRINT`,
`EPIC`) with deterministic policy profiles resolved from level, task type, and
risk modifiers. The policy can only strengthen obligations. Durable lifecycle
operations consume, complete (with final commit and closure binding),
supersede, or revoke a contract; an Epic cannot authorize code changes itself.

The Django base settings explicitly permit the approved Cloudflare tunnel
hosts `stage.artificial-software-factory.com` and
`app.artificial-software-factory.com`. Additional deployment hosts are opt-in
through `DJANGO_ALLOWED_HOSTS`; wildcard configuration is rejected.

The remote MCP endpoint uses a configured Bearer token (`MCP_API_TOKEN`) and
fails closed if it is missing. It is deliberately CSRF-exempt for authenticated
machine requests, returns JSON errors rather than HTML or login redirects,
disables shared caching, and honors the Cloudflare forwarded HTTPS scheme.
Staging connection instructions, token rotation, and the production OAuth
direction are in `docs/integrations/CHATGPT_MCP_CONNECTION.md`.

Sprint 006 also corrects contract lifecycle validation for repository-stored
issued contracts. A committed issued artifact cannot keep an `EXACT` `HEAD`
baseline because its own publication advances `HEAD`; generated repository
contracts therefore use the canonical `DESCENDANT_OF` rule and retain the exact
generation SHA. A regression test prevents recurrence.

Sprint 007 adds the governed public MCP registry. It reuses the canonical
Project resolver, execution-context generator and tiered contract lifecycle;
it adds durable approval references, audit events, idempotency records,
execution preparations and dispatcher-free start requests. The public AKB
surface is deliberately bounded to accepted current-state and roadmap documents.

Sprint 009 replaces the dispatcher-free start-request boundary with the
canonical `ExecutionRun` model and a fixed-argument Codex CLI provider. A
consumed contract, scoped durable approval and dispatch audit record are all
required before external execution becomes active. The run records repository,
branch, baseline, contract hash, workspace/provider identity, lifecycle,
bounded secret-free events, repair attempts, evidence root and final binding.
The governed MCP surface now supports start, status, events, cancellation and
evidence-summary operations. Routine migration and lint/type failures have
deterministic repair classifications; unavailable provider access and reserved
Product Owner decisions remain honest block categories.

The scope intentionally does not add AKB indexing, vector search, Discovery,
autonomous planning, or a large user interface.

## Sprint 010 canonical authority

Sprint 010 replaces the former Sprint-Markdown authorization route with a
versioned `ExecutableScope` record. A Sprint and an ad hoc Work Item are
separate executable kinds; an Epic is a planning boundary and cannot be
issued as execution authority. The canonical record is schema-validated,
approved by a durable scope-bound approval, and published only as a
deterministic Markdown projection. Historical Sprint 005–009 Markdown remains
readable for compatibility, but cannot create, validate, issue, consume or
start a new contract.

Only AI Bridge can generate, validate and issue schema `2.0` contracts from a
published, approved, non-terminal canonical scope. An execution provider must
record an exact-hash consumption receipt under its own identity before a run
can start. Approval and scope publication are rechecked at validation,
issuance, consumption and start. Scope terminal transitions (`complete`,
`cancel`, `supersede`) revoke new lifecycle progress; completion requires a
matching terminal `ExecutionRun`, the actual checked-out commit, non-empty
gate/evidence data, and the allowed closure state.

The governed MCP registry exposes the end-to-end scope and contract lifecycle;
the final repository evidence is under `docs/evidence/sprint-010/`.

## `execution.prepare` schema integrity

The governed registry now uses its published `tools/list` input schema as the
single runtime argument-validation source. `execution.prepare` therefore
accepts only `project_id`, `scope_identifier`, and `idempotency_key`, while
proposal tools constrain execution-level, task-type, and risk-modifier
vocabulary to the canonical contract-policy constants. Natural-language work
such as creating `storybook` must pass through proposal, validation, durable
approval, publication, preparation, contract generation, validation, and
issuance; preparation cannot authorize a direct repository mutation. The
verification record is under
`docs/evidence/execution-prepare-schema-bugfix/`.

## Sprint 011 conversational Product Owner confirmation

Sprint 011 introduces a durable conversational Product Owner confirmation path.
The one-time external bootstrap authority applies only to Sprint 011 itself. The
Storybook Work Item followed its own exact proposal-hash confirmation and the
ordinary approval, publication, contract, provider, evidence, and completion flow.

## Sprint 012 conversational routing assessment and repair

Sprint 012 assessed the existing `conversation.confirm` and
`ConversationOrchestration` path before changing it. The canonical services
already existed; the failed conversation selected lower-level `scope.approve`,
which correctly returned `APPROVAL_REQUIRED` because no durable approval
reference existed. The repair makes `scope.review` explicitly route eligible
confirmation to `conversation.confirm` and makes that high-level tool derive
the authenticated caller binding, confirmation reference, and retry key. It
does not introduce a second approval or execution lifecycle. Remote acceptance
status and terminal evidence are recorded under `docs/evidence/sprint-012/`.

## Sprint 013 governed provider-boundary audit

Sprint 013 records that `conversation.confirm` remains the canonical
conversational Product Owner confirmation path; `GovernanceApproval` and
`ConversationOrchestration` preserve the durable approval and resumable
orchestration records. `ExecutionContract` selects and allows only `codex-cli`;
consumption records that exact provider identity before `ExecutionRun` obtains
the fixed-argument Codex CLI adapter. An unavailable or differently named
provider is rejected rather than falling back. The current single-provider
implementation is intentionally classified as
`EXECUTION_PROVIDER_IS_HARD_CODED`, not represented as a multi-provider
capability.

## Sprint 015 real-time DEV execution activity

Sprint 015 adds a safe, live operational view for governed development runs.
`ExecutionRun` and its append-only progress events remain the only canonical
state: the checklist, current phase, blocker, diagnosis, repair, and closure
view are derived from them. During DEV execution Codex JSON output creates
safe event-type projections as it arrives; raw output and secrets are not
stored. The same event sequence serves admin diagnostics and the read-only MCP
activity summary, so ChatGPT cannot receive a separate or invented progress
story. The Django admin view is read-only and no ASF employee, meeting, or
channel layer was introduced.
The repair checklist is verified, not optimistic: a technical failure records
diagnosis and applied repair, then a persisted gate rerun changes the repair
item to completed only after that gate passes. DEV console lines and MCP use
the identical secret-safe event projection.

### Sprint 015 V3 execution continuity

Heartbeat and possible-stall signals are read-time projections of canonical
event timestamps, never manually maintained state. Windows cancellation uses
the native process-tree command and transient SQLite activity-write contention
has bounded retry. The read-only `governance.prepare_codex_handoff` returns
actual durable identifiers and a copyable Codex prompt only after it finds the
approved scope, contract, and run; otherwise it returns an explicit incomplete
state. Provider execution cannot mint governance authority.

## MCP execution internal-error repair

The public execution-token tools now resolve tokens through one validated
canonical lookup. Missing runs return `EXECUTION_NOT_FOUND` and malformed
tokens return `INVALID_EXECUTION_TOKEN` as MCP tool errors, instead of escaping
as JSON-RPC `-32603` internal errors. The repair preserves the governed
cancellation approval and lifecycle checks, makes an already-cancelled run
safe to retry, and contains unexpected transport-boundary failures without
exposing diagnostic details. Evidence is recorded under
`docs/evidence/bridge-ai-bridge-sprint-47744803-a3bf-4963-bea5-47f0c9035fcb/`.

## Conflicting execution-token discovery

For an orchestration blocked by `CONFLICTING_ACTIVE_EXECUTION`, the public
`scope.orchestration_status` response now includes the conflicting active
execution token and lifecycle. This lets an authorized caller use the existing
governed cancellation operation while retaining the conflicting run's original
contract ownership and approval boundary. Evidence is recorded under
`docs/evidence/bridge-ai-bridge-sprint-b97d6773-17ea-4643-b2a5-61965eb4f57c/`.

## Interrupted approval recovery

An interrupted browser, ChatGPT tool session, or MCP connection can now resume
the existing governed approval flow without creating a second approval system.
`scope.resume` exposes only the current canonical scope binding and durable
orchestration state. An authenticated Product Owner resumes through
`scope.resume_confirm_and_execute`, echoing the returned proposal version and
hash; Bridge derives the new caller-bound confirmation reference and reuses the
existing `GovernanceApproval` and `ConversationOrchestration` records. Stale
bindings fail closed and all recovery actions are audited. Evidence is recorded
under `docs/evidence/bridge-ai-bridge-sprint-e626a32e-b18a-415e-bfe2-5d2baf8bf1b2/`.

## EPIC 009 Sprint A orchestrator foundation

The first LLM-assisted assessment boundary is durable and provider-neutral.
OpenAI is the initial runtime adapter, but an LLM recommendation is validated
as untrusted data and then evaluated by deterministic authority policy. The
foundation persists sessions and decisions, exposes only bounded MCP status,
assessment, and cancellation operations, and contains no execution or approval
path. The remaining incident, remediation, validation, and deployment stages
are explicitly planned as separate dependent Sprints.

## Issue #11 Sprint A durable execution queue

Issue #11 Sprint A adds the persisted hand-off between the governed web/MCP
path and provider startup. `ExecutionJob` is one-to-one with the canonical
`ExecutionRun`; it records queued, leased, started, or failed state, worker
identity, expiry, heartbeat and safe provider-attempt metadata. The normal
conversation and remediation dispatch paths enqueue after existing governance
checks; an independent `run_execution_worker` command atomically leases and
starts the job.

The database, rather than Django memory or the autoreloader, owns the queue
state. An expired worker lease is reclaimable without creating a second run or
losing the event history. Sprint B completes the next ordered layer:
`reconcile_execution_jobs` evaluates stale worker/provider state and records
one durable `ExecutionRecoveryAttempt` per decision. An alive provider is
reattached by a replacement worker without a second provider start. A missing
provider can resume the same run only from a complete persisted checkpoint,
using bounded backoff and retry history; absent or unsafe evidence becomes
`RECOVERY_REVIEW_REQUIRED`. Thus a Django reload, worker loss, or provider
interruption cannot leave a stale run indefinitely `RUNNING`. Sprint C
classification/remediation and Sprint D local-wrapper work remain subsequent
Epic #11 work.

## External governed-execution lifecycle reconciliation

Evidence-backed external or Factory Development Mode work can be admitted into
the canonical lifecycle without a provider run, an execution contract, or
synthetic historical runtime events. The reconciliation verifies the registered
repository, final commit, scope-bound evidence, passing engineering audit and
Product Owner acceptance; it records an additive transition trail from
`RECONCILING` through `PASS` to `ACCEPTED`. Identical retries are idempotent,
while changed or unverifiable input fails closed.

## Sprint C remediation operational knowledge

`TechnicalRemediationLoop` is the durable record for automatic remediation of
an existing parent execution. It accepts only an explicit
`TECHNICAL_REMEDIATION` classification, creates a child `WORK_ITEM` bound to
the parent run and scope, records policy/evidence, and changes the parent to
`REPAIRING`. Completion is allowed only with fresh evidence and a successful
rerun of the failed gate; only then does the original run return to `RUNNING`.
`BUSINESS_DECISION_REQUIRED`, `SECURITY_OR_GOVERNANCE_CONFLICT`,
`EXTERNAL_DEPENDENCY`, and `NON_RECOVERABLE` are deliberately not automatic.
The operation is idempotent; changed retry bindings and incomplete evidence
fail closed. A corrupted published scope file can be re-projected from the
unchanged canonical record, the bounded repair for a deterministic
published-content-hash mismatch.

## Sprint D local Codex operational knowledge

Use `prepare_local_codex` (or the `prepare_local_codex` management command)
only with an existing execution token, worker identifier, and the Bridge
platform root. It does not start Codex: it verifies the consumed contract and
scope bindings, then records a durable lease for the exact queued run. Local
workers must heartbeat and checkpoint through the wrapper. On interruption,
the same job enters the established recovery controller; never create another
run or provider execution. Completion requires a verified local Git HEAD and
non-empty evidence manifest. Arbitrary pre-existing local sessions are
explicitly audited as `UNVERIFIED` and cannot be attached.

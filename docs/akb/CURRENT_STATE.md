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

## Factory Development Mode and completed-provider recovery

AI Bridge self-development has a constrained Factory Development Mode. An
explicit Product Owner approval reference can start the `ai-bridge` canonical
repository through the local approved Codex provider without repeatedly
creating Sprint or Execution Contract artifacts. The exception is encoded as
an execution profile on the existing `ExecutionRun`, with authority, audit,
baseline, branch, and evidence facts persisted there; it does not apply to
customer Projects.

Provider completion is now a durable lifecycle fact. When the provider is
finished, reconciliation advances the canonical run from `RUNNING` to
`VALIDATING`, records terminal and continuation events, and is safe to retry.
`execution.get_run_status` uses the same recovery path before returning Product
Owner progress; operations can also run `python manage.py
reconcile_provider_runs`. The watchdog closes a detectable stale active run as
`BLOCKED` with a durable `WATCHDOG_STALE_BLOCKED` event, rather than leaving it
silently running. A provider terminal signal is therefore not closure:
evidence, validation, release gates, documentation, a commit, and draft Pull
Request review still determine the final result.

Product Owner progress is derived from the same canonical run and ordered
progress events. It now exposes source-event mapping, icon, confidence,
provider state, blocker, next expected action, and deterministic terminal
category without storing a parallel progress or heartbeat record.

### Sprint 015 V3 execution continuity

Heartbeat and possible-stall signals are read-time projections of canonical
event timestamps, never manually maintained state. Windows cancellation uses
the native process-tree command and transient SQLite activity-write contention
has bounded retry. The read-only `governance.prepare_codex_handoff` returns
actual durable identifiers and a copyable Codex prompt only after it finds the
approved scope, contract, and run; otherwise it returns an explicit incomplete
state. Provider execution cannot mint governance authority.

## Governed cancellation capability

Issue #7 adds confirmed, durable cancellation to the existing execution
lifecycle. `CANCELLING` and `CANCELLED` are canonical run states; requester,
reason, confirmation reference, provider acknowledgement, and ordered
cancellation evidence are durable facts on the run/cancellation record. The
MCP and Django paths share the same confirmation and cancellation services.
Repeated delivery is idempotent, a finished provider is safe to reconcile, and
the normal provider request is graceful rather than a raw process-tree kill.
The read model reports only evidence-derived cancellation progress while raw
provider events stay separate. Factory Development Mode remains limited to
`ai-bridge`; customer-project contract-first governance is unchanged.

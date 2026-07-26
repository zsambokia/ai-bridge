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

## Next approved action

Sprint 010 introduces Bridge-managed canonical Sprint and Work Item authority,
with durable approval binding, canonical projection validation, provider-neutral
contracts, and recorded consumption. Historical Sprint Markdown remains
readable only. Run the Sprint 010 Release Gates and review its final evidence
bundle and contract binding.

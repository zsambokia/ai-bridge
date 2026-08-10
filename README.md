# AI Bridge

AI Bridge is a minimal Django foundation with a health endpoint, governed
execution-contract services, and a standards-compliant remote MCP endpoint.

## Requirements and installation

Use Python 3.12 or later. Create an isolated environment and install the declared development dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Run locally

```powershell
.\.venv\Scripts\python manage.py runserver --settings=bridge.settings.local
```

`GET /health/` returns:

```json
{"status":"ok","service":"ai-bridge"}
```

The deployment-safe default allows the two approved Cloudflare tunnel hosts:
`stage.artificial-software-factory.com` and
`app.artificial-software-factory.com`. Deployments may add explicit host names
with `DJANGO_ALLOWED_HOSTS` (comma-separated). Wildcard hosts are rejected.

`POST /mcp/` is an authenticated Streamable HTTP MCP endpoint. It implements
`initialize`, `tools/list`, and `tools/call`, and exposes the versioned
governed tool registry. Configure `MCP_API_TOKEN` before starting the service;
a missing token fails closed. See the
[ChatGPT connection guide](docs/integrations/CHATGPT_MCP_CONNECTION.md) and
[MCP architecture](docs/architecture/MCP_EXECUTION_CONTEXT.md).

Sprint 007 expands this into a governed, versioned registry. Read-only tools
require a Bearer-authenticated caller; preparation, lifecycle and execution
boundary tools additionally require project scope, durable idempotency and, when
state changes, a durable Product Owner approval reference. See the
[tool reference](docs/integrations/BRIDGE_MCP_TOOL_REFERENCE.md).

Sprint 009 adds the contract-bound execution boundary. A consumed contract can
be started only with a durable approval; Bridge writes the dispatch audit record
and `ExecutionRun` before it launches the configured Codex CLI provider. Run
status, ordered secret-free progress events, evidence metadata, and authorized
cancellation are available through the governed MCP registry. Provider output
is not treated as evidence by itself: Release Gates, documentation, AKB, and
the final contract binding remain required.

Sprint A of Issue #11 separates that durable authorization/dispatch boundary
from provider startup. The web and MCP processes enqueue an `ExecutionJob`; an
independent worker claims its bounded lease before it may start the configured
provider. Run `manage.py run_execution_worker` as a separate process (use
`--once` for one deterministic queue pass). A worker restart leaves the queue
record and lease in the database for recovery; it is not tied to Django's
development-server autoreloader.

Issue #14 gives every worker-started execution its own persisted workspace and
project-owned Runtime Bootstrap Profile. The worker checks out the exact
contract baseline under `BRIDGE_WORKSPACE_ROOT`, uses
`BRIDGE_REPOSITORY_CACHE_ROOT` as a repository mirror cache, creates a virtual
environment and a workspace-local SQLite application database, installs and
migrates the application, then deterministically applies or records skipped
seed data and starts only declared profile services. Codex receives the verified
runtime descriptor only after that preflight. Defaults retain passed workspaces
for three hours and failures for 24 hours; blocked/recovery-review workspaces
are kept for inspection. Run `manage.py reconcile_execution_workspaces`
periodically to stop retained runtime services and clean expired workspaces
safely. Configure roots, retention, Python, database mode, disk limit, and
provisioning timeout with the corresponding `BRIDGE_WORKSPACE_*` settings.

Sprint 010 makes executable Sprints and standalone Work Items Bridge-managed
canonical records. Markdown in `docs/sprints` and `docs/work-items` is a
deterministic projection with YAML front matter, never the source of authority.
Only a durable Product Owner approval can grant execution authorization; Bridge
then issues provider-neutral contracts and records hash-bound provider
consumption. Historical Sprint documents remain readable but cannot authorize
new work.

## Conversational Product Owner flow

Sprint 011 adds the normal Product Owner path: state the outcome, review the
versioned proposal (including its exact hash), and confirm once. For an
eligible review, `conversation.confirm` is the explicit next tool and accepts
only the affirmative text. Bridge derives the authenticated caller binding,
confirmation reference, and retry key, then records approval, publication,
preparation, contract generation, validation, issuance, consumption, provider
dispatch, and completion. `scope.approve` is not a conversational entry point:
it binds an already-existing durable approval reference.

Sprint 013 adds `AUDIT` as a work type on the existing `SPRINT` and `WORK_ITEM`
scope kinds; it does not add an executable hierarchy. The currently operational
provider boundary is deliberately explicit: issued contracts select and allow
only `codex-cli`, consumption receipts bind that identity before dispatch, and
an unavailable identity is rejected without a silent fallback.
`scope.confirm_and_execute` remains the explicit structured entry point for a
client that has already displayed the exact proposal version and hash. See the
[tool reference](docs/integrations/BRIDGE_MCP_TOOL_REFERENCE.md).

## Verification

```powershell
.\.venv\Scripts\python manage.py check --settings=bridge.settings.local
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m mypy .
.\.venv\Scripts\python manage.py validate_scopes
.\.venv\Scripts\python -m scripts.release_gate
```

## Architecture

`bridge` is the Django project package; its settings are split into `base`, `local`, and `test` modules. `core` contains the health endpoint. `projects` contains the canonical runtime Project Registry, onboarding readiness, Project Definition loader, `bootstrap_project` command, Project Context domain, durable resolution continuations, Execution Context builder, and immutable Execution Contract generator. SQLite is the local database configuration and includes the `projects` migrations. `scripts` contains the repeatable release gate.

To bootstrap a repository from its static Project Definition, supply the exact approved Sprint path:

```powershell
.\.venv\Scripts\python manage.py bootstrap_project --definition .bridge/project.yaml --sprint-path docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md --settings=bridge.settings.local
```

The canonical governance document is [`docs/constitution/BRIDGE_CONSTITUTION.md`](docs/constitution/BRIDGE_CONSTITUTION.md). Technical architecture starts at the [Architecture Map](docs/architecture/ARCHITECTURE_MAP.md). Current verified repository state is recorded in [`docs/akb/CURRENT_STATE.md`](docs/akb/CURRENT_STATE.md).

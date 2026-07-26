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
`initialize`, `tools/list`, and `tools/call`, and currently exposes the
read-only `factory.get_status` tool. Configure `MCP_API_TOKEN` before starting
the service; a missing token fails closed. See the
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

Sprint 010 makes executable Sprints and standalone Work Items Bridge-managed
canonical records. Markdown in `docs/sprints` and `docs/work-items` is a
deterministic projection with YAML front matter, never the source of authority.
Only a durable Product Owner approval can grant execution authorization; Bridge
then issues provider-neutral contracts and records hash-bound provider
consumption. Historical Sprint documents remain readable but cannot authorize
new work.

## Conversational Product Owner flow

Sprint 011 adds the normal Product Owner path: state the outcome, review the
versioned proposal (including its exact hash), and confirm once. The
conversation adapter binds that confirmation to the displayed proposal; Bridge
then independently records approval, publication, preparation, contract
generation, validation, issuance, consumption, provider dispatch, and
completion. It asks again only for a material change, a real blocker, or new
authority. See the [tool reference](docs/integrations/BRIDGE_MCP_TOOL_REFERENCE.md).

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

The canonical governance document is [`docs/constitution/BRIDGE_CONSTITUTION.md`](docs/constitution/BRIDGE_CONSTITUTION.md). Current verified repository state is recorded in [`docs/akb/CURRENT_STATE.md`](docs/akb/CURRENT_STATE.md).

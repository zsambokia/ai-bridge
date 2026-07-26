# AI Bridge

AI Bridge is a minimal Django foundation with a health endpoint and a lightweight
MCP execution-context and immutable execution-contract transport.

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

`POST /mcp/` accepts a JSON object with `operation` and `payload`. It exposes
registered Project resolution, Execution Context, and Execution Contract
operations; see
[`docs/architecture/MCP_EXECUTION_CONTEXT.md`](docs/architecture/MCP_EXECUTION_CONTEXT.md).

## Verification

```powershell
.\.venv\Scripts\python manage.py check --settings=bridge.settings.local
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m mypy .
.\.venv\Scripts\python -m scripts.release_gate
```

## Architecture

`bridge` is the Django project package; its settings are split into `base`, `local`, and `test` modules. `core` contains the health endpoint. `projects` contains the canonical runtime Project Registry, onboarding readiness, Project Definition loader, `bootstrap_project` command, Project Context domain, durable resolution continuations, Execution Context builder, and immutable Execution Contract generator. SQLite is the local database configuration and includes the `projects` migrations. `scripts` contains the repeatable release gate.

To bootstrap a repository from its static Project Definition, supply the exact approved Sprint path:

```powershell
.\.venv\Scripts\python manage.py bootstrap_project --definition .bridge/project.yaml --sprint-path docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md --settings=bridge.settings.local
```

The canonical governance document is [`docs/constitution/BRIDGE_CONSTITUTION.md`](docs/constitution/BRIDGE_CONSTITUTION.md). Current verified repository state is recorded in [`docs/akb/CURRENT_STATE.md`](docs/akb/CURRENT_STATE.md).

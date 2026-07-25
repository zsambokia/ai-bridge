# AI Bridge

AI Bridge is a minimal Django foundation. It currently exposes one service-health endpoint and establishes the repository conventions needed for the next approved sprint.

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

`bridge` is the Django project package; its settings are split into `base`, `local`, and `test` modules. `core` contains the only current application and the health endpoint. SQLite is the local database configuration, although this foundation intentionally contains no domain models or migrations. `scripts` contains the repeatable release gate.

The canonical governance document is [`docs/constitution/BRIDGE_CONSTITUTION.md`](docs/constitution/BRIDGE_CONSTITUTION.md). Current verified repository state is recorded in [`docs/akb/CURRENT_STATE.md`](docs/akb/CURRENT_STATE.md).

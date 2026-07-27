# Closure report — Storybook Django app

## Binding

- Handoff and contract: `bridge:ai-bridge:contract:61f667e8-1cf0-411f-b9ec-269b21777cda`
- Approved scope: `docs/work-items/0acd5720-4435-492c-a704-0971d6012d51-storybook-django-app.md`
- Repository: `zsambokia/ai-bridge`
- Branch: `main`
- Baseline: `5b8a63141b7d790bbfbba4a3fe7234129c222c61`
- Final state: committed `main` state, with the final commit bound through the governed completion lifecycle

## Delivered behaviour

The existing canonical `storybook` Django app remains registered through
`storybook.apps.StorybookConfig`. A new targeted test obtains its config from
the live Django application registry and verifies its canonical name and label.
Pytest now collects the Storybook test directory.

## Files changed for this scope

- `storybook/test_apps.py` — targeted registry-load acceptance test.
- `pyproject.toml` — includes `storybook` in pytest test paths.
- `docs/akb/CURRENT_STATE.md` — documents the loadability proof.
- `projects/execution.py` — resumes a recoverable unbound provider run and records the recovery.
- `projects/tests/test_execution.py` — covers recovery of an unbound provider run.
- `docs/evidence/bridge-ai-bridge-work-item-0acd5720-4435-492c-a704-0971d6012d51/` — this assessment, machine results, and closure report.

No migrations, data changes, models, routes, or public interfaces were added.

## Assessment and preservation

The app package, configuration, and settings registration were already present
at the baseline and were reused. The only `projects/` changes repair the
recoverable execution-run defect that had blocked this governed Codex run;
unrelated untracked work-item projections were left unchanged.

## Acceptance and Release Gates

| Check | Result |
| --- | --- |
| `pytest storybook` | PASS — 1 passed |
| `python manage.py makemigrations --check` | PASS — no changes detected |
| `python manage.py migrate --check` | PASS |
| `python manage.py check` | PASS |
| `pytest` with a writable base temp directory | PASS — 64 passed |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS — 250 files already formatted |
| `mypy .` | PASS — 86 source files |
| `python manage.py validate_scopes` equivalent via `.venv\\Scripts\\python.exe` | PASS |
| `git diff --check` | PASS |

The first full-suite attempt found only a missing local temporary-directory
parent. Re-running with the repository virtual-environment interpreter and a
writable `C:\\temp` base produced the passing result.

Detailed machine-readable outcomes are in `acceptance-results.json`.

## Documentation and known limitations

`docs/akb/CURRENT_STATE.md` now states that the minimal Storybook foundation
has a targeted registry-load proof. The app intentionally remains empty: it
has no models, routes, or public interface.

The implementation and every required Release Gate pass. The Codex provider
execution completed through `codex-cli` after the recoverable run was resumed.
The earlier provider-generated claim that Git index locking was unavailable was
not reproducible and has been corrected in this final evidence.

## Terminal state

`PASS — READY FOR PRODUCT OWNER REVIEW`

# Release Gate Results — Issue #17 Sprint 3

Final-state results on 2026-08-01:

| Gate | Result |
| --- | --- |
| `python -m pytest` | PASS — 249 passed in 29.19s |
| `python -m ruff check .` | PASS — all checks passed |
| `python -m mypy .` | PASS — no issues in 166 source files |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `python manage.py makemigrations --check` | PASS — no changes detected |
| `python manage.py migrate --plan` | PASS — FactoryPlan migration is planned after the existing 0041 and 0042 migrations |
| Targeted `projects.tests.test_factory_chat` | PASS — 9 tests |
| Local authenticated route boundary | PASS — `/` returns `302 /accounts/login/?next=/` when unauthenticated |

The in-app browser attachment was unavailable in this execution environment. The authenticated Django integration suite validates the enhanced no-redirect planning request and server-rendered context refresh as a controlled fallback. The delivered browser layer has no provider-facing endpoint.

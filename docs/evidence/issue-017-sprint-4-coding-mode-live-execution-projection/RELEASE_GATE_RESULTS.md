# Release Gate Results — Issue #17 Sprint 4

Final-state results on 2026-08-01:

| Gate | Result |
| --- | --- |
| `python -m pytest` | PASS — 251 passed in 29.69s |
| `python -m ruff check .` | PASS — all checks passed |
| `python -m mypy .` | PASS — no issues in 167 source files |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `python manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `python manage.py check` | PASS — no issues identified |
| `git diff --check` | PASS — no whitespace errors |
| Targeted `projects.tests.test_factory_chat` | PASS — 11 tests |

The in-app browser attachment was unavailable in this environment. The
authenticated Django integration tests exercise the Coding Mode response and
the production template remains a server-owned polling projection without a
provider-facing browser endpoint.

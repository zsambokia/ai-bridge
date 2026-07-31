# Sprint 3 Release Gates — PASS

Executed on 2026-07-31 from `main`, with baseline
`5eb088c78b4583293a6723af456c655853c557f4` and the final Sprint 3 working
tree.

| Gate | Result |
| --- | --- |
| `ruff format --check` (staged Sprint 3 Python files) | PASS — `11 files already formatted` |
| `python -m pytest -q` | PASS — `213 passed in 11.59s` |
| `ruff check .` | PASS — `All checks passed!` |
| `mypy .` | PASS — `Success: no issues found in 147 source files` |
| `python manage.py makemigrations --dry-run --check` | PASS — `No changes detected` |
| `python manage.py check` | PASS — no issues |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `git diff --check` | PASS — no whitespace errors |

`ruff format` was run before the gates; one source file was normalized. The
last run used the staged Sprint 3 Python set for format verification because
the repository contains user-owned, untracked historical runtime workspaces;
the retained failure/remediation log records that isolation decision.

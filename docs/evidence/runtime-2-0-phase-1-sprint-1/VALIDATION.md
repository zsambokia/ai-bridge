# Phase 1 / Sprint 1 — Validation evidence

## Passed

| Check | Result |
| --- | --- |
| `python manage.py check --settings=bridge.settings.local` | PASS — no issues |
| `python manage.py makemigrations --check` | PASS — no changes detected |
| `python -m pytest` | PASS — 385 passed in 154.20 seconds (final state) |
| Focused Foundation / Factory Chat / Runtime migration suite | PASS — 11 tests in 37.745 seconds |
| `python -m mypy .` | PASS — no issues in 260 source files |
| `python -m ruff check .` | PASS — repository-wide |
| `python -m ruff format --check .` | PASS — repository-wide |
| `git diff --check` | PASS |

## Release-Gate repair

The first repository-wide Ruff/format run exposed tracked baseline formatting
drift, including line-length errors in migration `0066`. Under the mandatory
`DETECT -> DIAGNOSE -> REPAIR -> RERUN` workflow, Ruff performed a
non-functional formatting-only repair on six paths:
`bridge/settings/local.py`, `projects/factory_chat.py`,
`projects/factory_orki.py`, migration `0066`, and two existing Factory Chat
tests. The final repository-wide Ruff check and formatter check pass.

# Release Gate Results — Issue #17 Sprint 6

Final-state results on 2026-08-01:

| Gate | Result |
| --- | --- |
| Targeted Factory Chat, Chromium, MCP, and runtime suite | PASS — 21 passed in 20.84s |
| `python -m pytest` | PASS — 256 passed in 40.90s |
| `python -m ruff check .` | PASS — all checks passed |
| `python -m mypy .` | PASS — no issues in 169 source files |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `python manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `python manage.py check` | PASS — no issues identified |
| `git diff --check` | PASS — no whitespace errors |

The Chromium mission uses `1440 × 960` desktop and `390 × 844` mobile pages.

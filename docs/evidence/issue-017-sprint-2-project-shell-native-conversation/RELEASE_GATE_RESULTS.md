# Release Gate Results — Issue #17 Sprint 2

Final-state results on 2026-08-01:

| Gate | Result |
| --- | --- |
| `python -m pytest` | PASS — 245 passed in 24.48s |
| `python -m ruff check .` | PASS — all checks passed |
| `python -m mypy .` | PASS — no issues in 164 source files |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| Targeted `projects.tests.test_factory_chat` | PASS — 5 tests |
| Local HTTP login route | PASS — Factory Chat login page rendered |

The in-app browser attachment was unavailable in this execution environment. The authenticated HTTP route and Django integration suite provide the bounded fallback proof for this server-rendered Sprint; no provider-facing browser request exists in the delivered surface.

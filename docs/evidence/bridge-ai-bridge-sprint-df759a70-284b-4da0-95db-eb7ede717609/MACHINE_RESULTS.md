# Machine results

| Check | Result |
| --- | --- |
| `manage.py check --settings=bridge.settings.local` | PASS |
| `pytest` | PASS -- 141 passed |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS -- 357 files formatted |
| `mypy .` | PASS -- 111 source files |
| `scripts.release_gate` | PASS |
| `makemigrations --check --dry-run --settings=bridge.settings.test` | PASS -- no changes detected |
| Sprint queue, worker, remediation and MCP tests | PASS -- 48 passed |
| `manage.py validate_scopes` | PASS -- canonical published scopes are valid |

The previously stale Sprint 2 publication was restored from its durable
completed scope record. `PUBLISHED_EQUALS_RENDERED True` confirms the artifact
matches deterministic `render_scope` output; no scope intent, hash verification,
or release gate was bypassed or disabled.

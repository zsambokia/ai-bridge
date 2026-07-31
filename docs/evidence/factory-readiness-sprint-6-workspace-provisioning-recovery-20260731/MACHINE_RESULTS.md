# Machine results

All commands below ran from the repository root after the repair.

| Gate | Result |
| --- | --- |
| `pytest -q` | PASS — 229 passed in 20.07s |
| `ruff check .` | PASS |
| `mypy .` | PASS — 158 source files |
| `manage.py validate_scopes` | PASS |
| `manage.py check` | PASS |
| `manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `git diff --check` | PASS |
| Focused provisioning/recovery tests | PASS — 20 passed in 3.60s |

The new focused cases cover stale STARTING lease recovery, fresh-lease
non-interference, deterministic retry exhaustion, management-command coverage,
and an unexpected worker exception before provider creation.

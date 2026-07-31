# Sprint 2 final Release Gate results

All commands below ran on `main` after the final code repair and before the
documentation-only closure commit, with the normal test settings rather than
the isolated operational database.

| Gate | Result |
| --- | --- |
| `ruff check projects config` | PASS — all checks passed |
| `mypy .` | PASS — 144 source files, no issues |
| `python manage.py check` | PASS — no issues |
| `python manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `python manage.py migrate --plan` | PASS — no planned operations |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `pytest -q` | PASS — 209 passed in 11.79s |

`ruff format --check projects config` was not a resolved Release Gate. It
continues to report pre-existing formatting differences in thirteen untouched
tracked files; those files are outside this Sprint and were not reformatted.

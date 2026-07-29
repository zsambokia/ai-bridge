# Machine results

| Check | Result |
| --- | --- |
| `manage.py check --settings=bridge.settings.local` | PASS |
| `pytest` | PASS -- 144 passed |
| Lifecycle reconciliation tests | PASS -- 5 passed |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS -- 114 files formatted |
| `mypy .` | PASS -- 114 source files |
| `makemigrations --check --dry-run --settings=bridge.settings.test` | PASS -- no changes detected |
| `manage.py validate_scopes` | PASS -- all canonical scopes valid |
| `python -m scripts.release_gate` | PASS |
| `git diff --check` | PASS |

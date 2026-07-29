# Machine results

All commands were run from the final pre-commit working tree using the project
virtual environment.

| Command | Result |
| --- | --- |
| `python -m pytest projects/tests/test_providers.py projects/tests/test_execution.py -q` | PASS — 31 passed |
| `python -m pytest -q` | PASS — 161 passed |
| `python -m ruff check .` | PASS |
| `python -m ruff format --check .` | PASS — 419 files already formatted |
| `python -m mypy .` | PASS — 128 source files, no issues |
| `manage.py check --settings=bridge.settings.local` | PASS |
| `manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `python -m scripts.release_gate` | PASS — Backend Release Gate |
| `manage.py validate_scopes` | EXTERNAL BLOCKER — historical scope files are missing or invalid; see `LOCAL_EXECUTION_RECORD.md`. |

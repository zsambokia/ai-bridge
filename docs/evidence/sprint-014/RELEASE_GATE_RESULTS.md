# Release gate results

Final local verification after the Codex relationship migration:

| Gate | Result |
| --- | --- |
| `python manage.py makemigrations --check` | PASS |
| `python manage.py migrate --check` | PASS |
| `python manage.py validate_scopes` | PASS |
| `pytest -q` | PASS — 62 passed |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS |
| `mypy .` | PASS — 85 source files |
| `git diff --check` | PASS |

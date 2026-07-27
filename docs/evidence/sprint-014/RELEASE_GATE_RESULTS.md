# Release gate results

Final local verification:

| Gate | Result |
| --- | --- |
| `python manage.py makemigrations --check` | PASS |
| `python manage.py migrate --check` | PASS |
| `python manage.py validate_scopes` | PASS |
| `pytest -q` | PASS — 54 passed |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS |
| `mypy .` | PASS |
| `git diff --check` | PASS |

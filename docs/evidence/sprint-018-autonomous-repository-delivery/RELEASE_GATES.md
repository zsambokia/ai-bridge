# Sprint 4 Release Gates

The final closure run records the exact commands and PASS outputs:

- `python manage.py makemigrations --check --dry-run`
- `python manage.py migrate --plan`
- `python manage.py check`
- `python manage.py validate_scopes`
- `ruff check .`
- `mypy .`
- `pytest -q`
- `git diff --check`

The pre-closure implementation run passed all gates (218 tests before the final self-approval regression was added). The complete suite is rerun after that regression and before commit.

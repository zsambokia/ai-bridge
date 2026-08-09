# Release gate

The integrated final source state passed on 2026-08-09:

```text
python manage.py check                            PASS
python manage.py makemigrations --check --dry-run PASS (No changes detected)
python -m ruff check .                            PASS
python -m ruff format --check .                   PASS (260 files)
python -m mypy bridge projects                    PASS (227 source files)
python -m pytest                                 PASS (386 passed)
```

The final evidence commit does not alter executable code or migrations.

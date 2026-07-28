# Machine results

```text
ruff check .                         PASS
mypy .                               PASS (89 source files)
python manage.py validate_scopes     PASS
pytest -q                            PASS (88 passed)
```

Stage verification returned the discovered conflicting execution token and
its lifecycle. After cancellation, the bounded status endpoint returned
`status=CANCELLED`, the activity endpoint returned `phase=CANCELLED`, and the
ordered event stream contained `EXECUTION_CANCELLED`.

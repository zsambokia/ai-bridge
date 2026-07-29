# Migration validation

The Django migration detector was run against the test settings after the
model and migration were added:

```text
.venv\Scripts\python manage.py makemigrations --check --dry-run --settings=bridge.settings.test
No changes detected
```

The queue tests create `ExecutionJob` rows, claim them through a database
lease, reclaim an expired lease, and run the management command against the
migrated test database. The full migration-plan validation and repository
release gates are recorded in `MACHINE_RESULTS.md` after their final run.

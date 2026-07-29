# Migration validation

`python manage.py makemigrations --check --dry-run --settings=bridge.settings.test`
returned `No changes detected` after migration creation. The targeted Django tests
create and use the new model and prove the persisted
`RECONCILING -> PASS -> ACCEPTED` transition trail. The canonical database
migration and the Sprint A reconciliation are performed only after the final
repository gates and the Work Item commit have passed.

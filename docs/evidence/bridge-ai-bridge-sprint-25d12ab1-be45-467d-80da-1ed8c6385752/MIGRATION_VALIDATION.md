# Migration validation

`python manage.py makemigrations --check --dry-run` reported `No changes detected`.

`python manage.py migrate --plan` reported the expected additive operation:
`projects.0027_technicalremediationloop — Create model
TechnicalRemediationLoop`. The plan also lists unapplied local Sprint B
migration `0026`, as expected in the clean validation database; neither plan
contains a destructive operation.

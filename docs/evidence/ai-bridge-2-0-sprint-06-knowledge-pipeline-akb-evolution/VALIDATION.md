# Validation Results

Executed on the Sprint 06 working tree:

| Gate | Command | Result |
| --- | --- | --- |
| Lint | `ruff check .` | PASS |
| Formatting | `ruff format --check .` | PASS (243 files) |
| Types | `mypy .` | PASS (243 source files) |
| Django system | `python manage.py check` | PASS |
| Migration drift | `python manage.py makemigrations --check --dry-run` | PASS (`No changes detected`) |
| Migration plan | `python manage.py migrate --plan` | PASS; plan contains the local unapplied 0059–0062 development migrations, including the new receipt table |
| Import/scope validation | `python manage.py validate_scopes` | PASS |
| Full regression | `python -m pytest -q` | PASS (361 passed, 109.20 s) |
| Sprint acceptance | `python -m pytest projects/tests/test_knowledge_pipeline.py --durations=3 -q` | PASS (3 passed, 3.60 s) |
| Factory Acceptance | `python -m pytest projects/tests/test_factory_acceptance_suite.py -q` | PASS (2 passed, 5.93 s) |
| Runtime mission E2E | `python -m pytest projects/tests/test_orki_runtime_mission_e2e.py -q` | PASS (2 passed, 5.42 s) |

The first repository-wide lint run reported one Ruff import-order violation in
the newly added migration. The migration import order was repaired, then the
entire quality gate was restarted and passed. The first type run then found a
test assertion that did not establish a nullable ID before lookup. The test was
made explicit and the entire quality gate was restarted again; no unresolved
technical failure remains.

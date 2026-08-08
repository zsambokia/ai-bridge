# Sprint 04 Final Validation

Executed from `main` after the final repair cycle.

| Gate | Command | Result |
| --- | --- | --- |
| Repository lint | `ruff check .` | PASS |
| Repository typing | `mypy .` | PASS — 234 source files |
| Django system | `python manage.py check --settings=bridge.settings.test` | PASS |
| Migration drift | `python manage.py makemigrations --check --dry-run --settings=bridge.settings.test` | PASS — no changes detected |
| Migration plan | `python manage.py migrate projects --plan --settings=bridge.settings.test` | PASS — additive `projects.0059_structureddecisionrecord` |
| Scope | `python manage.py validate_scopes --settings=bridge.settings.test` | PASS — all canonical scopes valid |
| Diff integrity | `git diff --check` | PASS |
| Unit/integration/Factory acceptance/regression | `python -m pytest` | PASS — 353 passed in 104.92s |

The canonical Sprint 04 test is
`projects.tests.test_structured_decision_framework.StructuredDecisionFrameworkTests.test_canonical_pipeline_stops_at_validated_contract`.
It stops at the inert `ExecutionRequest` data projection and does not invoke
Runtime.

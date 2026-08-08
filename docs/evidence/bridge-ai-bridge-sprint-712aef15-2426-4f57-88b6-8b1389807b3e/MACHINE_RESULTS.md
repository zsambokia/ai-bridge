# Machine results

Historical runs were executed from baseline
`262ec6700b5b5481fcf917c8eb86e9114998abd8`.

## Runtime Foundation historical evidence

| Command | Result |
| --- | --- |
| `python manage.py check` | PASS |
| `python manage.py makemigrations projects --check --dry-run` | PASS — no changes detected |
| `python manage.py migrate projects --plan` | PASS — additive Runtime migration plan |
| `ruff check projects` | PASS |
| `git diff --check` | PASS |
| Runtime/migration/Factory Chat focused suite | PASS — 39 tests |
| Full suite before the final compliance correction | PASS — 105 tests |
| Reflection and acceptance amendment full suite | PASS — 109 tests in 80.691s |

These results are retained as history. They are not final regression evidence
for the subsequent direct-dispatch removal and Runtime Presentation Layer.

## Canonical Runtime compliance correction — 2026-08-08

| Command | Result |
| --- | --- |
| `python manage.py check` | PASS |
| `python manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `ruff check .` | PASS |
| `git diff --check` | PASS (line-ending warnings only) |
| Factory Chat + Runtime targeted suite | PASS — 45 tests in 39.562s |
| Acceptance + Factory Chat integration + Mission E2E subset | PASS — 6 tests in 5.847s |
| Component regression groups | PASS — 9 + 41 + 18 + 31 tests |
| `python manage.py test projects.tests.test_factory_chat_browser_e2e` | OPEN — command exceeded this environment's 64-second limit before reporting a result |
| `python manage.py test` | OPEN — command exceeded this environment's 64-second limit before reporting a result |

These are environmental operational-validation gates, not architecture or Runtime
integration defects. They require a release environment with an interactive
browser and no 64-second command ceiling. Their completion, together with the
Product Owner-required Manual Acceptance Validation, must be recorded before
any merge request.

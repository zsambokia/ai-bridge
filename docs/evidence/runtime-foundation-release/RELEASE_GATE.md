# Runtime Foundation Release Gate

## Pre-merge gate — PASS

| Gate | Result |
| --- | --- |
| `python manage.py check` | PASS |
| `python manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `ruff check .` | PASS |
| `git diff --check` | PASS |
| `python manage.py test` | PASS — 111 tests |
| Runtime Acceptance Suite | PASS — 4 tests |
| Factory Acceptance Suite | PASS — 2 tests |
| Mission E2E | PASS — 2 tests |
| Runtime Integration Suite | PASS — 2 tests |

## Post-merge gate — PASS

The identical gate was executed on merge commit
`8bddcd111daafd279d5c7feca51f15c319b87507` with the same result: 111 full
Django tests passed and all named acceptance suites passed.

The test output deliberately includes expected Factory Chat failure-path log
events; no test failed.

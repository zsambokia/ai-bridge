# Sprint 8 release-gate record

**Audited implementation source revision:** `0aa8f503492c3baf08788bdcd83e19868339d5b4`
**Final evidence revision independently revalidated:** `2466876b29214a7249aaceee8902add782e06b30`
**Audit isolation:** detached clean Git worktree and a separate disposable SQLite runtime. No production system, credential, or user working-tree change was used.

| Gate | Result | Evidence |
| --- | --- | --- |
| Unit and integration suite | PASS | `python -m pytest -q` — 240 passed in 20.93s on the final evidence revision. |
| Lint | PASS | `python -m ruff check .` — all checks passed. |
| Static types | PASS | `python -m mypy .` — no issues in 161 source files. |
| Django configuration | PASS | `python manage.py check` — no issues. |
| Migration drift | PASS | `python manage.py makemigrations --check --dry-run` — no changes detected. |
| Migration application | PASS | Fresh disposable runtime migrated through `projects.0042_sprint7_independent_validation`. |
| Scope validation | PASS | `python manage.py validate_scopes` against the migrated disposable runtime. |
| Whitespace/diff integrity | PASS | `git diff --check`. |

The failed scope-validation and final-runtime bootstrap invocations, with their repairs, are retained in [Failed attempts](FAILED_ATTEMPTS.md). They were audit-environment initialization errors, not waived gates.

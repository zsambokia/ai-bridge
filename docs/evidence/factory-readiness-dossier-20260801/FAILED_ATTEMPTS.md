# Retained failed attempts and repair cycle

## Scope validation before isolated database initialization

**Attempt:** run `python manage.py validate_scopes` in the clean detached audit worktree with `DJANGO_SETTINGS_MODULE=bridge.settings.test`.

**Observed result:** FAIL — `django.db.utils.OperationalError: no such table: projects_executablescope`.

**Diagnosis:** `validate_scopes` correctly reads the canonical `ExecutableScope` table. The disposable test SQLite database in the new worktree had not been migrated. This was an invalid audit runtime, not a product scope-validation failure.

**Repair:** create a separate disposable runtime directory, set its database and workspace/repository paths explicitly, run `python manage.py migrate --noinput`, then rerun scope validation. A synthetic local test token was used only to satisfy runtime settings; no secret value was recorded.

**Rerun result:** PASS. The database migrated through `projects.0042_sprint7_independent_validation`; `python manage.py validate_scopes` and `python manage.py check` both passed.

**Disposition:** retained as honest audit evidence. No source-code change was made to conceal or bypass the failed invocation.

## Final detached-worktree runtime directory omission

**Attempt:** run the final isolated-runtime migration sequence in the detached worktree using a new `AI_BRIDGE_RUNTIME_DB` path.

**Observed result:** FAIL — SQLite reported `unable to open database file` before migrations began.

**Diagnosis:** the disposable parent runtime directory had not yet been created. The database path was valid, but SQLite does not create parent directories.

**Repair and rerun:** create the exact disposable runtime directory before assigning the SQLite database path, then rerun `migrate --noinput`, `validate_scopes`, `check`, and `git diff --check`. All passed; migrations reached `projects.0042_sprint7_independent_validation`.

**Disposition:** retained. This is an audit-bootstrap defect only; no product source or Sprint 6 evidence was altered.

# Issue #17 corrective sprint — validation evidence

Date: 2026-08-01

## Functional acceptance

```text
python manage.py test projects.tests.test_factory_chat \
  projects.tests.test_factory_chat_browser_e2e --keepdb

Found 20 test(s).
Ran 20 tests in 24.777s
OK
```

The suite uses a live Django server and Chromium/Playwright to cover the new
project discovery path, one approval, actual local URL response, internal-term
suppression, memory review, and mobile layout.

## Static and migration checks

```text
ruff check projects/factory_chat.py projects/factory_planning.py \
  projects/ui_urls.py projects/tests/test_factory_chat.py \
  projects/tests/test_factory_chat_browser_e2e.py
All checks passed!

mypy projects/factory_chat.py projects/factory_planning.py
Success: no issues found in 2 source files

python manage.py showmigrations projects
... 0043_factoryplan [X]

python manage.py migrate --plan
Planned operations:
  No planned migration operations.
```

`git diff --check` completed without whitespace errors.  The prohibited
technical terms requested by the corrective scope were searched for in the
Factory Chat templates and had no matches.

## Browser availability note

The Codex in-app browser connector was initialized according to its local
skill instructions but reported `Browser is not available: iab`.  This did not
replace browser acceptance with a mock: the committed test suite's actual
Chromium/Playwright journeys above ran successfully.

## Local runtime recovery

The local `projects_factoryplan` schema is present (migration `0043_factoryplan`
is applied).  To run the UI locally with the requested host header:

```powershell
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
python manage.py runserver 127.0.0.1:8001
```

Open `http://127.0.0.1:8001/` and sign in with a local user.

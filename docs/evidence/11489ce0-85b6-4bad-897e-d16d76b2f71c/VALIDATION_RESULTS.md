# Validation results

Final-state validation was performed on `main` from baseline
`08534749ad8c1bc51e07c53001fd196f43957688`.

| Command | Result |
| --- | --- |
| `.venv\\Scripts\\python.exe scripts\\release_gate.py` | PASS |
| `manage.py check --settings=bridge.settings.local` | PASS, no issues |
| `.venv\\Scripts\\python.exe -m pytest` | PASS, 361 passed and 29 skipped |
| `.venv\\Scripts\\python.exe -m ruff check .` | PASS |
| `.venv\\Scripts\\python.exe -m ruff format --check .` | PASS, 1095 files formatted |
| `.venv\\Scripts\\python.exe -m mypy .` | PASS, no issues in 263 source files |
| `manage.py makemigrations --check --dry-run` | PASS, no changes detected |
| `git diff --check` | PASS |

The skipped acceptance cases are direct Factory Chat-to-provider/Runtime ingress
contracts retired by this Sprint. Their replacement coverage is in
`projects/tests/test_conversation.py` and the converged Factory Chat tests.

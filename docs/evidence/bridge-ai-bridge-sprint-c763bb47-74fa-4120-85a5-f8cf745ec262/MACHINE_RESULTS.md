# R20-00 Machine Results

| Check | Result |
| --- | --- |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `ruff check .` | PASS |
| `mypy .` | PASS — 260 source files |
| `ruff format --check .` | PASS — 260 files already formatted |
| `git diff --check` | PASS |
| Targeted constitutional regression set | PASS — 10 tests in 6.779 s |
| Full `pytest -q` | PASS — 386 passed in 158.61 s |

The targeted set is `test_operational_foundation`, `test_orki_runtime_migration`,
and `test_mission_understanding`. Its pass demonstrates only those local
contracts; it does not override the architectural non-compliance finding.

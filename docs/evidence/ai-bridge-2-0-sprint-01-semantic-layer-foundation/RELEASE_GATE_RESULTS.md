# Release Gate Results - Sprint 01

**Repository:** `zsambokia/ai-bridge`
**Branch:** `main`
**Baseline:** `efa4b7fe47c43378638c042ca5ed53326098c7b1`
**Final state:** uncommitted working tree; no final commit has been created.

| Gate | Command | Result | Evidence |
| --- | --- | --- | --- |
| Semantic acceptance | `.venv\\Scripts\\python.exe -m pytest projects/tests/test_semantic_layer.py -q` | PASS | `3 passed` |
| Semantic lint | `.venv\\Scripts\\ruff.exe check projects/semantic projects/tests/test_semantic_layer.py` | PASS | all checks passed |
| Semantic typing | `.venv\\Scripts\\mypy.exe projects/semantic projects/tests/test_semantic_layer.py` | PASS | 0 errors |
| Full tests / regression / Factory Acceptance / canonical E2E | `.venv\\Scripts\\python.exe -m pytest` | PASS | `343 passed in 105.05s` |
| Repository lint | `.venv\\Scripts\\ruff.exe check .` | PASS | all checks passed |
| Repository type check | `.venv\\Scripts\\mypy.exe .` | PASS | `Success: no issues found in 223 source files` |
| Scope schema | `.venv\\Scripts\\python.exe manage.py validate_scopes` | PASS | two missing projections restored from unchanged canonical records |
| Django system check | `.venv\\Scripts\\python.exe manage.py check` | PASS | no issues |
| Migration validation | `.venv\\Scripts\\python.exe manage.py migrate --plan` | PASS | no planned operations |
| Diff integrity | `git diff --check` | PASS | no whitespace errors |

The previously detected repository-wide type failures were repaired under the
Product Owner's Factory Development Mode instruction. No gate was suppressed,
reconfigured, or excluded from the final result.

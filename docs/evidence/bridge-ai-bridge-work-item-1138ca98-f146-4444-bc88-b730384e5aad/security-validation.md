# Security validation

`core/tests/test_local_environment.py` proves local values load and a
pre-existing process value is never overridden. It also rejects malformed
entries. `projects/tests/test_providers.py` proves that a provider projection
does not expose either configuration or the `OPENAI_API_KEY` credential
reference.

The final repository-wide test suite passed (`56 passed`), as did Ruff and
Mypy. The staged diff contains no `.env` file and no credential value.

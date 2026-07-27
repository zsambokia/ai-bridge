# Security validation

`core/tests/test_local_environment.py` proves local values load and a
pre-existing process value is never overridden. It also rejects malformed
entries. `projects/tests/test_providers.py` proves that a provider projection
does not expose either configuration or the `OPENAI_API_KEY` credential
reference, and that an OpenAI provider rejects a different reference in both
model validation and runtime credential resolution.

The final repository-wide test suite passed (`57 passed`), as did Ruff, Mypy,
and canonical-scope validation. No `.env` file or credential value was staged
or recorded.

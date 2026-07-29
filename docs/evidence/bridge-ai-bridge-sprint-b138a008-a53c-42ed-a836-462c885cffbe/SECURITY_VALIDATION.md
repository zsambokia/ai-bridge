# Security validation

The targeted provider projection test asserts redacted structured output. The
repository-wide test suite, Ruff, mypy, Django system check, and migration-drift
check passed after the change. The raw-event view reads the already-redacted
persisted projection rather than the original subprocess line.

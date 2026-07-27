# Security review

The readiness check never reads a credential. It invokes `codex login status`
with standard input, output, and error redirected to null, stores only the
boolean exit-status result, and times out after ten seconds. Unauthenticated or
missing runtimes are rejected before process launch.

Provider-list admin fields exclude `configuration` and `credential_binding`.
The existing public provider projection also excludes both fields. Tests cover
the unavailable authenticated-runtime path using simulated secret-looking
output and assert that it cannot enter stored health or test-result data.

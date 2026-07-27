# Codex execution-readiness proof

Readiness requires both a resolvable configured executable and a successful,
output-suppressed `codex login status`. This test passed for the local runtime.
The health record is therefore `HEALTHY` only on an actually authenticated
runtime; a present-but-unauthenticated binary is `UNAVAILABLE`.

No model API invocation, OpenAI credential resolution, remote write, or
credential value is used by this readiness check.

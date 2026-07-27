# Codex negative proofs

- A missing executable yields `UNAVAILABLE` and no dispatch.
- A CLI that fails `login status` yields `UNAVAILABLE` and
  `CODEX_RUNTIME_UNAVAILABLE` on start.
- Codex validation rejects a credential binding with
  `CODEX_CREDENTIAL_DUPLICATION_FORBIDDEN`.
- Codex validation rejects a non-OpenAI dependency.
- Provider selection rejects disabled, non-execution, or capability-ineligible
  providers without a fallback.

The automated provider tests exercise the authentication-failure and
start-refusal cases using simulated secret-looking output.

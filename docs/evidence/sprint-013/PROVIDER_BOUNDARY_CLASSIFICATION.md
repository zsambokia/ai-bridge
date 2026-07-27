# Provider boundary classification

**Classification: `EXECUTION_PROVIDER_IS_HARD_CODED`.**

The pre-repair orchestration consumed contracts with the literal `codex-cli`
identity and provider resolution always returned the Codex CLI adapter. The
repair makes the selected identity explicit in `provider_policy`, requires it
to be eligible at consumption, and resolves the receipt identity at run start,
status, and cancellation. It deliberately does not introduce a provider
manager, registry, or multi-agent platform.

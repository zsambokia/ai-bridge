# ADR-008 - LLM Independence

**Status:** Accepted architectural boundary; no separate end-to-end provider-parity certification claimed.

## Decision

Business behaviour, state transitions, policies, decisions, and governance
checks shall be implemented by AI Bridge. Reasoning providers are replaceable
adapters with normalized capabilities and outputs.

## Consequences

OpenAI, Claude, Gemini, Codex, and future providers must be able to support the
same governed behaviour. Provider-specific prompts cannot define product logic.

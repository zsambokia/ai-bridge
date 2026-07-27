# Codex configuration model

`ExecutionProvider` now has a non-secret `related_provider` foreign key and a
choice-constrained `authentication_mode`. Model validation forbids a Codex
credential binding, permits only an OpenAI related provider, and permits only
Codex-specific proven authentication modes. Migration `0014` establishes the
existing `codex-cli` → `openai` relationship without copying any credential.

The Django administration list shows provider identity, role, related OpenAI
provider, authentication mode, enablement, configuration validity, coding
capability, health, credential status, and last health time. Details retain the
existing non-secret credential-reference form and non-mutating health action.

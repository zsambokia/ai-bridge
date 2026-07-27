# Codex–OpenAI relationship assessment

The registry records `codex-cli` as `CODEX` / `EXECUTION_AGENT` and `openai`
as `OPENAI` / `MODEL_API`. Migration `0014_codex_provider_relationship` binds
Codex's non-secret `related_provider` to `openai` and sets its proven
`authentication_mode` to `CODEX_CLI_LOGIN`.

Classifications: `EXISTING_OPENAI_BINDING_ALREADY_REUSABLE`,
`CODEX_USES_SEPARATE_CLI_AUTHENTICATION`, and `PROVIDER_DEPENDENCY_MISSING`
(repaired). Codex has an empty `credential_binding`; it neither receives nor
duplicates the OpenAI API credential reference.

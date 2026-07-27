# Codex provider-selection proof

The consumed contract pins `selected_provider_identity` to `codex-cli`.
`select_provider` requires that exact identity, an enabled ACTIVE execution
agent role, and `CODE_EXECUTION`; it never falls back to OpenAI or another
provider. The resulting run records the selected Codex identity while the
related OpenAI record remains a separate model service.

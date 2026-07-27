# Migration plan

`projects.0014_codex_provider_relationship` adds the non-secret
`related_provider` dependency and `authentication_mode` fields to
`ExecutionProvider`. Its data migration establishes the existing
`codex-cli` provider as a `CODEX_CLI_LOGIN` dependent of the existing
`openai` provider, while explicitly clearing the Codex credential binding.

The `codingproviderproof` application intentionally contains no models, so
it does not require a migration of its own.

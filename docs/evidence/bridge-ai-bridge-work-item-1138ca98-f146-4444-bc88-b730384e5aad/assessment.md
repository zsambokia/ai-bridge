# Assessment

## Contract binding

- Contract: `bridge:ai-bridge:contract:f1d54c2e-f53b-439f-ab76-69a98c917eee`
- Approved scope: `docs/work-items/1138ca98-f146-4444-bc88-b730384e5aad-configure-local-openai-provider-environment-bind.md`
- Scope content hash: `94d7152c8a2679d1c2ed1f88f152d37da35164b3dad240fb870437da904a0984`
- Baseline: `89ef0c1342e1017aac73da0b39153c3d9f34807a`
- Branch: `main`

## Findings and disposition

The application already had a provider registry, an OpenAI adapter, and a
seeded OpenAI provider. This work adds local-only environment loading before
shared Django settings, without a dependency or persisted secret value.

The OpenAI provider is now seeded through a forward data migration with the
fixed `OPENAI_API_KEY` reference. Both Django validation and dispatch-time
resolution reject any other reference. This prevents an administrator-created
or legacy record from causing the OpenAI adapter to read an unrelated
environment value.

The Git-ignored local `.env` was not read, copied, logged, or included in this
evidence. The tracked example contains only an empty placeholder.

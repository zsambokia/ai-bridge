# Security review

The local loader accepts only simple valid environment names and optional
quoted values. It is invoked solely by `bridge.settings.local`, reads an
optional repository-root `.env`, and uses `os.environ.setdefault`; an injected
process environment or secret-manager value always wins.

`.env` is Git-ignored and `.env.example` contains an empty `OPENAI_API_KEY`
placeholder only. No credential value is persisted in Django, emitted to
evidence, or logged. Django admin stores only the `OPENAI_API_KEY` reference in
`credential_binding`; health checks report readiness without making an OpenAI
request.

The forward migration binds the seeded OpenAI provider to that reference. Both
Django model validation and dispatch-time resolution reject a different OpenAI
binding, including for a record that bypassed admin validation.

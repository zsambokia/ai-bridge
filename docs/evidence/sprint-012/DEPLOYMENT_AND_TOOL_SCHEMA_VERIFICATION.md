# Deployment and tool-schema verification

The connected endpoint is the Cloudflare Tunnel for this checkout's local
server. It was restarted after the repair with an ephemeral Bearer credential;
the credential was not written to source, evidence, logs, or configuration.

An authenticated remote `factory.list_capabilities` call returned HTTP 200,
`tool_surface_version: 2026-07-27.1`, and both required capabilities:
`conversation.confirm` and `scope.confirm_and_execute`.

The public `conversation.confirm` schema accepts only `project_id`,
`scope_identifier`, and `confirmation_text`. The server derives the
authenticated Product Owner identity, exact confirmation reference, proposal
binding, and idempotency key. A manual ChatGPT connector re-scan is the
Product Owner retest step; direct tunnel verification proves the active server
already serves the corrected schema.

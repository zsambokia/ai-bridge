# Django admin operational notes

Django admin is the temporary inspection, diagnostic, and recovery interface;
it is not a separate authority path. Inspect `ExecutableScope`,
`ConversationOrchestration`, `ExecutionPreparation`, `ExecutionContract`,
`ExecutionStartRequest`, `ExecutionRun`, and `McpAuditEvent` together.

For a blocked conversation, first inspect the exact proposal version/hash,
confirmation reference, transition history, contract lifecycle, run phase, and
last failure. Resume only through the public canonical orchestration operation
with its idempotency key. Do not edit status, approval, contract, or run fields
directly, and do not create a second approval or execution request to repair a
retry. Admin exposes the data as read-only so recovery keeps the same domain
invariants as MCP.

For a pending Product Owner review, inspect the review response before treating
the conversation as blocked: an eligible response must name
`conversation.confirm` as its next tool. That high-level tool derives the
authenticated caller binding, confirmation reference, and retry key. Do not use
admin or `scope.approve` to turn a free-form affirmative message into approval:
`scope.approve` remains a lower-level operation that requires a pre-existing
durable approval reference.

Completion is operationally valid only after the provider has stopped, every
Release Gate has passed, evidence paths exist, and the final commit is known.
Record completion through `scope.complete_execution`; it binds the run and
contract rather than relying on an admin field edit.

## Local OpenAI model provider configuration

Use this procedure only in local development. The application does not store a
credential value in Django or in the provider configuration.

1. Copy `.env.example` to `.env` if it does not already exist, then set
   `OPENAI_API_KEY` to a valid locally issued key. `.env` is Git-ignored; do
   not paste its contents into tickets, commits, logs, or the Django admin.
2. Start Django with `bridge.settings.local` (the default for `manage.py`). It
   reads `.env` before shared settings, without overriding an already supplied
   process environment variable. A process/secret-manager value therefore has
   precedence.
3. In Django admin, open `/admin/projects/executionprovider/`, select the
   OpenAI provider, set **Credential binding** to `OPENAI_API_KEY`, and save.
   This field stores only the reference name.
4. Confirm the provider is **Active** and enable it only when it is intended
   for use. Use **Run non-mutating provider health check** from the provider
   list to verify that the reference resolves; it does not call OpenAI.

For staging and production, do not deploy `.env`; inject `OPENAI_API_KEY`
through the environment or the platform secret manager and retain the same
`credential_binding` reference.

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

## Recovering a completed provider run

Do not edit execution lifecycle fields in Django admin. A provider can finish
after its caller has disconnected; reconciliation records the terminal fact
and moves the canonical run from `RUNNING` to `VALIDATING` exactly once. The
same recovery path closes an active run past the persisted-activity deadline
as `BLOCKED` with a `WATCHDOG_STALE_BLOCKED` event; it never silently remains
active after a detectable stall.

Run the bounded, idempotent recovery command from the repository root:

```powershell
python manage.py reconcile_provider_runs
```

`execution.get_run_status` performs the same reconciliation before presenting
Product Owner progress. The resulting validation continuation must still run
the applicable tests and release gates, write evidence, update documentation,
and bind the final commit before the draft Pull Request can be closed.

Factory Development Mode is only for the canonical `ai-bridge` repository and
requires an explicit Product Owner approval reference. It is not available
for customer Projects and does not permit a manual terminal-state override.

## Governed cancellation

The `ExecutionRun` detail view has a **Request cancellation** action for an
active run. Enter a non-empty reason, inspect the resulting confirmation page,
and select the explicit confirmation button. The first submit records only a
durable cancellation request; the confirmation submit invokes the same
canonical cancellation service as MCP. Do not edit lifecycle fields, terminate
a process tree from the shell, or use admin to bypass confirmation.

The normal action requests graceful provider termination and leaves the run in
`CANCELLING` until provider acknowledgement/reconciliation writes
`CANCELLED`, cancellation evidence, and closure facts. A completed or terminal
provider response is safe and is reported deterministically rather than raising
an error. `python manage.py reconcile_provider_runs` also reconciles a
persisted `CANCELLING` run after a restart; a non-responsive provider remains
observable through its durable cancellation events and the existing watchdog.

There is intentionally no routine force-cancel control. A forceful emergency
action, if separately authorized in a future scope, must preserve the same
requester, reason, confirmation, event, evidence, and audit trail.

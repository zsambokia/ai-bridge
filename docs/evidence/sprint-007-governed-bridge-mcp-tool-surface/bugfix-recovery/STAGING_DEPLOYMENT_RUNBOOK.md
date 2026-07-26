# Staging deployment runbook — Sprint 007 recovery

## Required operator action

Run these commands in the deployed staging release environment, using the same
database and settings as the public MCP service:

```text
python manage.py migrate
python manage.py showmigrations projects
```

The required verification line is:

```text
[X] 0005_governed_mcp_records
```

If the process does not pick up the migrated schema automatically, restart or
redeploy the staging web process. Do not edit migration records or contract
lifecycle data directly in the database.

## Post-deployment acceptance

Use the staging HTTPS MCP endpoint with a Bearer token. Complete `initialize`,
`notifications/initialized`, `tools/list`, the eight bounded calls specified
in `acceptance-results.json`, and the negative authorization/protocol checks.
The expected result is HTTP 200 JSON-RPC for every valid call, exactly 23 tools,
tool surface version `2026-07-26.1`, and no HTML, stack trace, or secret.

## Rollback

This is an additive Django migration. Do not fake a rollback by deleting
migration history. If deployment causes a separate operational failure, restore
the previous application release according to the staging platform procedure
and preserve the database state for investigation. Escalate a destructive
database rollback for an explicit operator decision.

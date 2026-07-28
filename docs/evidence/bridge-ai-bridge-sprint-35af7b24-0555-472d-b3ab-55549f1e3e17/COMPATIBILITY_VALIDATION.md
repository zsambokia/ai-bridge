# Sprint 015 compatibility validation

## Public MCP protocol

The governed MCP surface version is `2026-07-28.1`. The change is additive:
`execution.get_activity_summary` is a new read-only tool. Existing
`execution.get_run_status` and `execution.list_events` retain their names,
authorization class, and response responsibility. Existing clients therefore
remain compatible; clients that need the compact calculated checklist may opt
in to the new tool.

## Persistence and lifecycle

No migration is required. The implementation uses the existing `ExecutionRun`
and `ExecutionProgressEvent` tables and their ordered relation. The new event
types are values in the existing event stream, so historical executions remain
readable and no parallel lifecycle or status model is introduced.

## Verification

`python manage.py makemigrations --check --dry-run` reported `No changes
detected`. The full test suite, lint, type check, scope validation, and format
check passed on the final candidate state. The focused provider projection test
also proves that provider text containing credential-like content is not
retained in the activity event.

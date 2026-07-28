# Sprint 015 assessment

## Scope and canonical reuse

The approved Sprint 015 scope was assessed against the existing execution
boundary. `ExecutionRun` remains the sole lifecycle record and
`ExecutionProgressEvent` remains its ordered, durable event stream. The
activity view is a pure projection of those records; it introduces neither a
second lifecycle nor a manually maintained status field.

The implementation reuses the configured Codex provider adapter, the existing
repair loop, audit-backed MCP dispatch, and the governed read-only execution
tools. In DEV activity mode the adapter reads Codex JSON output as it arrives,
projects only the event type to a secret-safe progress event, and makes that
event available before provider completion. Provider text, stack traces, and
credential-like values are not persisted or displayed.

## Why `execution.get_activity_summary` is required

`execution.get_run_status` exposes the current run record and
`execution.list_events` exposes the ordered raw event history. Neither can
provide a bounded, continuously recomputed checklist without every consumer
duplicating the event-to-checklist rules. The additive, read-only
`execution.get_activity_summary` is therefore required: it returns the same
canonical event data as short activity entries plus the eight derived checklist
states. It does not create new authority, mutate a run, or replace either
existing tool.

## Assessment result

The approved scope is implementable without an ASF employee, meeting, channel,
or invented-person layer. The resulting console, Django admin, and MCP views
all project the one canonical event stream. Repair completion is only derived
after a persisted successful gate rerun (`REPAIR_VERIFIED`).

# Integration validation

The real V3 scope, immutable contract, and dispatched execution run were read
through the governed MCP surface. `governance.prepare_codex_handoff` returned
`HANDOFF_READY` from those persisted records. The provider was observed as
finished; the activity stream remained canonical and its heartbeat projection
did not mutate the run.

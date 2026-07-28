# Compatibility validation

The change preserves the existing append-only event contract and existing
read-only MCP activity tool. Heartbeat is an additive derived field. The new
handoff tool is read-only and returns an explicit incomplete state when durable
authority is missing. Existing full-suite verification passed: 78 tests.

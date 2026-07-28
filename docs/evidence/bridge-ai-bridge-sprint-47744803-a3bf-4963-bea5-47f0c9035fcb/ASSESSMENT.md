# Assessment — Fix MCP Execution Internal Error

## Scope and risk

This BUGFIX covers only the public MCP execution-token tools in
`zsambokia/ai-bridge`: status, activity summary, event listing, and
cancellation. It is assessed as an external-integration and public-protocol
change because a malformed failure reaches connected MCP clients.

## Finding and repair strategy

All four tools used a direct ORM `ExecutionRun.objects.get()` lookup. An absent
record raised `ExecutionRun.DoesNotExist`, which was not handled by the public
tool adapter and became JSON-RPC `-32603`. The repair centralizes UUID parsing
and missing-record handling, preserves the existing canonical lifecycle and
approval path, and adds both domain and HTTP-MCP regression coverage.

## Compatibility decision

No successful response schema or authority rule changed. Expected invalid
execution-token requests now receive a bounded MCP tool error, which is the
compatible replacement for an unusable transport-level internal error.

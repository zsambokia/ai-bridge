# Production-impact smoke requirement

The staging smoke is intentionally pending. After the migration and any needed
restart, it consists of authenticated HTTPS MCP initialization, discovery, and
the bounded non-destructive calls listed in `acceptance-results.json`; every
valid call must return HTTP 200 JSON-RPC with no HTML, stack trace, or secret.

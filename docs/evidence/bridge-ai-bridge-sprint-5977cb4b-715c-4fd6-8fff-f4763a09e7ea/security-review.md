# Security and governance review

The AKB service binds every operation to a ready active Project context. Project
entries are isolated; only the `ai-bridge` project may author Platform scope.
Only active entries are searchable/readable by default. Candidate mutation
cannot overwrite active knowledge. Activation requires an unrevoked,
project-bound durable approval. Context packages exclude repository content and
secrets. MCP audit details record references rather than entry content.

Residual risk: direct Python service callers do not independently create
`McpAuditEvent`; the governed public surface does. This is a documented
medium-term governance gap, not a claim of complete audit coverage.

# Security review

Credentials are represented only by validated environment/backend binding names. Values are never persisted, returned by MCP, put in audit events, or written to this evidence. Public provider projections omit both configuration and credential bindings. Admin health checks are non-mutating.

OpenAI and Claude are model APIs only. GitHub is a repository service and BigQuery a data service; neither is classified as an execution agent.

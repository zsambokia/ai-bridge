# Rollback assessment

The operational change is the normal, additive application of
`projects.0005_governed_mcp_records`. It creates the canonical governed-MCP
records required by valid tools. Direct manipulation of Django migration history
or execution-contract rows is prohibited. If a platform rollback is required,
use the staging deployment platform's recoverable release procedure and retain
database evidence for diagnosis.

# Sprint 007 recovery assessment

## Scope and relationship

This is an additive BUGFIX / RECOVERY execution under contract `8`
(`797f08d26b8697dec63f4dde106d37f96af1947d71287f1edd010327abad1c8a`).
It references the approved Sprint 007 specification, implementation commit
`7d361103023041ea9232d3d07375cf4fb7bf80fd`, and the prior terminal contract
`bridge:ai-bridge:sprint_007_governed_bridge_mcp_tool_surface:d9ea9d6b-bc78-409d-986a-1207c0c58322`
(`f962c3d49a762f02ab2e53b95b4a6420ebedc10c5228c332326ead95497428ab`).
The earlier contract remains historical and unchanged.

## Findings

- `projects/migrations/0005_governed_mcp_records.py` exists at implementation
  commit `7d36110` and is therefore on `main`.
- The local migration inventory reports `[ ] 0005_governed_mcp_records`.
- Valid public tools create an append-only `McpAuditEvent` through the existing
  canonical governed-MCP service. `McpAuditEvent` is introduced by migration
  `0005`; a database lacking that migration causes the observed valid
  `tools/call` HTTP 500 failure before a structured MCP result can be returned.
- No alternate tool implementation, schema migration, authentication path, or
  Cloudflare bypass is required for recovery. The required repair is deployment
  of the existing migration, followed by a bounded live acceptance rerun.

## Canonical risk mapping

The requested names map directly to the strongest matching canonical enum:

| Requested intent | Canonical modifier |
| --- | --- |
| `DATABASE_MIGRATION` | `DATA_OR_SCHEMA_MIGRATION` |
| `DEPLOYMENT_OR_PRODUCTION_IMPACT` | `PRODUCTION_IMPACT` |

The other requested modifiers are canonical as written:
`EXTERNAL_INTEGRATION`, `PUBLIC_API_OR_PROTOCOL`, and
`AUTHENTICATION_OR_AUTHORIZATION`.

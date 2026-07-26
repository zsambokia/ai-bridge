# Sprint 005 Generator Bootstrap Assessment

**Baseline:** `a3ebbb594c898ca87b773b8e9325b2ad254d0a0f`  
**Bootstrap contract:** `bridge:ai-bridge:sprint-005:foundation-bootstrap-2026-07-26` (consumed for this assessment and execution)

## Reused canonical components

| Required responsibility | Existing canonical component | Sprint 005 extension |
| --- | --- | --- |
| Project Registry | `projects.models.Project` | Contract belongs to the selected Project. |
| Project definition and readiness | `projects.services.load_project_definition`, `assess_onboarding` | Reuse validated static configuration and configured gates. |
| Project Context | `projects.models.ProjectContext` | Require a valid Context before a standard contract can be issued. |
| Repository identity and HEAD | `projects.services._repository_identity`, `_head_sha`, `_current_branch` | Reuse for binding validation and baseline resolution. |
| Sprint validation and evidence root | `projects.execution_context.build_execution_context` | Extend its explicit Project/Sprint checks into a persisted Contract payload. |
| MCP transport and registration | `projects.mcp`, `projects.views.mcp_endpoint` | Register the contract lifecycle operations on the same endpoint. |
| Persistence | Django `projects` app migrations | Add one immutable issued-contract record; do not create a second Registry or Context store. |

There is no existing persisted execution-contract or audit model. The existing
Execution Context is an in-memory, canonical input package, so it is the
appropriate source for contract resolution but not a replacement for durable
issued-contract storage.

## Design decision

The generator will store a normalized JSON payload, its SHA-256 hash, and a
lifecycle state in `projects.ExecutionContract`. Draft validation may update a
draft; once issued, the payload and hash are immutable. Human-readable handoff
text is rendered exclusively from that stored payload. Contract operations are
registered through the existing `/mcp/` adapter.

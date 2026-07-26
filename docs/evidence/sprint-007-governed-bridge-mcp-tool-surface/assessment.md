# Sprint 007 repository assessment

## Assessment record

- Assessed repository: `zsambokia/ai-bridge`
- Assessed branch: `main`
- Assessed baseline: `26b0de7321f9d9904470a373a2c2002a7069e79c`
- Sprint authority: `docs/sprints/SPRINT_007_GOVERNED_BRIDGE_MCP_TOOL_SURFACE.md`
- Assessment boundary: planning and contract issuance only; no Sprint 007 implementation has started.

The repository is a Django application with a persisted project registry and a
Streamable HTTP MCP endpoint.  Sprint 006 already established a standards-based
remote transport, Bearer-token authentication, JSON-only protocol failures, and
the tiered execution-contract lifecycle.  The current public surface remains
intentionally narrow: `factory.get_status` only.

## Existing reusable services

| Existing component | Current capability | Sprint 007 reuse decision |
| --- | --- | --- |
| `projects.models.Project` and `ProjectContext` | Persisted project identity, readiness, and canonical runtime context | Reuse as the sole project/context source; extend only where visibility or caller scoping needs durable data. |
| `projects.mcp` operation registry | Internal, typed-by-convention dispatch for project resolution, context generation, and contract lifecycle operations | Reuse as the canonical service seam; replace its implicit/public-ineligible dispatch with a governed registry facade and explicit schemas. |
| `resolve_project` / `continue_project_resolution` | Exact and ambiguous project resolution with persisted continuation token | Reuse the resolution behavior and durable continuation record; add expiry, caller/project scope, and audit/idempotency controls before public exposure. |
| `projects.execution_context.build_execution_context` | Builds project-scoped execution context from the registered project definition | Reuse directly behind `project.get_context` and execution preparation; do not recreate document/path resolution in the HTTP adapter. |
| `projects.contracts` | Generate, validate, issue, consume, complete, supersede, revoke and validate tiered contracts | Reuse the lifecycle service and its immutable issued payload; place authorization, approval, audit, idempotency, and public schemas around each public lifecycle tool. |
| `projects.contract_policy.resolve_policy` | Deterministic policy, evidence, documentation, review, and gate obligations | Reuse unchanged for Sprint 007 issuance and later governance validation. |
| `projects.views.mcp_endpoint` | MCP initialize, `tools/list`, `tools/call`, JSON errors, Bearer token check, Cloudflare/proxy-safe HTTPS handling | Retain as a thin Streamable HTTP protocol adapter; replace the hard-coded one-tool conditional with the governed registry. |
| Sprint 006 remote MCP tests | Real protocol/authentication/proxy regression coverage | Extend as the public transport regression suite; preserve status tool compatibility. |
| Django migrations/admin/test stack | Persisted state, deterministic migrations and pytest coverage | Reuse for new governance records and all lifecycle/tool-journey validation. |

## Publish as MCP tools after governed facade work

These functions already have canonical business behavior.  They are candidates
for publication, not reimplementation, once the registry supplies schemas,
classification, authorization, audit, and idempotency where applicable.

| MCP tool family | Reused canonical behavior | Required facade work before publication |
| --- | --- | --- |
| `factory.get_status`, `factory.list_capabilities` | Existing status data; registry metadata | Generalize the current status handler and expose only caller-visible capabilities. |
| `project.resolve`, `project.continue_resolution`, `project.get` | Project lookup and continuation resolution | Project visibility, expiry, scoped continuation ownership, validated arguments, and audit. |
| `project.get_context` | `build_execution_context` | Project-scoped authorization, bounded/redacted result schema, and audit. |
| `contract.generate`, `contract.validate`, `contract.issue`, `contract.consume`, `contract.complete`, `contract.supersede`, `contract.revoke`, `contract.get_status`, `contract.render_handoff` | `projects.contracts` lifecycle services and existing internal registrations | Explicit tool schemas, lifecycle classification, durable approval/authorization checks, idempotency, and audit trail. |

## Capabilities requiring real implementation

| Capability | Assessment finding |
| --- | --- |
| Canonical governed tool registry | No public registry currently exists: public dispatch is a hard-coded `factory.get_status` conditional and the internal registry has no schema/classification/policy metadata. |
| Authentication and authorization policy | The endpoint has one shared Bearer-token check, but no caller identity, role/capability policy, project visibility, or approval boundary. |
| Audit and idempotency | No audit-event or idempotency persistence model exists.  These are required for mutating and approval-sensitive operations. |
| Approval and lifecycle controls | Contract services enforce state transitions, but no durable approval record or caller authorization envelope protects public lifecycle mutations. |
| AKB access | No bounded, project-scoped AKB search/document retrieval service exists.  It must be implemented without arbitrary filesystem access. |
| Execution preparation and start request | No persisted preparation, handoff, start-request, or dispatcher abstraction exists.  `execution.request_start` must persist a governed request and must not execute shell, Git, SQL, filesystem, or code actions. |
| Tool schemas and protocol error mapping | Existing remote tests prove only status.  Every Sprint 007 tool needs a stable input/output schema and protocol-safe JSON failures. |
| Documentation/evidence | Required tool reference, architecture, AKB/roadmap updates and all Sprint 007 evidence artifacts do not yet exist. |

## Explicit non-goals and safety boundary

The public MCP server must not expose arbitrary shell commands, Git operations,
raw filesystem access, SQL, Django admin mutations, or code execution.  The
HTTP adapter remains transport-only; all decisions and mutations must run
through project-scoped canonical services.

## Risk-modifier compatibility mapping

The approved Sprint requests five risk intentions.  The canonical generator's
current enum contains the first three exactly, but has no literals named
`STATE_MUTATION` or `EXECUTION_ORCHESTRATION`.  Before implementation, the
generator is therefore invoked only with canonical modifiers and records this
deterministic, non-weakening mapping:

| Requested intent | Canonical modifier used | Reason |
| --- | --- | --- |
| `EXTERNAL_INTEGRATION` | `EXTERNAL_INTEGRATION` | Exact canonical match. |
| `AUTHENTICATION_OR_AUTHORIZATION` | `AUTHENTICATION_OR_AUTHORIZATION` | Exact canonical match. |
| `PUBLIC_API_OR_PROTOCOL` | `PUBLIC_API_OR_PROTOCOL` | Exact canonical match. |
| `STATE_MUTATION` | `IRREVERSIBLE_OPERATION` | Strongest existing mutation-safety modifier; it adds rollback assessment and explicit risk review. |
| `EXECUTION_ORCHESTRATION` | `CROSS_REPOSITORY` | Closest existing cross-boundary governance modifier; it adds coordination obligations and does not weaken the requested control boundary. |

The resulting Sprint policy is expected to be `extended` and to require the
baseline Sprint artifacts plus authorization, integration, compatibility,
rollback, explicit-risk, and cross-boundary coordination evidence/review.  The
issued contract is the authoritative record of the resolved output.

## Assessment conclusion

Sprint 007 is feasible without replacing the established project registry,
execution-context builder, contract lifecycle, or remote MCP transport.  The
work is predominantly a governed-publication layer plus the missing durable
governance and execution/AKB services.  Contract issuance can proceed from
this clean, approved baseline; implementation must wait until the issued
contract has been committed and then consumed.

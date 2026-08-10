# API & Integration Assessment

## Target Architecture

Conversation is a human interface. API, MCP, scheduler, webhook, and automation use source-specific adapters that converge at Mission intake, then use Kernel/Operational Foundation/Provider Integration boundaries.

## Current Repository

`bridge/urls.py` exposes UI, admin, health, and MCP routes. `projects/ui_urls.py` exposes Factory and runtime execution endpoints. `projects/runtime_api.py` controls `OrkiExecution`; `projects/mcp.py` and `projects/governed_mcp.py` implement MCP services.

## Gap Analysis

**Partial:** multiple integration boundaries exist and governed MCP is substantial. **Missing:** a public source-neutral Mission intake contract, integration identity/scope propagation, consistent versioning/error envelope, and Kernel event terminology. **Legacy:** UI runtime endpoints directly expose ORKI Runtime operations.

## Migration Strategy

Place an intake adapter in front of each source and map output to stable neutral projections. Maintain existing routes through compatibility adapters until clients migrate; version any public contract changes.

## Risks and Dependencies

Client breaking changes and authorization gaps are material. Depends on Mission Intake, Identity & Scope, Kernel facade, Provider Integration, and event envelope.

## Readiness

**Partially Ready.** Existing boundaries are useful adapters but currently converge only indirectly.

## Evidence

`bridge/urls.py`; `projects/ui_urls.py`; `projects/runtime_api.py`; `projects/mcp.py`; `projects/governed_mcp.py`.

# Provider Architecture Assessment

## Target Architecture

Provider Integration → Provider Resolver → stateless Capability Provider → stateful Provider Executor. Execution belongs solely to Kernel; the provider binding is immutable per Execution, replacement is executor-only, and recovery remains within that provider.

## Current Repository

`ExecutionProvider` and `ProviderAuditEvent` are durable records. `projects/providers.py` contains provider contracts/adapters; `projects/provider_gateway.py:ProviderGateway` is the active invocation boundary, and `projects/execution.py` dispatches through it.

## Gap Analysis

**Partial:** configurable providers, audit events, and adapter isolation exist. **Missing:** constitutional resolver/integration separation, immutable per-Execution binding, explicit executor lifecycle, and complete Runtime Profile capability contract. **Legacy adapter:** Provider Gateway remains a first-class coordinating concept.

## Migration Strategy

Make Gateway an internal Provider Integration adapter. Add a resolver that persists the selected binding before execution, then introduce executor records/projections without allowing cross-provider fallback. Existing provider configuration remains compatible.

## Risks and Dependencies

Provider sessions/workspaces can be stateful; accidental provider failover violates reproducibility. Depends on Kernel Execution identity and scope-aware secrets policy.

## Readiness

**Partially Ready.** Reusable adapter infrastructure exists, but the ownership and binding contracts do not.

## Evidence

`projects/models.py` (`ExecutionProvider`, `ProviderAuditEvent`); `projects/providers.py`; `projects/provider_gateway.py`; `projects/execution.py`.

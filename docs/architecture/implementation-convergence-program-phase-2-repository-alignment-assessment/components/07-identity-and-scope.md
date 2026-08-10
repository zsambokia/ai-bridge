# Identity & Scope Assessment

## Target Architecture

Every relevant object has explicit owner and scope through Organization, Workspace, Repository, and scope-based authority. Kernel, AKB, provider, evidence, and API operations honor that scope.

## Current Repository

`Project` is the principal owner and contains repository identity/root. `ExecutableScope` and contracts bind governed work to a Project. Django login identifies UI users; MCP has token configuration.

## Gap Analysis

**Partial:** project-level ownership and executable scope exist. **Missing:** Organization/Workspace models, membership/role relationships, repository as independent scoped object, uniform scope identifiers, and policy enforcement across records. **Debt:** `project` means both product context and effective tenant.

## Migration Strategy

Decide the canonical ownership graph, add it additively, backfill existing Project records into a default organizational scope, then propagate scope to new writes and authorization checks. Do not infer tenancy from repository strings.

## Risks and Dependencies

Data migration and authorization are security-sensitive. This is the prerequisite for multi-tenancy, localized asset ownership, and scope-safe API/provider operations.

## Readiness

**Not Ready.** A Product Owner-approved ownership/retention/backfill decision is required before implementation.

## Evidence

`projects/models.py` (`Project`, `ExecutableScope`, contract-bound records); `projects/scopes.py`; `projects/contracts.py`; `projects/factory_chat.py`; `bridge/settings/base.py`.

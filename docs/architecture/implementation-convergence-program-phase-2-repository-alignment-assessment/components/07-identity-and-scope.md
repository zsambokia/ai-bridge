# Identity & Scope Assessment

## Target Architecture

Article VI defines the only logical Scope hierarchy as `Organization ->
Workspace -> Project`. Every persistent domain object SHALL have exactly one
direct Scope owner; no persistent domain object may float without Scope
ownership. Repository is a Scope-owned Resource, normally Project-owned, and
is never a Scope or identity-hierarchy level. A Project may own zero, one or
multiple Repositories. Providers, credentials, secrets, documents, artifacts,
configurations and knowledge infrastructure are Resources, not Scope types.

Every Mission has exactly one direct Scope owner. Product-development Missions
normally belong to a Project, while Organization- and Workspace-scoped Missions
remain valid target use cases. Ownership and inherited higher-scope information
are distinct; this target does not prescribe redundant ancestor ownership
fields or detailed inheritance semantics.

## Current Repository

`Project` is the principal owner and contains repository identity/root. `ExecutableScope` and contracts bind governed work to a Project. Django login identifies UI users; MCP has token configuration.

## Gap Analysis

**Partial:** project-level ownership and executable scope exist. **Missing:**
Organization/Workspace models, membership/role relationships, a uniform direct
Scope-owner relationship, Repository as an independent Scope-owned Resource,
and policy enforcement across records. **Debt:** `project` means both product
context and effective tenant; physical execution workspace can be confused with
the logical Workspace Scope.

## Migration Strategy

The canonical ownership graph is decided by Article VI. A Phase 3 Sprint must
choose the implementation and development-data disposition under its approved
scope. Pre-MVP direct convergence permits replacement or rebuild where simpler;
it does not authorize this assessment to migrate data or infer tenancy from
repository strings.

## Risks and Dependencies

Data migration and authorization are security-sensitive. This is the prerequisite for multi-tenancy, localized asset ownership, and scope-safe API/provider operations.

## Readiness

**Not Ready.** The target hierarchy is approved, but Phase 3 still requires an
implementation decision for inheritance, shared Resources, authorization and
development-data disposition.

## Evidence

`projects/models.py` (`Project`, `ExecutableScope`, contract-bound records); `projects/scopes.py`; `projects/contracts.py`; `projects/factory_chat.py`; `bridge/settings/base.py`.

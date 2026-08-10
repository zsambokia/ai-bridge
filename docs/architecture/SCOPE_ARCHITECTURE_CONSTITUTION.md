---
status: APPROVED_TARGET
owner: Architecture
version: 1.0.0
canonical_language: en
authority: Product Owner Directive (2026-08-10)
---

# Article VI — Scope Architecture

## Authority and status

This is an approved target Constitution Book entry. It defines the canonical
scope, ownership and resource model for AI Bridge. It does not authorize a
schema, API, data migration or runtime implementation. Those changes require
an approved implementation Sprint and the relevant ADRs.

Normative text is English. Localized renderings are derived representations
and MUST preserve the meaning, identifier, version and provenance of this
entry.

## VI.1 Scope Architecture

Every persistent domain object SHALL be owned by exactly one Scope. There are
no floating persistent domain objects. A Scope is an ownership and authorization boundary;
it is not a repository, a provider, a physical working directory or a generic
tag.

The only canonical Scope types are:

```text
Organization
    → Workspace
        → Project
```

An Organization is the tenant and authorization root. A Workspace is a
logical operating scope within one Organization. A Project is the governed
product and execution context within one Workspace. Every Mission SHALL have
exactly one direct Scope owner. Product-development Missions normally belong
to a Project; Organization- and Workspace-scoped Missions remain valid target
architecture for governance, maintenance, and cross-project operations. A
Mission's ancestor scopes are derived through its direct owner.

## VI.2 Scope and Resource are distinct

Only Organization, Workspace and Project are Scope containers. A Resource is
owned by exactly one Scope and MUST NOT own a Scope. A Scope MAY own child
Scopes and Resources only.

```text
Organization
    → Workspace
        → Project
            → Repository
            → Project-scoped Mission
            → Context Package
            → Evidence
            → Provider binding
```

Repository is a Resource, never a Scope. A Project MAY own multiple
Repositories; a Repository does not contain a Project in the canonical model.
Provider definitions, provider credentials, secrets, documents, models,
artifacts, configurations and knowledge infrastructure are likewise Resources,
not Scopes. Their owner may be an Organization, Workspace or Project when
their governed policy permits it.

The Architectural Knowledge Base (AKB) is a scope-aware knowledge model, not
an ordinary Resource or a database synonym. Its graph, embeddings, indexes and
retrieval infrastructure are supporting Resources. Knowledge Object identity,
version and lifecycle remain governed by Articles I and II; Scope governs
ownership, authorization and applicable policy.

The following invariants apply:

1. **SC-001:** A Scope SHALL own only child Scopes and Resources.
2. **SC-002:** Every Resource SHALL belong to exactly one Scope.
3. **SC-003:** A Resource MUST NOT own, contain or create a Scope.
4. **SC-004:** Repository and Provider are Resources; neither is a Scope type.
5. **SC-005:** Physical `ExecutionWorkspace` is a Provider Executor resource,
   not the logical Workspace Scope.

## VI.3 Uniform Scope Ownership Model

All Scope types use one abstract Scope model. Each Scope SHALL expose a
globally unique identity, metadata, its parent Scope where applicable, child
Scopes, Resources, Policies, Configuration, Members, Knowledge, Evidence and
Audit references.

Organization is the sole root Scope and has no parent. Every Workspace has
exactly one parent Organization. Every Project has exactly one parent
Workspace. A Scope MAY have zero or more child Scopes and zero or more
Resources.

Scope identity is not user identity. Membership and authorization are Resources
and policies governed by Scope; they do not redefine the Scope hierarchy.

## VI.4 Scope Ownership and Inheritance

Direct ownership and inheritance are distinct. A persistent object has one
authoritative direct Scope owner; it MUST NOT duplicate ancestor ownership
identifiers solely to restate the hierarchy. Ancestor Scope information is
derived from the direct owner.

Scope inheritance is a general platform mechanism, not a special case for
Providers, AKB or credentials. Detailed inheritance rules, including which
policies, knowledge, credentials, providers, permissions, and configurations
may inherit or be overridden, remain open architecture questions. They require
ADR-035 before implementation; this Article does not prescribe inheritance
modes, conflict resolution, or a persistence representation.

Inherited access never changes Resource ownership. A Resource retains exactly
one owning Scope, while an applicable ancestor policy may make it available to
a descendant Scope under recorded authorization and evidence rules.

## VI.5 Architectural consequences

1. Scope-aware, tenant-ready, organization-ready and workspace-ready describe
   architectural readiness, not immediate multi-customer operation.
2. Authorization, provider credentials, Context Packages, Evidence, AKB
   access and Kernel operations SHALL evaluate direct ownership and applicable
   ancestor Scope through this hierarchy.
3. Every persistent canonical object SHALL record one owning Scope or have its
   ownership deterministically derived from a canonical owning object; no
   object may infer Scope from a Repository alone.
4. Existing project-bound scopes, physical execution workspaces and repository
   lifecycle records are historical implementation evidence. They are not
   canonical scope definitions and require an approved migration or rebuild
   plan before replacement.

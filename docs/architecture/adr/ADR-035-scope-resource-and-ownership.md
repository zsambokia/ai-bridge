---
status: ACCEPTED_TARGET
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
canonical_language: en
authority: Product Owner Decision Alignment (2026-08-10)
---

# ADR-035 -- Scope, Resource and Direct Ownership

## Decision

The canonical Scope hierarchy is `Organization -> Workspace -> Project`. Every persistent domain object SHALL have exactly one direct Scope owner; no persistent domain object may float without Scope ownership.

Repository is a Scope-owned Resource, normally owned by a Project. A Project may own zero, one or multiple Repositories. Provider configuration/binding, credentials, secrets, documents, artifacts, configurations, knowledge infrastructure and physical execution workspaces are Resources, not Scope types. A Resource SHALL NOT own a Scope.

Every Mission has exactly one direct Scope owner. Product-development Missions normally are Project-scoped; Organization- and Workspace-scoped Missions remain valid target cases. Direct ownership and inherited higher-Scope information are distinct, and this ADR does not mandate redundant ancestor fields.

## Consequences

The current Project-bound implementation is a Phase 3 gap. Scope inheritance, shared Resources, authorization policy and development-data disposition require an approved implementation Sprint; this ADR does not define them.

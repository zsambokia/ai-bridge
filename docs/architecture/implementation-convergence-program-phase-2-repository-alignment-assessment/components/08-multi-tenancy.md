# Multi-tenancy Assessment

## Target Architecture

The platform is scope-aware, tenant-ready, organization-ready, and workspace-ready. This is an architectural capability; immediate multi-customer operation is not presumed.

## Current Repository

`KnowledgeEntry` distinguishes PLATFORM and PROJECT scope; most durable records use `Project`. The repository contains no Organization or Tenant model and no cross-record tenant policy layer.

## Gap Analysis

**Partial:** platform/project knowledge partition and project-scoped relations are useful precursors. **Missing:** tenant root, workspace layer, membership/roles, isolation constraints, tenant-aware query conventions, and migration/backfill policy.

## Migration Strategy

Build only after Identity & Scope ADR approval. Start with additive ownership fields and safe default scope, then make scoped managers/repositories mandatory for new writes before enforcing database constraints. Avoid a wholesale `Project` rename.

## Risks and Dependencies

Incorrect backfill or query filtering can disclose data. Depends completely on component 07 and security authorization.

## Readiness

**Not Ready.** The target requires a missing foundational ownership model.

## Evidence

`projects/models.py` (`Project`, `KnowledgeEntry.Scope`); `projects/knowledge.py`; `projects/scopes.py`.

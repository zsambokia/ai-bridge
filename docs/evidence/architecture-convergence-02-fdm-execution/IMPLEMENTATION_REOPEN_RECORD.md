# Architecture Convergence 02 — Factory Development Mode implementation reopen

**Execution profile:** Product Owner Factory Development Mode for AI Bridge self-development  
**Authority:** Product Owner instruction attached on 2026-08-14; it explicitly
authorizes work without an AI Bridge-managed provider, heartbeat, worker lease,
or Bridge-issued running Execution Contract while the managed runtime is not
proven stable.  
**Scope authority:** `docs/evidence/architecture-convergence-02-local-source-reconstruction/CONVERGENCE_EPIC.md`, including its source decision package.  
**Branch:** `main`  
**Baseline:** `0ecef95d2d92fd39b84eee076fe5e03ed2b77414`  
**Working-tree preflight:** clean

## Reopen boundary

The preceding Architecture Convergence 02 closure remains immutable historical
evidence of constitutional/document convergence.  This record reopens only the
previously unimplemented runtime, migration, test, end-to-end, and evidence
obligations.  It does not reinterpret the approved R/CHAT decisions or revert
the canonical Constitution.

## Planned implementation boundary

- Reuse the existing `projects` Project, Conversation, Context Profile,
  Context Package, Knowledge Entry, and Cognitive State owners.
- Add a persisted FactoryIP L0–L4 foundation: effective scope, attributable
  evidence, append-only provenance, immutable artifact versions and explicit
  knowledge-publication resolution, nodes/services, packets, and zoning.
- Provide a deterministic Factory Fabric Service that resolves nodes/services
  and zones a semantic Conversation Understanding request without proxying
  payload storage or domain authorization.
- Add stateless Cognitive Processing result production and bind it to the
  existing CSM/Conversation and AKB boundaries without assigning Cognitive or
  FactoryIP ownership to the AI Kernel.

## Checkpoint

| Field | Value |
| --- | --- |
| Completed steps | FDM preflight; source-bound L0–L4 protocol implementation; migration 0069; integration tests; conformance, obligation, chat traceability, and audit evidence. |
| Modified files | `projects/models.py`, `projects/factory_protocol.py`, migration 0069, Context Package eligibility plumbing, protocol tests, and additive evidence records. |
| Validation | `manage.py check`, full pytest, ruff check/format, mypy, migration check, local migration application, and diff check pass; final architecture evidence test and commit/push remain. |
| Remaining steps | Final architecture evidence test, closure record, commit, push, and origin/main verification. |
| Next action | Bind final validation and commit to the implementation-completion closure report. |

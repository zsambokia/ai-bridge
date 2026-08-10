---
status: CURRENT
scope: Architecture Convergence Program – Sprint 4
language: en
---

# Open Issues and ADR Needs

## No unresolved terminology choice was silently decided

| ID | Open issue | Required action | Status |
| --- | --- | --- | --- |
| ADR-020 | Constitution Book authority and adoption sequence. | Adopt the Book only through an explicit constitutional amendment Sprint. | Required. |
| ADR-021 | Tenant-ready scope hierarchy conflicts with legacy product-only wording. | Define Organization, logical Workspace, Repository, Project and authorization semantics. | Required. |
| ADR-023 | Target Execution aggregate vs `ExecutionRun`, jobs and recovery records. | Define compatibility and migration proof. | Required. |
| ADR-024 | Capability declaration, discovery and resolution. | Define distinct Engine Definition Registry and Capability Registry contracts. | Required. |
| ADR-025 | Context Package and Knowledge Reference schema. | Define versioning, storage, provenance and retention. | Required. |
| ADR-026 | Localization model. | Define canonical-English source, locale fallback and derived-content provenance. | Required. |
| ADR-027 | Kernel Event envelope and replay. | Map current events without relabelling history. | Required. |
| ADR-029 | Provider Integration/Resolver, immutable Binding and Executor recovery. | Define adapter compatibility and same-Provider recovery proof. | Required. |
| ADR-033 | AI Kernel boundary and terminology transition. | Define the transition/retirement sequence for legacy Runtime names. | Required. |
| ADR-034 | `ExecutionJob` retention vs Execution Attempt. | Make a dedicated implementation compatibility decision; no rename before it. | Required. |

## Controlled remaining inconsistencies

1. The Repository still implements legacy Runtime, Gateway, `ExecutionRun` and
   `ExecutionJob` terminology. This Sprint intentionally makes no code claim.
2. Accepted ADR bodies and immutable evidence retain their original language.
   The classification register, rather than retrospective edits, makes their
   relationship to the target explicit.
3. Article I and Article III are approved target entries, not yet the adopted
   single Constitution Book. Their status must not be promoted without ADR-020
   and the controlled adoption Sprint.

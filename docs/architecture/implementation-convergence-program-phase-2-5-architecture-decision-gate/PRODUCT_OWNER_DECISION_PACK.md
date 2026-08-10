# Product Owner Decision Pack

**Classification:** Architecture Convergence decision artifact preserved in the
historical mixed Phase 2.5 record. Only accepted decisions recorded in the
Constitution Book and/or accepted ADRs are canonical. Governance is defined by
[Architecture and Implementation Convergence
Governance](../ARCHITECTURE_IMPLEMENTATION_CONVERGENCE_GOVERNANCE.md).

## Decision requested

Approve, modify, or reject each recommendation below. A modified decision should state the intended canonical object, owner, and lifecycle boundary so the ADR and Phase 3 contract can be updated without inference.

| ID | Recommended decision | Product Owner response |
| --- | --- | --- |
| AC-01 | Remove `ExecutionJob` from the canonical model; replace its delivery role with `OperationalWorkItem`. | Pending |
| AC-02 | Adopt one Kernel-owned `Execution`; remove `OrkiExecution`, replace `ExecutionRun`, and defer first-class `ExecutionAttempt` until justified by ADR. | Pending |
| AC-03 | Adopt `Organization → Workspace → Project`; classify Repository, Provider, AKB and physical Execution Workspace as scope-owned Resources; keep physical Execution Workspace distinct. | **Accepted — Product Owner Directive (2026-08-10); recorded in Article VI.** |
| AC-04 | Adopt minimum AKB primitives: KnowledgeObject, immutable version, relationship, KnowledgeReference, and ContextPackage; approve initial type set and KLM minimum. | Pending |
| AC-05 | Adopt English canonical technical identifiers; require multilingual support for eligible semantic/user-facing content; preserve original Evidence and derive translations separately; preserve Knowledge identity/version across language representations. | **Accepted -- Product Owner Decision Alignment (2026-08-10); recorded in Article VII. Detailed representation, fallback and lifecycle mechanics remain ADR-037.** |
| AC-06 | Place OperationalWorkItem delivery with Operational Foundation and Execution lifecycle with AI Kernel; remove rather than blindly rename `ExecutionRun`. | Pending |

## Accepted-decision alignment

**AC-03 -- Scope / Identity Hierarchy.** The approved target is
`Organization -> Workspace -> Project`. Every persistent domain object has
exactly one direct Scope owner. Repository is a Scope-owned Resource, normally
Project-owned; it is never a Scope or hierarchy level. A Mission has exactly
one direct Scope owner; Project is normal for product development but
Organization- and Workspace-scoped Missions remain valid target cases.

**AC-05 -- Localization.** Canonical code and technical identifiers are
English. Appropriate user-facing and semantic content is multilingual-ready.
Original Evidence remains in its original language and content; translations
are separately attributable derived representations. Knowledge translations do
not automatically become unrelated Knowledge identities. Implementation
mechanics remain governed by ADR-037.

## Follow-up authority requested

After the remaining decisions above, authorize preparation/acceptance of ADR-034 through ADR-038 and the controlled documentation clarification implied by AC-06. AC-03 and AC-05 are already resolved by Articles VI and VII; ADR-035 and ADR-037 record only their remaining implementation-level decisions. This is still not authority for data reset, destructive migration, or application implementation; those require an exact approved Phase 3 child Sprint.

## Recommended approval statement

> I approve the Phase 2.5 Canonical Implementation Blueprint and the six recorded recommendations, subject to ADR-034 through ADR-038. I authorize Phase 3 child Sprint planning under the proposed implementation contract. No destructive migration or implementation is authorized by this approval alone.

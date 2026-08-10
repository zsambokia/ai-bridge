# Product Owner Decision Pack

## Decision requested

Approve, modify, or reject each recommendation below. A modified decision should state the intended canonical object, owner, and lifecycle boundary so the ADR and Phase 3 contract can be updated without inference.

| ID | Recommended decision | Product Owner response |
| --- | --- | --- |
| AC-01 | Remove `ExecutionJob` from the canonical model; replace its delivery role with `OperationalWorkItem`. | Pending |
| AC-02 | Adopt one Kernel-owned `Execution`; remove `OrkiExecution`, replace `ExecutionRun`, and defer first-class `ExecutionAttempt` until justified by ADR. | Pending |
| AC-03 | Adopt `Organization → Workspace → Repository → Project`; keep physical Execution Workspace distinct. | Pending |
| AC-04 | Adopt minimum AKB primitives: KnowledgeObject, immutable version, relationship, KnowledgeReference, and ContextPackage; approve initial type set and KLM minimum. | Pending |
| AC-05 | Adopt versioned LocalizedRepresentation, English canonical source, explicit fallback, and source-language evidence preservation. | Pending |
| AC-06 | Place OperationalWorkItem delivery with Operational Foundation and Execution lifecycle with AI Kernel; remove rather than blindly rename `ExecutionRun`. | Pending |

## Follow-up authority requested

After the decisions above, authorize preparation/acceptance of ADR-034 through ADR-038 and the controlled documentation clarification implied by AC-06. This is still not authority for data reset, destructive migration, or application implementation; those require an exact approved Phase 3 child Sprint.

## Recommended approval statement

> I approve the Phase 2.5 Canonical Implementation Blueprint and the six recorded recommendations, subject to ADR-034 through ADR-038. I authorize Phase 3 child Sprint planning under the proposed implementation contract. No destructive migration or implementation is authorized by this approval alone.

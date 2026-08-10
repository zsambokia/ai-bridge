---
status: CURRENT
scope: Architecture Convergence Program – Sprint 4
language: en
---

# Constitution Documentation Consistency Matrix

| Canonical concept | Documents updated | Remaining / controlled disposition |
| --- | --- | --- |
| AI Kernel | Article III remains canonical; Runtime 2.0 and core constitutions marked TRANSITIONAL. | Historical snapshots and evidence retain Runtime wording by register policy. |
| Provider Integration / Provider Resolver | Runtime 2.0, Architecture Constitution, Engine Constitution, Operational Foundation Constitution, Article III, Sprint 4 report. | Legacy Gateway occurrences are controlled by historical/immutable/transitional policy; implementation migration requires ADR-029/033. |
| Kernel Managers / Registries / Objects | Article III, Sprint 3 Matrix, Sprint 4 plan/report. | No code or historical-record rename is authorised. |
| Engine Definition Registry distinct from Capability Registry | Article III, Sprint 3 Matrix, Sprint 4 plan/report. | Contract/persistence topology remains ADR-024 governed. |
| Execution / ExecutionJob | Article III, Sprint 3 Matrix, Sprint 4 plan/report. | 69 historical/implementation references to `ExecutionJob` retained pending ADR-034. |
| Kernel Object pattern | Article III, Sprint 3 Matrix, Sprint 4 plan/report. | Exact persistence topology remains ADR-backed. |
| Operational Foundation separate layer | Article III, Operational Foundation Constitution transition note, Sprint 4 report. | Current implementation ownership is not recertified. |
| Context Package | Article III, AKB Article I, Sprint 4 report. | Schema/storage adoption remains ADR-025. |
| Knowledge Object / Knowledge Reference | AKB Article I, Sprint 4 classification/report. | Existing AKB implementation names remain transitional pending ADRs. |
| Scope-aware / tenant-ready / localization-ready | Bridge Constitution transition, Article III, Book plan. | Data/API implementation migration remains ADR-021/026 governed. |

## Zero-tolerance checks for active target terminology

| Check | Required result |
| --- | --- |
| Provider Gateway described as first-class target object | No occurrence. |
| Kernel Services used as canonical object category | No occurrence. |
| Engine Definition Registry collapsed into Capability Registry | No occurrence. |
| Automatic `ExecutionJob` rename claimed | No occurrence. |

Legacy wording is not a failure when the document is classified historical,
immutable evidence or transitional and its treatment is explicit in the
[classification register](DOCUMENT_CLASSIFICATION_REGISTER.md).

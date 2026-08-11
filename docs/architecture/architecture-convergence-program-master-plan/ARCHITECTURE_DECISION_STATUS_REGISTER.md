# Architecture Decision Status, Challenge, and PO Queue

## Decision register

| ID | Subject | Status | Required disposition |
| --- | --- | --- | --- |
| ADR-020 | Constitution Book authority/adoption | OPEN | PO adopts authority, conflict and amendment rule |
| ADR-021 / 035 | Scope hierarchy and ownership | APPROVED target / OPEN mechanics | Preserve Article VI; decide inheritance and sharing |
| ADR-022 | unified Mission intake | PROPOSED | PO decision before runtime work |
| ADR-023 / 034 / 038 | Execution, job, run and OWI boundary | CHALLENGED | PO selects one ownership model |
| ADR-024 | Capability contract | OPEN | Define routing, input/output, evidence and failure boundary |
| ADR-025 | Context Package / Knowledge Reference | OPEN | Confirm immutable addressing and invalidation |
| ADR-026 / 037 | Localization | APPROVED target / OPEN mechanics | Decide representation, BCP-47, fallback and lifecycle |
| ADR-027 | Kernel events/replay | OPEN | Define event/recovery authority |
| ADR-029 | Provider resolver/binding/recovery | OPEN | Resolve canonical provider boundary |
| ADR-030-032 / 036 | Knowledge object and lifecycle | APPROVED target / OPEN adoption mechanics | Bind Book and minimum implementation contract |
| ADR-033 | Kernel boundary transition | OPEN | Define transition without mixed ownership |

## Conflicts and challenges

| Challenge | Evidence | Status | Gate |
| --- | --- | --- | --- |
| `ExecutionJob` is delivery machinery | model and worker queue evidence | CHALLENGED | ADR-034 |
| `ExecutionRun` couples delivery and kernel concepts | current models and foundation docs | CHALLENGED | ADR-038 |
| provider gateway terminology | legacy adapter/module versus target Provider Integration | SUPERSEDED terminology, implementation-only adapter retained | ADR-029 |
| Repository as Scope | older maps versus Article VI | SUPERSEDED target assumption | ADR-035 mechanics |
| document-centred knowledge | `KnowledgeEntry`/revision models versus target AKB | IMPLEMENTATION-ONLY evidence | ADR-030-032/036 |

## PO decision queue

1. Adopt or reject ADR-020 and name the Constitution Book's canonical effective date.
2. Select the Execution/OperationalWorkItem ownership boundary (ADR-034/038); reject mixed lifecycle ownership.
3. Approve the capability, Context Package, and provider contract set.
4. Confirm AKB target adoption mechanics and the Scope/localization implementation-design decisions.

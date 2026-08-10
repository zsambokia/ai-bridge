# Revised Migration Strategy — Pre-MVP Direct Convergence

## Decision

The Phase 2 migration roadmap is valuable as repository evidence, but its compatibility-first defaults are superseded for future implementation planning by this document. Phase 3 will converge toward the accepted canonical blueprint through direct replacement and controlled rebuild where that is simpler and safer.

## Default rule

| Situation | Default action |
| --- | --- |
| Historical model conflicts with canonical ownership | Replace it; do not preserve its public or persistence shape. |
| Development data blocks a clean model | Rebuild or migrate it in a separately approved implementation scope. |
| A historical term is used only internally | Remove it rather than retain an alias. |
| A temporary compatibility path is proposed | Reject unless its bounded benefit, exit criteria, owner, and removal Sprint are documented. |
| A destructive operation is required | Stop for separately approved scope and evidence; Phase 2.5 grants no such authority. |

## Transformation map

| Current evidence | Canonical destination | Preferred transformation | Compatibility justification needed? |
| --- | --- | --- | --- |
| `OrkiExecution` combined intake/orchestration | Conversation, Mission, MSM, and outcome projections | Decompose and replace | Yes, if any projection is retained after cutover. |
| `ExecutionRun` contract-bound dispatcher record | Kernel `Execution` | Replace aggregate and lifecycle | Yes, if historical rows/API are exposed after cutover. |
| `ExecutionJob` queue/lease record | Operational `OperationalWorkItem` | Replace name and boundary | Yes, if a queue adapter remains. |
| Provider Gateway | Provider Integration adapter | Internalize behind resolver/binding | Yes, if external callers remain. |
| Knowledge Entry / Revision packages | Uniform AKB primitives | Rebuild/migrate through published Knowledge Objects | Yes, if legacy reads stay enabled. |
| Project-only scope | Organization → Workspace → Repository → Project | Establish canonical root hierarchy before dependent aggregates | Yes, if unscoped paths coexist. |
| UI-string-only language assumptions | Versioned Localized Representation | Add only after ADR-approved object boundary | Yes, for fallback aliases or implicit translation. |

## Required transformation order

1. Product Owner accepts or changes AC-01 through AC-06 and the Phase 3 contract.
2. Establish canonical scope/ownership and authorization boundaries before creating dependent durable aggregates.
3. Separate Mission/MSM authority from Operational Work Item delivery authority.
4. Establish Kernel `Execution`, events, Provider Binding, and executor integration behind immutable contracts.
5. Introduce Context Package and minimum AKB primitives with KLM publication and invalidation boundaries.
6. Migrate/rebuild development data only inside an approved implementation Sprint, with explicit recovery and evidence plans.
7. Delete transitional paths once their approved cutover criteria are satisfied; do not leave compatibility infrastructure without an owner and removal date.

## Explicit exceptions ledger

No compatibility exception is approved by Phase 2.5. Any Phase 3 proposal requesting an adapter, alias, dual read/write, data projection, or strangler route must add this record to its Sprint evidence:

| Field | Required content |
| --- | --- |
| Canonical boundary affected | Exact aggregate/contract and constitutional rule. |
| Why direct replacement is unsafe | Concrete technical evidence, not convenience. |
| Narrow exception | Endpoint, model, data set, or integration retained. |
| Owner and expiry | Responsible owner and removal Sprint/date. |
| Validation | Cutover, rollback, and deletion evidence. |

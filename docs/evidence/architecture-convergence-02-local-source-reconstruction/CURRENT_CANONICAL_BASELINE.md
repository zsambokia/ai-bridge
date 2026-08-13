# Current canonical baseline

## Status and comparison rule

This is a repository-baseline observation made after the independent local-source
reconstruction. It is not a source of target decisions.

The Bridge Constitution describes itself as a **TRANSITIONAL CANONICAL DRAFT**.
Its 2026-08-10 convergence note says that more-specific Architecture Constitution
Book entries are to be adopted through the Book process. Consequently the
baseline is authoritative for the current repository, but it does not override
the Product Owner-approved semantics in `DECISION_LEDGER.md`.

## Material baseline already present

| Baseline material | Relationship to source reconstruction |
|---|---|
| `BRIDGE_CONSTITUTION.md` | Governance baseline; requires controlled adoption of material architecture changes. |
| `CONVERSATION_TO_MISSION_ARCHITECTURE_CONSTITUTION.md` | Substantially aligns with the Conversation → CU → CSE → Mission Resolution → Mission direction, CU statelessness, and immutable Context Package/Evidence concepts. |
| `AI_KERNEL_ARCHITECTURE_CONSTITUTION.md` | Aligns with R-28: AI Kernel is an execution core and is not Cognitive Processing. |
| `runtime_2_0_constitution.md` | Establishes the current Runtime 2.0 baseline and its migration vocabulary. |

## Material baseline gaps or unresolved mappings

The source-derived package has no confirmed canonical home in the inspected
baseline for FactoryIP as a full L0–L4 package (R-24), FFS as a thin control
plane (R-25), or the communication-authorization zoning model (R-26).

Names also require deliberate reconciliation: the repository uses **Conversation
State Engine (CSE)** while the source discusses **CSM** in its state/lifecycle
separation. This package does not equate those terms without an adopted mapping.

See `CONSTITUTION_IMPACT_MATRIX.md` for proposed adoption work; none of it is a
Constitution amendment in this documentation-only sprint.

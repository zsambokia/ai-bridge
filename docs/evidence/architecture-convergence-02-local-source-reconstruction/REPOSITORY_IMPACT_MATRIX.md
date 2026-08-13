# Repository impact matrix

| Area | Source-derived change to assess | Evidence needed before change |
|---|---|---|
| Domain models and services | Enforce single ownership for Conversation, lifecycle/state, Mission Resolution, and Mission | call graph, write-path inventory, transition tests |
| CU and cognitive processing | Separate stateless interpretation from durable state and business authority | write-path proof and contract tests |
| Artifact/evidence persistence | Apply immutable/versioned artifact, claim, relation, assurance, and retention semantics | schema inventory, migration plan, reproducibility tests |
| Factory protocols | Model Factory Message and FactoryIP without making FFS a proxy | protocol specification, compatibility and security review |
| Network boundaries | Apply communication authorization separately from domain authorization | threat model, policy model, integration tests |
| UI/nodes | Keep Factory Chat/Node UI from owning domain runtime state | API ownership map and UI contract tests |
| Documentation/ADRs | Adopt approved deltas and terminology | Constitution Book proposal, ADRs, diagram evidence |

This sprint makes none of these changes. The matrix is intentionally a
sequencing aid, not implementation authority.

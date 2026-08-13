# 02 — Constitution Impact Matrix

Status: **PRE-VERIFICATION IMPACT MATRIX — approved target, repository coverage to be verified by Codex**

This matrix records the known architectural impact of section 02. It is intentionally not presented as an exhaustive repository traversal.

| Area | Existing baseline to preserve/reconcile | Section-02 delta | Required treatment | Verification owner |
|---|---|---|---|---|
| Root architecture chain | PO → Factory Chat → Conversation → Mission → MSM → Operational Foundation → AI Kernel/runtime | Add explicit Cognitive Processing and Factory Protocol boundaries without moving AI Kernel pre-Mission | Amend canonical chain/definitions | Codex |
| Factory Chat | UI/interaction adapter, not Runtime | Clarify adapter cannot own business state or bypass FactoryIP domain boundaries | Clarify | Codex |
| Conversation | First-class durable domain | Separate durable state from stateless Understanding/Evaluation; preserve 00/01 state model | Amend | Codex |
| Conversation progression | Existing maturity/progression rules may be numeric/linear | Semantic State + Lifecycle Status + Readiness Conditions; Knowledge Publication and Mission Resolution are separate boundaries | Replace conflicting rules | Codex |
| Context | Immutable Context Package exists | Add Effective Scope/Profile resolution and canonical Context Assembly role | Extend/reconcile | Codex |
| Cognitive Profile | New convergence concept | Versioned processing contract for context/understanding/evaluation policies | Add canonical definition | Codex |
| Understanding | Existing CU/CSE language may imply authority | Stateless interpretation only; immutable Understanding Result | Replace/clarify | Codex |
| Evaluation | May be scattered/domain-specific | Reusable stateless qualification capability; immutable Evaluation Result | Add/normalize | Codex |
| Domain Authority | Existing ownership rules across domains | Explicit consequence boundary after cognitive processing | Clarify consistently | Codex |
| AI Kernel | Post-admission execution core; executes, does not decide | Explicitly keep Cognitive Processing outside Kernel | Confirm + remove contrary diagrams/text | Codex |
| Scope Constitution | Project/scope/resource distinction | Add Effective Operational Scope and resolved bindings as L0 | Extend | Codex |
| Evidence | Evidence already important/auditable | Formal L1 Evidence Protocol, sufficiency separation and ownership | Extend/normalize | Codex |
| Provenance | Existing evidence/provenance concepts may be partial | New L2 graph, relation registry, lifecycle, authority, evidence contracts | Add/reconcile | Codex |
| Artifact | Existing planning/execution outputs and knowledge links | New L3 Artifact Contract, identity/version/payload/integrity/governance model | Add/reconcile | Codex |
| Artifact ↔ Evidence | Existing docs may conflate output/evidence | Artifact remains Artifact; Evidence references Artifact Version for proof purpose | Replace conflation | Codex |
| Artifact ↔ Knowledge | Existing docs may say approved Artifact becomes Knowledge | Semantic extraction → Knowledge Candidate → Publication Resolution | Replace | Codex |
| AKB | Versioned/searchable/auditable Knowledge | Add candidate/publication outcomes/conflict handling and provenance from Artifact Version | Amend | Codex |
| Claim | New convergence concept | Governed scoped assertion with authority obligation; one Resolution Subject | Add cross-cutting definition | Codex |
| Resolution | New convergence concept | Standard unresolved-authority handoff/result/consequence protocol | Add; placement to be validated | Codex |
| L4 Transport | Existing MCP/HTTP/runtime handoffs may be ad hoc | Canonical semantic boundary transport; not every service call | Add/reconcile | Codex |
| FactoryIP | New convergence concept | Name of complete L0–L4 stack | Add | Codex |
| Factory Packet | New convergence concept | Transported unit carrying layered protocol semantics and payload | Add | Codex |
| FactoryIP Node | New convergence concept | Addressable logical service boundary, implementation hidden | Add | Codex |
| Published services | Existing APIs may be CRUD-oriented | Semantic service contracts; no internal reach-through | Add invariant + identify gaps | Codex |
| Conversation Node | Existing Conversation interfaces | `conversation.interaction/context/projection` service families | Add canonical boundary | Codex |
| FFS | New convergence concept | Thin name/service resolution control plane; not payload proxy | Add | Codex |
| Zoning | New convergence concept | Single transport communication-permission model; domain auth separate | Add principle; defer final matrix | Codex |
| MCP / external adapters | Existing remote MCP integration | Adapter to FactoryIP; may not bypass Node/domain authority | Amend/reconcile | Codex |
| Operational Foundation | Unified admission/execution infrastructure | Its cross-domain handoffs must fit FactoryIP without moving business authority | Reconcile | Codex |
| Mission/MSM | Mission lifecycle authority | Preserve; Resolution/FactoryIP must not steal MSM authority | Confirm | Codex |
| Provider/Executor | Definition vs runtime execution split | Preserve; later Node/service topology must respect it | Confirm/reconcile | Codex |
| Diagrams | Existing canonical diagrams | Must show correct cognitive, domain, FactoryIP and runtime boundaries | Regenerate/update | Codex |
| ADRs/indexes | May contain OPEN or superseded convergence assumptions | Close/supersede/update where section-02 decisions resolve them | Traverse and update | Codex |
| Current implementation | May reflect old architecture | Must be documented as Current Implementation and Gap, not treated as target | Assess only unless separately authorized | Codex |

## Explicitly not claimed by this matrix

- It does not claim every impacted file has been found.
- It does not claim all terminology collisions have been detected.
- It does not claim current implementation conforms.
- It does not finalize FactoryIP zoning topology.
- It does not authorize feature implementation beyond canonical documentation/convergence work.

Codex must expand this matrix with concrete repository paths and evidence during closure.

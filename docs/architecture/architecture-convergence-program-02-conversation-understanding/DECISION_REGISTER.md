# Architecture Convergence 02 — Product Owner Decision Register

Status: WORKING

This register separates accepted decisions from proposals, hypotheses, open questions, current implementation facts and future target work. Detailed semantics are defined in `FOUNDATION_DECISIONS.md`.

| ID | Area | Decision | Status | Closure treatment |
|---|---|---|---|---|
| CP-01 | Cognitive Processing | Generalizable stateless processing; durable state remains with invoking domain | ACCEPTED | 02 canonical candidate |
| CP-02 | Cognitive Profile | One versioned scope-aware profile with Context/Understanding/Evaluation policies | ACCEPTED | Supersedes standalone Context Profile |
| CP-03 | Processing Purpose | Processing Purpose is known routing input; User Intent is an Understanding Result | ACCEPTED | 02 invariant |
| CP-04 | Profile composition | Effective profile composition/version/hash must be auditable; no automatic new domain object | ACCEPTED | 02 canonical candidate |
| CP-05 | Invocation | Processing invocation is a contract, not automatically a first-class domain entity | ACCEPTED | 02 simplification |
| CP-06 | Understanding Result | Immutable structured evidence-linked output preserving observation/inference/assumption/reference/ambiguity | ACCEPTED | 02 canonical candidate |
| CP-07 | Evaluation | Evaluation applies contract/policy; Domain Authority owns consequence | ACCEPTED | Cross-cutting invariant |
| L0-01 | Scope hierarchy | Organization/Tenant → Workspace → Project; repository is Resource Context, not automatic scope level | ACCEPTED | Foundation |
| L0-02 | Application rules | Defaults/invariants above scope resolution are not another tenant/scope | ACCEPTED | Foundation |
| L0-03 | Effective Scope | Resolve effective scope/resource/policy/profile bindings before stateless processing | ACCEPTED | Foundation |
| L0-04 | Isolation | Isolation/eligibility before semantic retrieval; no similarity override or sibling leakage | ACCEPTED | Foundation invariant |
| L0-05 | Language | Multilingual context may distinguish interaction/artifact/code/source languages | ACCEPTED | Foundation |
| L1-01 | Evidence | Significant handoffs/transitions produce immutable Evidence; Evidence ≠ logging | ACCEPTED | Foundation |
| L1-02 | Evidence Record | Historical fact references immutable/versioned objects with integrity; may reference Artifact | ACCEPTED | Foundation |
| L1-03 | Authority | Domain Authority owns asserted fact; Evidence Infrastructure records proof | ACCEPTED | Foundation invariant |
| L1-04 | Sufficiency | Evidence existence ≠ sufficiency; Evaluation assesses, Domain Authority decides | ACCEPTED | Foundation invariant |
| L2-01 | Provenance purpose | Record historical derivation/causality/use; not a business decision engine | ACCEPTED | Foundation |
| L2-02 | Relation families | Small controlled canonical families + versioned specializations; no runtime ad-hoc relation types | ACCEPTED | Foundation |
| L2-03 | Historical fact | Materialized relation source/target/semantics immutable | ACCEPTED | Foundation invariant |
| L2-04 | Append history | Correct by appending new relation facts; inverse may be projection | ACCEPTED | Foundation invariant |
| L2-05 | Relation lifecycle | PENDING → ACTIVE → RETRACTED; SUPERSEDED represents replacement of historically legitimate relation | ACCEPTED | Foundation |
| L2-06 | Relation authority | Activation authority contract belongs to canonical relation definition | ACCEPTED | Foundation |
| L2-07 | Assurance separation | Relation lifecycle and Evidence Assurance are separate axes | ACCEPTED | Foundation invariant |
| L3-01 | Artifact identity | First-class Artifact identity + immutable Artifact Versions | ACCEPTED | Foundation |
| L3-02 | Qualification | Understanding may classify; Evaluation applies contract; Artifact Authority owns consequence | ACCEPTED | Foundation |
| L3-03 | Governance | Artifact Contract determines stateful/stateless governance | ACCEPTED | Foundation |
| L3-04 | Evidence relation | Artifact may support Evidence without becoming Evidence or being mutated | ACCEPTED | Foundation invariant |
| L3-05 | Knowledge publication | Full Artifact does not automatically enter AKB; semantic extraction under Knowledge authority | ACCEPTED | Knowledge foundation |
| L3-06 | Knowledge Candidate | Structured provenance-linked candidate; no unnecessary candidate state machine | ACCEPTED | Knowledge foundation |
| L3-07 | Knowledge conflict | Conflict does not auto-weaken ACTIVE knowledge; no last/newest/confidence-wins | ACCEPTED | Knowledge invariant |
| L3-08 | Artifact Contract | Versioned contract defines qualification/purpose/versioning/persistence/integrity/governance/authority | ACCEPTED | Foundation |
| L3-09 | Materialization | Artifact Version metadata separate from inline/external immutable payload; stable ref + digest | ACCEPTED | Foundation |
| L3-10 | Integrity | Same Artifact Version means same immutable content identity | ACCEPTED | Foundation invariant |
| L3-11 | Composition | Composite Artifacts reference immutable versions; dependencies use L2 provenance, not second graph | ACCEPTED | Foundation |
| L3-12 | Applicability | Historical legitimacy ≠ current applicability; evaluate intended use/context/policy | ACCEPTED | Foundation |
| L3-13 | Retention/scope | Historical identity/provenance separate from payload availability; use L0 scope | ACCEPTED | Foundation |
| L3-14 | Protocol boundary | L3 may detect need for external authority but does not perform authority resolution | ACCEPTED | Boundary to L4 |
| X-01 | Result semantics | Result ≠ Outcome ≠ Projection | ACCEPTED | Cross-cutting canonical candidate |
| X-02 | Claim | First-class when explicit responsible authority is needed; not mandatory for deterministic conflict | ACCEPTED | Cross-cutting candidate |
| X-03 | Resolution | Resolution is an L4 interaction pattern, not L3 and not all of L4 | ACCEPTED | Protocol boundary |
| L4-01 | Factory Message | Standardized unit for genuine domain/protocol boundary crossing | ACCEPTED | Foundation |
| L4-02 | Layering | Packet carries L0–L4 semantics; enrich only when relevant new fact exists | ACCEPTED | Foundation invariant |
| L4-03 | Message structure | Envelope + Delivery/Interaction Semantics + Payload Contract | ACCEPTED | Foundation |
| L4-04 | L4 authority | L4 applies communication authorization only; does not absorb domain authorization | ACCEPTED | Foundation invariant |
| FIP-01 | FactoryIP | Name of complete L0–L4 Factory communication stack; not CRUD/API | ACCEPTED | Platform foundation |
| FIP-02 | Node | Stable LAN-addressable logical service boundary; not domain/process/deployment/instance synonym | ACCEPTED | Platform foundation |
| FIP-03 | Published services | Node communication only through published semantic services; no internal reach-through | ACCEPTED | Platform invariant |
| FIP-04 | External adapters | MCP/HTTP/WebSocket do not bypass FactoryIP authority boundaries | ACCEPTED | Platform invariant |
| FIP-05 | Factory Chat | Standalone FactoryIP interaction Node/boundary; UI not Runtime; no Conversation state ownership | ACCEPTED | 00/01 amendment |
| FIP-06 | Conversation | Standalone FactoryIP Node with interaction/context/projection service families | ACCEPTED | 01/02 amendment |
| FIP-07 | Conversation CRUD | No generic CRUD/message CRUD/external state-transition authority as canonical services | ACCEPTED | Negative invariant |
| FFS-01 | FFS role | Factory Fabric Service = FactoryIP routing/name-resolution control plane | ACCEPTED | Platform foundation |
| FFS-02 | FFS traffic | Packets do not flow through FFS; control plane, not data-plane proxy | ACCEPTED | Platform invariant |
| FFS-03 | FFS MVP | Thin/static, AI Bridge internal, no mandatory HA/dynamic discovery/leases/heartbeats/LB | ACCEPTED | MVP baseline |
| ZONE-01 | Zoning | One communication-policy mechanism; identity-to-identity permission, not payload/domain authorization | ACCEPTED | Foundation |
| ZONE-02 | Zoning timing | Finalize after Node + service topology is known | ACCEPTED | Deferred detailed design |
| KERNEL-01 | AI Kernel | Operational execution core, not Cognitive Processing | ACCEPTED | Constitution correction |
| KERNEL-02 | Kernel authority | Kernel executes; it does not decide | ACCEPTED | Constitution invariant |
| KERNEL-03 | Context boundary | Context construction outside Kernel; Kernel consumes prepared immutable Context Package | ACCEPTED | Constitution invariant |
| SCOPE-01 | Course boundary | 02 Understanding; 03 Conversation State & Mission Resolution | ACCEPTED | Closure scope |
| SEQ-01 | Later convergence | L0–L4 + FactoryIP + Node + FFS must be canonical before Mission/MSM relies on them | ACCEPTED | Blocking sequencing rule |
| OPEN-01 | Context Assembly owner | Final owning Node/domain not frozen | OPEN | Later explicit design |
| OPEN-02 | conversation.context consumer | Concrete consumer not frozen | OPEN | Resolve with Context Architecture |
| OPEN-03 | Zoning policy | Exact deny-by-default/service-level rule set not finalized | OPEN | After topology |
| OPEN-04 | Remaining Nodes | Do not integrate unreviewed future domains into LAN topology | OPEN / DEFERRED | Review section-by-section |

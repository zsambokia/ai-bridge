# Architecture Convergence 02 — Lossless Approved Decision Ledger

Status: WORKING / APPROVAL-PRESERVATION RECORD
Authority: Product Owner approvals made sequentially during the 02 training/convergence discussion
Canonical effect: NONE until closure approval and merge

## Purpose

This is the approval-preservation source for Convergence 02. No previously approved Product Owner decision may be lost through summarization, renaming, constitutional compression, or later repository convergence.

## Rules

1. ACCEPTED = explicitly accepted in sequence or confirmed by the later P4 accepted-decision inventory.
2. OPEN / DEFERRED / DIRECTION items are not promoted to ACCEPTED.
3. Later refinements control final semantics, but approved distinctions remain traceable.
4. Examples are explanatory unless separately approved as canonical enumerations.
5. New concepts including Cognitive Profile, Factory Protocol L0–L4, FactoryIP, Factory Packet, Artifact Contract, Claim and FFS are genuine convergence deltas.

# A. Cognitive Processing / Conversation Understanding

## CU-01 — Explicit immutable Context input — ACCEPTED
Understanding consumes explicitly assembled immutable Context Package; no hidden persistent processing memory. The visible context must be reconstructable.

## CU-02 — Immutable structured Understanding Result — ACCEPTED
Preserve Explicit Observation, Inference, Assumption, Resolved Reference and Ambiguity as distinct semantics; do not flatten them into confidence.

## CU-03 — Understanding ≠ Domain Authority — ACCEPTED
Understanding interprets; Evaluation qualifies; Domain Authority owns consequence/state change. High model confidence is not authority.

## CU-04 — Generalized stateless Cognitive Processing — ACCEPTED
Conversation Understanding is one application; durable state remains with invoking domain.

## CU-05 — One Cognitive Profile architecture — ACCEPTED
Use one versioned scope-aware Cognitive Profile with Context Policy, Understanding Policy and Evaluation Policy. This supersedes standalone Context Profile.

## CU-06 — Profile declares requirements, not LLM workflow — ACCEPTED
The same profile may be fulfilled by deterministic processing, classifiers, embeddings, one/multiple LLM calls or verification.

## CU-07 — Processing Purpose ≠ User Intent — ACCEPTED
Profile resolution uses known inputs (purpose/state/actor/scope/trigger/metadata); User Intent is an Understanding Result.

## CU-08 — Cognitive Profile is canonical declarative processing definition — ACCEPTED
It is not Conversation State, Knowledge Object, Context Package or Understanding Result; it is versioned/scope-aware and may carry composition/provenance/supersession metadata.

## CU-09 — Effective Cognitive Profile composition — ACCEPTED
Versioned fragments may compose the effective profile; component versions/snapshot/hash must be auditable.

## CU-10 — Effective Cognitive Profile not automatically first-class — ACCEPTED
Execution/Evidence may preserve effective snapshot/hash; do not create a lifecycle entity solely for composition.

## CU-11 — Cognitive Processing Request is invocation contract, not automatically domain entity — ACCEPTED
Auditability alone does not justify another first-class object.

## CU-12 — Context → Understanding → Evaluation separation — ACCEPTED
Processing Invocation → Profile Resolution → Effective Profile → Context Assembly → immutable Context Package → Understanding → immutable Understanding Result → Evaluation → immutable Evaluation Result → Domain Authority.

## CU-13 — Evaluation is stateless qualification, not consequence authority — ACCEPTED

## CU-14 — Understanding Result historical validity ≠ current applicability — ACCEPTED
An Understanding Result preserves what was understood at T1 from a particular Context Package/Profile. Later evidence does not rewrite it. There is no universal mutable VALID/INVALID status. Applicability depends on current context/state + intended consequence + applicable policy.

## CU-15 — Applicability is evaluated, not decided by Understanding — ACCEPTED
If old interpretation is not applicable to a new consequence, Domain Authority may require reprocessing; old result remains historical evidence.

# B. L0 — Effective Operational Scope & Isolation

## FP-L0/01 — L0 foundation — ACCEPTED
L0 defines effective operating space/isolation for a Factory Protocol handoff.

## FP-L0/02 — Organization/Tenant → Workspace → Project — ACCEPTED
Project is primary working/domain scope.

## FP-L0/03 — Repository/Branch/Revision/Environment are Resource Context — ACCEPTED
Not automatic additional Scope levels.

## FP-L0/04 — Application Default Rules ≠ Scope/Tenant — ACCEPTED
May contain overrideable defaults and non-overridable architecture/security invariants.

## FP-L0/05 — Resolve effective bindings before stateless processing — ACCEPTED
Scope/resource/policy/profile/resolution provenance are supplied; stateless services do not invent their environment.

## FP-L0/06 — Isolation before semantic retrieval — ACCEPTED
Tenant eligibility → Scope eligibility → Resource authorization → Policy eligibility → semantic retrieval → ranking. Similarity never overrides isolation; no sibling-project leakage.

## FP-L0/07 — Multidimensional Language Context — ACCEPTED
Interaction, canonical artifact, code and source languages may differ.

# C. L1 — Evidence Protocol

## FP-L1/01 — Significant handoff/transition Evidence — ACCEPTED
Evidence is immutable proof, not generic logging.

## FP-L1/02 — Evidence Record — ACCEPTED
Uses immutable/versioned references and verifiable integrity; may reference Artifact without transforming it into Evidence.

## FP-L1/03 — Domain Authority owns fact; Evidence Infrastructure records proof — ACCEPTED

## FP-L1/04 — Evidence existence ≠ sufficiency — ACCEPTED
Evidence proves/supports → Evaluation assesses sufficiency/applicability → Domain Authority decides consequence.

# D. L2 — Provenance & Causality Protocol

## FP-L2/01 — L2 purpose — ACCEPTED
Historical derivation/production/use/trigger/causality infrastructure; not business decision engine.

## FP-L2/02 — Stable Relation Families + controlled specialization — ACCEPTED
Small canonical family set, controlled/versioned specializations, inheritance of parent semantics, no runtime ad-hoc relation types. Concrete example specialization lists are not frozen taxonomy.

## FP-L2/03 — Relation is first-class historical semantic fact — ACCEPTED
A materialized relation is independently auditable/governable rather than merely anonymous edge; source/target/type semantics are immutable.

## FP-L2/04 — One authoritative direction; inverse is projection — ACCEPTED
Do not persist two independently authoritative inverse facts by default.

## FP-L2/05 — Append-only temporal history — ACCEPTED
Do not delete/rewrite historical relation fact to correct it; append correcting/replacing fact. Original source/type/target remain unchanged.

## FP-L2/06 — Relation lifecycle — ACCEPTED
PENDING → ACTIVE/RETRACTED; ACTIVE → RETRACTED/SUPERSEDED. RETRACTED does not require replacement; SUPERSEDED means historically legitimate but replaced. Challenge alone does not demote ACTIVE.

## FP-L2/07 — Activation authority ownership — ACCEPTED
Authority contract is part of relation definition. Domain Authority owns semantic truth; Provenance Infrastructure owns recording/integrity/lifecycle mechanics/retrieval. Activation may be deterministic or governed.

## FP-L2/07-A — Authority inheritance — ACCEPTED
Relation Family provides default authority contract; specialization may refine without violating parent semantics.

## FP-L2/08 — Relation Lifecycle ≠ Evidence Assurance — ACCEPTED
Evidence challenge/withdrawal/assurance loss does not automatically alter lifecycle. Re-evaluate assurance; Domain Authority chooses keep/retract/supersede. ACTIVE + DEGRADED assurance is valid. Assurance is represented through immutable Evaluation Results/current projection.

# E. L3 — Artifact Protocol

## FP-L3/01 — Artifact Qualification — ACCEPTED
Producer naming does not make an output canonical Artifact. Versioned contract/policy qualifies output; execution may produce Artifact, Evidence, transient/diagnostic or other output classes.

## FP-L3/02 — Logical Artifact identity + immutable Artifact Versions — ACCEPTED
Change creates new Version, never in-place content mutation. Historical consumers reference concrete immutable Versions, not `latest`.

## FP-L3/03 — Semantic-purpose + contract identity — ACCEPTED
Content similarity is not identity. Same semantic purpose + same contract can remain same logical Artifact despite major content change; different purpose is different Artifact even if derived.

## FP-L3/04 — Understanding may assist classification but is not Artifact authority — ACCEPTED
Understanding → Evaluation against Artifact Contract/Versioning Policy → Artifact Domain Authority → NEW_VERSION / NEW_ARTIFACT / NEEDS_REVIEW. Deterministic cases need no LLM.

## FP-L3/05 — Immutability ≠ statefulness — ACCEPTED
Artifact Contract determines whether durable governance surrounds immutable Version. Mutable approval/review lifecycle is separate governance state, not mutable Artifact content.

## FP-L3/06 — Artifact ↔ Evidence separation — ACCEPTED
Evidence role is not Artifact property/subtype/flag. Same immutable Artifact Version can support multiple Evidence Records. Evidence challenge never mutates Artifact Version.

## FP-L3/07 — Artifact ↔ Knowledge separation — ACCEPTED
Artifact preserves what was produced; Knowledge preserves what the system knows. Full Artifact does not transform into/become Knowledge. Governed publication + provenance links them.

## FP-L3/07-A — Semantic extraction, not mechanical chunking — ACCEPTED
Knowledge units are semantically independent assertions/syntheses; source provenance is retained.

## FP-L3/08 — Knowledge Candidate first-class immutable provenance-linked intermediate — ACCEPTED
Candidate is not yet Knowledge. Understanding may identify it but cannot publish to AKB. No large Candidate state machine; Evaluation/Publication Results preserve treatment.

## FP-L3/09 — Knowledge Publication Resolution — ACCEPTED
Controlled outcomes: CREATE, REVISE, CONFIRM, DUPLICATE, CONFLICT, REJECT. CONFIRM may add provenance/evidence without unnecessary Knowledge content version. Publication Resolution ≠ Publication Consequence; Domain Authority owns consequence/governance.

## FP-L3/10 — Knowledge Conflict stability + lightweight default — ACCEPTED
CONFLICT does not weaken/overwrite ACTIVE Knowledge. No last-writer, highest-confidence or newest-Artifact wins. Default representation uses Candidate + Knowledge + Understanding/Evaluation + Evidence + Provenance + Authority result; policy may promote genuinely complex cases to governance case. Tentative conflict outcome names were not frozen and must remain non-canonical unless later approved.

## FP-L3/11 — Artifact Contract — ACCEPTED
Versioned contract defines qualification, semantic purpose/type, identity, versioning, persistence, integrity, governance/lifecycle, governance requirements/authority, publication/downstream rules. Infrastructure does not invent semantics ad hoc.

## FP-L3/12 — Materialization & Payload — ACCEPTED
Artifact Version is canonical identity/metadata record, not necessarily blob. Payload may be inline/external immutable content addressed by stable ref + digest. Storage technology independent.

## FP-L3/13 — Artifact Integrity — ACCEPTED
Same Artifact Version = same immutable content identity. Different payload = new Version or integrity failure.

## FP-L3/14 — Composition & Dependencies — ACCEPTED
Composite Artifacts reference concrete immutable Versions; dependencies use L2 relations, not a second graph; never historical `latest` binding.

## FP-L3/15 — Artifact Applicability — ACCEPTED
Historical legitimacy ≠ current-purpose applicability. Evaluate Version + intended use + current context/state + policy/scope. No mutable VALID/INVALID Artifact status.

## FP-L3/16 — Retention, Availability & Scope — ACCEPTED
Historical identity/provenance ≠ payload availability ≠ retention. Policy may archive/remove payload without rewriting history. Use L0 scope; no L3 authorization subsystem.

## FP-L3/17 — Protocol Boundary — ACCEPTED
L3 may detect unresolved authority need but does not resolve cross-domain authority; subject crosses into L4.

# F. Result / Outcome / Projection / Claim / Resolution

## FP-X/01 — Result ≠ Outcome ≠ Projection — ACCEPTED
Result = processing/execution output; Outcome = domain-interpreted consequence; Projection = controlled representation for another domain.

## FP-X/02 — Claim may be first-class — ACCEPTED
When ambiguity/conflict requires explicit responsibility/decision authority, Claim is scope-bound governed assertion carrying required authority semantics. Deterministic conflicts need no ceremonial Claim.

## FP-X/03 — Claim is not L3 resolution mechanism — ACCEPTED
It can be cross-boundary subject/payload.

## FP-X/04 — Resolution is one interaction pattern — ACCEPTED
Resolution Request/Result is one general Factory communication interaction; L4 must also carry PO messages, results, outcomes, projections and future interactions.

# G. L4 — Factory Message / Transport semantics

## FP-L4/01 — General upper communication layer — ACCEPTED with terminology evolution
Design evolved Resolution Protocol → Factory Message Protocol → explicit Transport Layer responsibility. Controlling semantics: general cross-boundary messaging plus A→B transport responsibility; not Resolution-specific and not business authority. Final Constitution must reconcile naming without losing either accepted semantic distinction.

## FP-L4/02 — Genuine boundary trigger — ACCEPTED
Not every internal call is Factory Message; use standardized Factory communication at real domain/protocol boundary.

## FP-L4/03 — Envelope / Delivery-Interaction / Payload Contract separation — ACCEPTED
Payload may carry Input/Message, Result, Outcome, Projection, Claim, Resolution Request/Result and future domain payloads.

## FP-L4/04 — Transport owns only A→B transfer information at its level — ACCEPTED
Includes routing/addressing, transport identity/security/authorization context, delivery/interaction, protocol/version information.

## FP-L4/05 — Transport authorization ≠ Domain authorization — ACCEPTED
L4 decides who may communicate with whom/transport action/scope; domain authority decides requested business consequence.

## FP-L4/06 — No separate Layer Bindings block — ACCEPTED
The layered packet already contains needed information; do not duplicate it with separate binding abstraction.

## FP-L4/07 — Layer responsibility isolation — ACCEPTED
Each layer reads/carries its own semantics without needing internal knowledge of other layers.

## FP-L4/08 — Direct layer interpretability — ACCEPTED
Information required at a layer is directly readable at that level.

## FP-L4/09 — Enrich only on relevant new fact — ACCEPTED
No ceremonial Evidence/Artifact per hop.

# H. FactoryIP / Factory Packet / Node

## FIP-01 — FactoryIP = complete L0–L4 communication stack — ACCEPTED
Not merely routing and not CRUD API.

## FIP-02 — Factory Packet = complete layered carried unit — ACCEPTED
Services/infrastructure may operate on relevant packet layer without understanding entire packet.

## FIP-03 — FactoryIP Node = LAN-addressable logical service boundary — ACCEPTED

## FIP-04 — Node ≠ Domain ≠ Service ≠ Process ≠ Deployment ≠ Instance — ACCEPTED
Domain owns concepts/rules; Node is external Factory LAN boundary; Service is what Node publishes; Process/Component is internal realization. Multiple instances do not imply multiple logical Nodes.

## FIP-05 — Node Qualification — ACCEPTED
First-class/deployable/service/engine status alone does not make a Node. Node requires legitimate stable published service contract while internals remain encapsulated. Conversation can qualify; Conversation State/MSM/Context Assembly/Understanding/Evaluation/Execution are not automatically Nodes. Tentative future Node examples remain non-canonical until their sections.

## FIP-06 — No Internal Reach-Through — ACCEPTED
No direct canonical-state reach-through across Node boundary.

## FIP-07 — Published semantic services only; FactoryIP ≠ CRUD — ACCEPTED

## FIP-08 — MCP/HTTP/WebSocket are adapters, not parallel authority paths — ACCEPTED
External protocol → AI Bridge adapter/server → FactoryIP → published Node service.

## FIP-09 — Factory Chat independently addressable Node/boundary — ACCEPTED
Still UI/interaction boundary, not Runtime, and not Conversation state owner.

## FIP-10 — Conversation independent FactoryIP Node — ACCEPTED

## FIP-11 — `conversation.interaction` — ACCEPTED
Semantic interaction intake; external callers do not own message persistence mechanics.

## FIP-12 — `conversation.context` — ACCEPTED
Purpose-bound/scoped authoritative Conversation context. Concrete future consumer remains OPEN.

## FIP-13 — `conversation.projection` — ACCEPTED
Runtime/other domains communicate domain facts, not chat presentation instructions; Conversation Domain decides representation and Factory Chat presentation.

## FIP-14 — Conversation transition is internal authority — ACCEPTED
Do not publish generic `conversation.transition`/`state.set` allowing external state mutation. Conversation decides transition from accepted facts/results.

## FIP-15 — Forbidden canonical Conversation CRUD/state services — ACCEPTED
No canonical `conversation.create/update/delete`, `message.create/update`, `state.set`, generic external `state.transition`. Adapter/implementation CRUD may exist without becoming FactoryIP semantics.

# I. Factory Fabric Service (FFS)

## FFS-01 — FFS naming/role — ACCEPTED
Factory Fabric Service = FactoryIP routing/name-resolution control plane.

## FFS-02 — FactoryIP defines communication; FFS resolves delivery — ACCEPTED
Logical identity/service/address → transport binding/target.

## FFS-03 — Control plane, not data-plane proxy — ACCEPTED
Factory Packet does not normally flow through FFS; avoid central bottleneck.

## FFS-04 — One logical authoritative FFS view — ACCEPTED architectural direction
Future physical replication/failover must not create competing logical authorities.

## FFS-05 — MVP FFS inside AI Bridge, static/thin acceptable — ACCEPTED

## FFS-06 — HA/dynamic fabric not MVP — ACCEPTED
No mandatory dynamic discovery, endpoint leases, heartbeats, LB, distributed registry, HA cluster/failover.

# J. Zoning / firewall

## ZONE-01 — Zoning instead of overlapping Envelope Authority — ACCEPTED

## ZONE-02 — Identity-to-identity communication permission — ACCEPTED
Not payload semantics and not business/domain authorization.

## ZONE-03 — Detail after Node + Service topology — ACCEPTED / DEFERRED DETAIL

## ZONE-04 — Firewall direction accepted; exact deny policy OPEN
Do not falsely canonicalize deny-by-default/service granularity before later approval.

# K. AI Kernel boundary correction

## KERNEL-01 — AI Kernel ≠ Cognitive Processing — ACCEPTED
Kernel is post-admission operational execution core, not Understanding/CSE/Mission Resolution.

## KERNEL-02 — Kernel executes; does not decide — ACCEPTED

## KERNEL-03 — Context construction outside Kernel — ACCEPTED
Kernel consumes prepared immutable Context Package; Context Assembly is not Kernel internal persistent state/manager.

# L. Scope / sequencing

## SCOPE-01 — 02 = Conversation Understanding — ACCEPTED

## SCOPE-02 — 03 = Conversation State & Mission Resolution — ACCEPTED
Do not silently re-approve CSE state axes/transitions, Mission readiness or Mission Resolution outcomes in 02.

## SEQ-01 — L0–L4/FactoryIP foundation before Mission/MSM convergence — ACCEPTED

## SEQ-02 — Do not integrate unreviewed future domains into Factory LAN — ACCEPTED methodology
Examples are not future Node approvals.

# M. Explicit OPEN / DEFERRED — DO NOT PROMOTE

1. Context Assembly final owner/Node.
2. Concrete consumer of `conversation.context`.
3. Profile Resolution ambiguity/fallback/clarification policy.
4. Exact Understanding Result schema beyond approved semantic distinctions.
5. Exact reusable Evidence Evaluation capability contract.
6. Exhaustive Relation Family/specialization taxonomy.
7. Final Knowledge Conflict resolution outcome taxonomy.
8. Exact Zoning rules including deny-by-default/service granularity.
9. Remaining FactoryIP Nodes/services for unreviewed domains.
10. Concrete Conversation State/CSE/Mission Resolution model — 03.
11. Detailed HA/dynamic FFS architecture — future, not MVP.
12. Implementation database/table/API/deployment choices not explicitly approved.
13. Final constitutional naming reconciliation of Factory Message Protocol vs L4 Transport Layer, preserving both approved semantics.

# N. Mandatory non-loss verification

Closure fails if it loses/weakens any accepted distinction above, including CU applicability; Relation first-class/direction/authority inheritance/assurance; Artifact qualification and Evidence-role separation; semantic Knowledge extraction; first-class Knowledge Candidate; all six Publication Resolution outcomes; Publication Resolution vs Consequence; conflict stability; L4 transport-vs-domain authorization; rejected Layer Bindings; Factory Packet; Node Qualification; Conversation projection/transition boundary; FFS control-plane behavior; or OPEN-vs-ACCEPTED status distinctions.

Codex MUST produce Decision → Canonical Location and Canonical Change → Decision traceability covering every ACCEPTED entry. Decision loss, status inflation or semantic weakening = closure failure.
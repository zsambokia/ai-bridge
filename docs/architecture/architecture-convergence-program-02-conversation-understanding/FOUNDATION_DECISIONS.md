# Architecture Convergence 02 — Foundation Decisions

Status: WORKING DECISION RECORD
Authority: Product Owner decisions made during Architecture Convergence 02
Canonical effect: none until closure approval and merge to `main`

This document intentionally records cross-cutting decisions discovered while reviewing Conversation Understanding, whether or not they belong constitutionally to Article IV. Later convergence sections MUST treat the accepted foundation here as baseline once it is constitutionalized.

## A. Cognitive Processing foundation

### CP-01 — Generalized stateless processing

Conversation Understanding is an application of a reusable Cognitive Processing model, not a stateful intelligent domain owner. The durable state remains owned by the invoking domain.

Canonical processing separation:

```text
Processing Invocation
→ Cognitive Profile Resolution
→ Effective Cognitive Profile
→ Context Assembly
→ immutable Context Package
→ Understanding
→ immutable Understanding Result
→ Evaluation
→ immutable Evaluation Result
→ Domain Authority
→ domain consequence
```

### CP-02 — Cognitive Profile

Use one versioned, scope-aware Cognitive Profile rather than independent Context/Understanding/Evaluation profiles. It contains at least:

- Context Policy — what context is required;
- Understanding Policy — what must be understood;
- Evaluation Policy — what criteria must be evaluated.

This supersedes the standalone Context Profile abstraction created during 01.

The profile declares the processing goal and requirements, not an implementation workflow or fixed number of LLM calls. Implementations may use deterministic parsing, classifiers, embeddings, one or more LLM calls, verification or combinations thereof.

### CP-03 — Processing Purpose is not User Intent

Profile resolution cannot depend on a User Intent that Understanding has not yet discovered.

Known routing inputs may include Processing Purpose, current state, actor/role, scope, trigger and input metadata. User Intent is an Understanding Result.

### CP-04 — Profile composition

Effective Cognitive Profile may be composed from versioned profile fragments. The exact effective composition/version/hash used by a run must be auditable. The Effective Cognitive Profile is not automatically a new first-class domain object; execution/evidence may preserve its snapshot/hash.

### CP-05 — Invocation contract, not another domain object

`Cognitive Processing Request` is not introduced as a first-class domain entity merely for auditability. The invocation is a contract carrying explicit input/current state/actor/scope/trigger/processing purpose. Auditability is provided by execution/evidence records.

### CP-06 — Understanding Result

Understanding Result is immutable, structured and evidence-linked. It must preserve semantic distinctions such as:

- explicit observation;
- inference;
- assumption;
- resolved reference;
- ambiguity.

Understanding interprets; it does not mutate domain state and high model confidence is not authority.

### CP-07 — Evaluation and authority

Understanding answers "what does this mean?" Evaluation answers "how does it qualify against the applicable contract/policy?" Domain Authority owns the consequence.

Evaluation is a reusable stateless capability. Evaluation Result is not itself a domain state transition.

## B. L0 — Effective Operational Scope & Isolation

### FP-L0-01 — Scope hierarchy

Canonical ownership hierarchy:

```text
Organization / Tenant
→ Workspace
→ Project
```

Project is the primary working/domain scope. Repository is not automatically another scope level.

Resource Context may include Repository, Branch, Revision, Environment and other resources.

### FP-L0-02 — Application rules

Application Default Rules sit above tenant/workspace/project resolution but are not a Scope or tenant. They may contain:

- overrideable defaults;
- non-overridable architectural/security invariants.

### FP-L0-03 — Effective Operational Scope

L0 resolves and records the effective operating space in which a Factory Protocol handoff is valid. It can bind:

- Organization / Workspace / Project identity;
- effective resource bindings;
- effective policy bindings;
- effective Cognitive Profile binding;
- resolution provenance.

Stateless services do not invent or independently resolve their operating environment. They operate from an already resolved Effective Scope and applicable Profile/Policy.

### FP-L0-04 — Isolation before semantic retrieval

Tenant/scope/resource/policy eligibility is resolved before semantic retrieval/ranking. Semantic similarity can never override tenant or scope isolation. There is no implicit sibling-project context leakage.

### FP-L0-05 — Language context

The code/canonical technical language may be English while the system is multilingual. Language context may distinguish interaction language, canonical artifact language, code language and source languages rather than forcing one global language value.

## C. L1 — Evidence Protocol

### FP-L1-01 — Granularity

Architecturally significant handoffs/transitions produce immutable Evidence. Evidence is not equivalent to generic logging.

### FP-L1-02 — Evidence Record

Evidence records historical facts using immutable/versioned references and verifiable integrity. Evidence may refer to Artifacts without copying or transforming the Artifact into Evidence.

### FP-L1-03 — Authority and recording

The relevant Domain Authority owns the fact/truth being asserted. Evidence Infrastructure records and preserves proof; it does not become the domain decision authority.

### FP-L1-04 — Sufficiency

Evidence existence does not imply evidence sufficiency. Evaluation assesses whether the available Evidence satisfies the applicable Evidence Contract/policy; Domain Authority owns the resulting consequence.

```text
Evidence → proves/supports
Evaluation → assesses sufficiency/applicability
Domain Authority → decides consequence
```

## D. L2 — Provenance & Causality Protocol

### FP-L2-01 — Purpose

L2 records how canonical objects/events are historically related: what they derive from, what caused/triggered/produced them, and what they used. It is common provenance infrastructure, not a business decision engine.

### FP-L2-02 — Canonical relation families

Define a small stable set of canonical Relation Families with controlled, versioned specializations. A specialization inherits parent semantics and cannot contradict it. Runtime ad-hoc relation types are prohibited.

### FP-L2-03 — Relations are historical semantic facts

A materialized relation represents a historical fact. Source, target and canonical relation semantics are immutable after creation. New knowledge appends new relation facts rather than rewriting history.

### FP-L2-04 — Append-oriented graph

The provenance graph is append-oriented. Corrections preserve the old fact/history and append the correcting relation. Inverse relationships may be projections; avoid storing duplicate contradictory directions as independent truth.

### FP-L2-05 — Relation lifecycle

Accepted lifecycle semantics:

```text
PENDING
  → ACTIVE
  → RETRACTED

ACTIVE
  → RETRACTED
  → SUPERSEDED
```

- PENDING: candidate relation, not yet canonical fact;
- ACTIVE: currently canonical relation;
- RETRACTED: assertion withdrawn; replacement not required;
- SUPERSEDED: historically legitimate relation replaced by a newer canonical relation.

Challenge/review does not automatically demote an ACTIVE relation.

### FP-L2-06 — Authority ownership

The activation authority contract is part of the canonical relation definition. Domain Authority owns semantic truth; Provenance Infrastructure owns recording, integrity, lifecycle mechanics and retrieval.

Relation Family may define a default authority contract; controlled specializations may refine it without violating parent semantics.

### FP-L2-07 — Lifecycle and evidence assurance are separate axes

A supporting Evidence challenge, withdrawal or assurance loss does not automatically alter Relation lifecycle. Re-evaluate the Evidence Contract/assurance, then let Domain Authority decide whether to keep, retract or supersede the relation.

Thus a relation can remain ACTIVE while evidence assurance is DEGRADED.

## E. L3 — Artifact Protocol

### FP-L3-01 — Artifact identity and immutable versions

Artifact is a first-class logical identity with immutable, versioned materializations. Artifact Version is immutable; a changed payload is a new version or an integrity failure, never an in-place rewrite.

### FP-L3-02 — Artifact qualification and authority

Artifact identity/version classification may require semantic Understanding, but Understanding does not own the decision. Evaluation applies the relevant Artifact Contract/versioning policy; Artifact Domain Authority owns the consequence. Deterministic cases need not invoke LLM Understanding.

### FP-L3-03 — Stateful vs stateless artifact governance is contract-driven

The applicable Artifact Contract determines whether persistent governance/lifecycle is required. Artifact Infrastructure owns materialization/storage/integrity/version mechanics; domain-specific lifecycle meaning and consequences belong to the authority named by the contract.

Artifact Version itself remains immutable; mutable review/approval lifecycle should live in a separate governance/lifecycle record when such lifecycle is required.

### FP-L3-04 — Artifact ↔ Evidence

An Artifact Version may support one or many Evidence records without becoming an Evidence object and without an `is_evidence` mutation. Challenging Evidence does not mutate the Artifact Version.

### FP-L3-05 — Artifact ↔ Knowledge

A complete Artifact Version does not automatically become AKB Knowledge. Knowledge Publication identifies semantically independent Knowledge Candidates/Objects from the Artifact. This is semantic extraction, not mechanical chunking. Knowledge retains provenance back to the immutable Artifact Version.

Understanding does not directly publish to AKB; Evaluation and Knowledge Domain Authority govern publication.

### FP-L3-06 — Knowledge Candidate

A Knowledge Candidate is a structured provenance-linked potential knowledge unit that is not yet canonical Knowledge. Do not create a large candidate state machine merely because a candidate exists.

### FP-L3-07 — Knowledge conflict stability

Detecting CONFLICT does not automatically weaken or overwrite currently ACTIVE Knowledge. No last-writer-wins, higher-LLM-confidence-wins or newer-Artifact-wins rule. Existing canonical Knowledge remains canonical until the appropriate authority resolves the conflict.

### FP-L3-08 — Artifact Contract

Every canonical Artifact Type uses a versioned Artifact Contract defining qualification, semantic purpose, identity/versioning, persistence, integrity, governance/lifecycle and authority requirements.

### FP-L3-09 — Materialization & payload

Artifact Version is the canonical identity/metadata record; payload may be inline or stored externally as immutable content. Artifact Version references the payload using stable reference and content digest. Logical Artifact semantics are storage-technology independent.

### FP-L3-10 — Integrity

Persistent Artifact Version content must have verifiable integrity. Same Artifact Version means same immutable content identity.

### FP-L3-11 — Composition & dependencies

Composite Artifacts may reference other concrete immutable Artifact Versions. Do not create a separate Artifact dependency graph; use L2 Provenance/Causality relations such as `used` / `derived_from`. Never depend on mutable `latest` where an immutable version is required.

### FP-L3-12 — Applicability

Historical legitimacy and current-purpose applicability are separate. Applicability may be represented by immutable Evaluation Result over Artifact Version + intended use + current context/state + policy. Do not mutate Artifact Version with generic VALID/INVALID state.

### FP-L3-13 — Retention, availability and scope

Historical Artifact identity/provenance is distinct from physical payload availability and retention. Retention/archival policy may move/remove payload according to policy without rewriting historical identity/provenance.

Artifact use is scope-bound by L0. L3 does not implement a second authorization system.

### FP-L3-14 — Protocol boundary

L3 may detect that external authority resolution is required, but authority resolution is not an Artifact Protocol responsibility. The unresolved subject crosses into L4 communication semantics.

## F. Result, Outcome, Projection, Claim and Resolution

### FP-X-01 — Result ≠ Outcome ≠ Projection

- Result: concrete output of processing/execution, e.g. Understanding Result, Evaluation Result, Execution Result.
- Outcome: domain-interpreted consequence, e.g. Mission Outcome, Knowledge Publication Outcome.
- Projection: controlled representation prepared for another domain, e.g. Conversation Projection.

These concepts must not be collapsed into one generic `Result` type.

### FP-X-02 — Claim

Claim may be a first-class, scope-bound governed assertion when a disagreement/uncertainty requires an explicit responsible decision authority. It carries enough semantics to identify the required authority/responsibility. A straightforward deterministic conflict need not create a Claim object merely for ceremony.

### FP-X-03 — Resolution is an interaction pattern

Resolution is not an L3 mechanism and not the whole L4. Claim can be transported as a payload through the general Factory Message Protocol to the responsible authority; Resolution Request/Result is one interaction pattern among others.

## G. L4 — Factory Message Protocol

### FP-L4-01 — Boundary messaging

L4 is the Factory Message Protocol. A Factory Message is the standardized communication unit used when information crosses a genuine domain/protocol boundary. Not every internal service call is a Factory Message.

### FP-L4-02 — Layered packet semantics

Factory Message/Packet carries the layered protocol information. Each responsible boundary produces or forwards the information belonging to its layer. A layer is enriched only when a new relevant fact exists; do not fabricate Evidence or Artifacts on every hop.

Conceptual stack:

```text
L0 Scope & Isolation
L1 Evidence
L2 Provenance & Causality
L3 Artifact
L4 Factory Message Protocol
```

Each layer remains responsible only for its own semantics and need not know lower-layer implementation internals. Information needed at the current layer should be directly interpretable at that layer.

### FP-L4-03 — Envelope / interaction / payload separation

Factory Message separates:

- common Envelope;
- Delivery / Interaction Semantics;
- Payload Contract.

Payload may carry Input/Message, Result, Outcome, Projection, Claim, Resolution Request/Result and future domain-specific types without redefining the transport foundation.

### FP-L4-04 — Transport responsibility

L4 transport carries information needed to move a message from logical A to logical B and applies L4 communication authorization. It does not absorb domain authorization or layer-binding responsibilities belonging elsewhere in the packet.

## H. FactoryIP

### FIP-01 — Name and scope

`FactoryIP` is the name of the complete L0–L4 Factory communication stack. It is not merely a routing service and not a CRUD API.

### FIP-02 — Node

A FactoryIP Node is a stable, LAN-addressable logical service boundary. Node is not synonymous with Domain, component, process, deployment or instance.

Multiple physical instances do not imply multiple logical Nodes. Internal implementation topology is not automatically Factory LAN topology.

### FIP-03 — Published semantic services

Nodes communicate through published semantic services. Direct reach-through into another Node's internal implementation/canonical state is prohibited.

### FIP-04 — External adapters

External protocols such as MCP/HTTP/WebSocket may provide access adapters. They must not bypass FactoryIP Node boundaries to mutate canonical state directly. MCP is not a competitor to FactoryIP; it is an access/integration protocol that may reach AI Bridge services through FactoryIP.

### FIP-05 — Factory Chat Node

Factory Chat is a standalone FactoryIP Node/boundary for communication with the Product Owner, while remaining UI/interaction boundary rather than Runtime and not owning Conversation canonical state.

### FIP-06 — Conversation Node

Conversation is a standalone FactoryIP Node. Accepted semantic service families:

- `conversation.interaction` — intake of Conversation-relevant interactions;
- `conversation.context` — purpose-bound authoritative Conversation context;
- `conversation.projection` — controlled projection of facts from other domains into Conversation semantics.

Do not expose generic Conversation/message CRUD or external `state.set/transition` authority as canonical FactoryIP semantics.

The concrete future consumer of `conversation.context` remains open until Context Assembly ownership is designed.

## I. Factory Fabric Service (FFS)

### FFS-01 — Role

Factory Fabric Service (FFS) is the FactoryIP routing/name-resolution control-plane concept. It resolves a logical FactoryIP identity/service toward the transport binding/target.

### FFS-02 — Control plane, not data-plane proxy

Factory Packets do not flow through FFS. FFS supplies registry/resolution/communication-policy information; transport performs direct delivery using the resolved binding.

### FFS-03 — MVP simplification

For MVP, FFS remains deliberately thin and may be static. It is part of AI Bridge, not a separately deployed service mesh. Dynamic discovery, endpoint leases, heartbeat infrastructure, load balancing and HA clustering are not MVP requirements.

Earlier HA/fallback exploration is retained as future design context, but the Product Owner explicitly decided that HA is not an MVP goal.

## J. Zoning / firewall model

### ZONE-01 — Canonical L4 communication policy mechanism

Use Zoning rather than a second overlapping Envelope Authority model. Zoning answers whether one FactoryIP identity is permitted to communicate with another FactoryIP identity. It does not interpret payload business semantics and is not a replacement for domain authorization.

### ZONE-02 — Design timing

Do not finalize Zoning before the Node + published-service topology is sufficiently known. First discover Nodes/services/required communication paths; derive Zoning afterwards.

Firewall thinking is the baseline. A deny-by-default concrete policy is a strong direction but remains to be explicitly finalized during the topology/Zoning review.

## K. AI Kernel terminology correction

AI Kernel is not Cognitive Processing. It is the post-admission operational execution core. It begins after Operational Foundation admits an immutable Execution Request.

Kernel responsibilities include execution lifecycle, scheduling, capability resolution, immutable Context Package binding, Provider Executor coordination, leases/recovery, telemetry/evidence/security and Kernel Events.

**Invariant:** the Kernel executes; it does not decide.

Context construction is outside the Kernel; Kernel consumes an already prepared immutable Context Package.

## L. Section boundary / deferred items

The training course separates:

- 02 — Conversation Understanding;
- 03 — Conversation State & Mission Resolution.

Therefore 02 closure must not silently re-approve or redesign 03 concerns merely because the current Article IV Constitution combines them. Concrete Conversation State axes, CSE transition rules, Mission readiness and Mission Resolution outcome semantics remain 03 review subjects.

Cross-cutting foundation discovered during 02 — especially L0–L4, FactoryIP, Node model and FFS — is different: it must be constitutionalized before later Mission/MSM convergence relies on it as baseline.

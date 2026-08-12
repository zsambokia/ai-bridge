# Architecture Convergence 02 — Lossless Approved Decision Ledger

Status: WORKING / APPROVAL-PRESERVATION RECORD
Authority: Product Owner approvals made sequentially during the 02 training/convergence discussion
Canonical effect: NONE until closure approval and merge

## Purpose

This file exists for one reason: **no previously approved Product Owner decision may be lost through summarization.**

It is intentionally more granular than the Change Register and Constitution Amendment. Each entry records a distinct approved semantic statement. Closely related decisions remain separate if they were discussed/approved separately, because later constitutional wording must be traceable back to the individual decisions.

Rules:

1. ACCEPTED means the decision was explicitly accepted or appears in the approved P4 decision inventory produced from the sequential approvals.
2. OPEN / DEFERRED items must never be silently promoted to ACCEPTED.
3. Where a later accepted decision refined an earlier one, both history and the final controlling interpretation are recorded.
4. Repository verification is delegated to Codex at closure; this ledger specifies **what must be preserved**, not where every implementation occurrence exists.
5. New concepts created during this convergence (Cognitive Profile, Factory Protocol L0–L4, FactoryIP, Artifact Contract, Claim, FFS, etc.) are genuine convergence deltas, not rediscovered prior canonical terminology.

---

# A. Conversation Understanding → Cognitive Processing

## CU-01 — Understanding consumes explicit Context
**Status:** ACCEPTED

Understanding SHALL NOT construct hidden private memory/context. It operates from an explicitly assembled immutable Context Package so the information visible to the processing run can later be reconstructed.

## CU-02 — Understanding Result is immutable and structured
**Status:** ACCEPTED

Understanding produces an immutable, structured, evidence-linked interpretation result. The result preserves semantic distinctions including:

- Explicit Observation;
- Inference;
- Assumption;
- Resolved Reference;
- Ambiguity.

These distinctions SHALL NOT be flattened into one confidence-bearing assertion.

## CU-03 — Understanding is not Domain Authority
**Status:** ACCEPTED

Understanding interprets meaning. It SHALL NOT mutate canonical domain state merely because it has high confidence.

Canonical separation:

```text
Understanding → interpretation
Evaluation → qualification against policy/contract
Domain Authority → consequence / state change
```

## CU-04 — Cognitive Processing is generalizable and stateless
**Status:** ACCEPTED

Conversation Understanding is one application of a reusable stateless Cognitive Processing model. Durable state remains owned by the invoking domain.

## CU-05 — One Cognitive Profile, not three profile systems
**Status:** ACCEPTED

Do not maintain separate Context Profile, Understanding Profile and Evaluation Profile architectures. Use one versioned, scope-aware Cognitive Profile containing:

```text
Cognitive Profile
├── Context Policy
├── Understanding Policy
└── Evaluation Policy
```

This supersedes the standalone Context Profile abstraction introduced during 01.

## CU-06 — Profile declares requirements, not implementation workflow
**Status:** ACCEPTED

The Cognitive Profile states **what must be understood/evaluated and under what requirements**, not how many LLM calls or processing stages must be used.

A compliant implementation may use deterministic parsing, classifier, embedding, one or more LLM calls, multi-stage processing, verification, alternate models or combinations thereof.

## CU-07 — Processing Purpose is distinct from User Intent
**Status:** ACCEPTED

Profile resolution cannot depend on User Intent before Understanding has discovered User Intent.

Known pre-processing routing inputs may include:

- Processing Purpose;
- Current State;
- Actor / Role;
- Scope;
- Trigger;
- Input metadata.

User Intent is an Understanding Result, not a prerequisite for selecting the processing definition.

## CU-08 — Cognitive Profile is a versioned canonical processing definition
**Status:** ACCEPTED

Cognitive Profile is a scope-aware, versioned, declarative processing definition. It is not Conversation State, Knowledge Object, Context Package or Understanding Result.

It may carry identity, version, scope, status, composition, policy fragments, provenance and supersession metadata.

## CU-09 — Effective Cognitive Profile may be composed
**Status:** ACCEPTED

Profile resolution may compose versioned profile fragments instead of requiring one prebuilt profile for every combination.

The effective composition used by a run must be auditable through component versions/snapshot/hash.

## CU-10 — Effective Cognitive Profile is not automatically a first-class domain object
**Status:** ACCEPTED

Do not create a new durable domain entity solely because a run has an effective profile composition. Execution/Evidence may preserve the effective snapshot/version/hash needed for reconstruction.

## CU-11 — Cognitive Processing Request is an invocation contract, not automatically a domain entity
**Status:** ACCEPTED

The invocation explicitly carries input/current state/actor/scope/trigger/processing purpose. Auditability alone is insufficient reason to introduce another first-class lifecycle object.

## CU-12 — Context, Understanding and Evaluation are distinct concerns
**Status:** ACCEPTED

Canonical processing chain:

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
```

## CU-13 — Evaluation is stateless qualification, not consequence authority
**Status:** ACCEPTED

Evaluation answers whether the interpreted facts satisfy an applicable policy/contract. It does not itself perform the resulting business/domain transition.

---

# B. L0 — Effective Operational Scope & Isolation

## FP-L0/01 — L0 exists as the foundation layer
**Status:** ACCEPTED

L0 is **Effective Operational Scope & Isolation**: it determines and records the effective operating space in which a Factory Protocol handoff is valid.

## FP-L0/02 — Canonical scope hierarchy
**Status:** ACCEPTED

```text
Organization / Tenant
→ Workspace
→ Project
```

Project is the primary working/domain scope.

## FP-L0/03 — Repository is Resource Context, not automatic Scope
**Status:** ACCEPTED

Repository, Branch, Revision, Environment and similar bindings belong to Resource Context unless explicitly promoted by a future architectural decision.

## FP-L0/04 — Application Default Rules are above scope but are not Scope/Tenant
**Status:** ACCEPTED

Application Default Rules may contain:

- overrideable defaults;
- non-overridable architectural/security invariants.

They SHALL NOT be modeled as another tenant/scope level.

## FP-L0/05 — Effective bindings are resolved before stateless processing
**Status:** ACCEPTED

Effective Scope may bind scope identity, resources, policies, Cognitive Profile and resolution provenance. Stateless services SHALL NOT invent/resolve their operating environment independently.

## FP-L0/06 — Isolation precedes semantic retrieval
**Status:** ACCEPTED

Canonical ordering:

```text
Tenant eligibility
→ Scope eligibility
→ Resource authorization
→ Policy eligibility
→ Semantic retrieval
→ Ranking
```

Semantic similarity SHALL NEVER override tenant/scope isolation. No implicit sibling-project context leakage.

## FP-L0/07 — Language Context is multidimensional
**Status:** ACCEPTED

The code/canonical technical language may remain English while the platform is multilingual. Processing context may distinguish interaction language, canonical artifact language, code language and source languages instead of forcing one global language field.

---

# C. L1 — Evidence Protocol

## FP-L1/01 — Evidence granularity
**Status:** ACCEPTED

Architecturally significant handoffs/transitions SHALL produce immutable Evidence. Evidence is not synonymous with generic logging.

## FP-L1/02 — Evidence Record
**Status:** ACCEPTED

Evidence records historical facts using immutable/versioned references and verifiable integrity. It may reference an Artifact without copying or transforming that Artifact into Evidence.

## FP-L1/03 — Authority and recording are separate
**Status:** ACCEPTED

The relevant Domain Authority owns the truth/fact being asserted. Evidence Infrastructure records/preserves proof; it SHALL NOT become business decision authority.

## FP-L1/04 — Evidence existence is not Evidence sufficiency
**Status:** ACCEPTED

```text
Evidence → proves/supports
Evaluation → assesses sufficiency/applicability
Domain Authority → decides consequence
```

Evidence presence SHALL NOT automatically authorize or accept a consequence.

---

# D. L2 — Provenance & Causality Protocol

## FP-L2/01 — L2 purpose
**Status:** ACCEPTED

L2 records historical semantic relationships: what something derives from, what caused it, produced it, triggered it, or what it used. It is common provenance infrastructure, not a business decision engine.

## FP-L2/02 — Controlled Relation Families
**Status:** ACCEPTED

Use a small canonical set of Relation Families with controlled/versioned specializations. Runtime ad-hoc relation types are prohibited. A specialization inherits and may refine, but SHALL NOT contradict, parent semantics.

## FP-L2/03 — Materialized relation is an immutable historical semantic fact
**Status:** ACCEPTED

Source, target and canonical relation semantics are immutable after creation. New knowledge appends new relation facts rather than rewriting history.

## FP-L2/04 — One authoritative direction; inverse is projection
**Status:** ACCEPTED

Each provenance/causality relation has one authoritative direction. The inverse may be query/navigation projection but is not independently persisted as another provenance fact.

## FP-L2/05 — Append-oriented temporal history
**Status:** ACCEPTED

Corrections preserve old history and append correcting/superseding facts rather than mutating the old fact.

## FP-L2/06 — Relation lifecycle vocabulary
**Status:** ACCEPTED

Canonical lifecycle semantics:

```text
PENDING → ACTIVE → RETRACTED
ACTIVE → RETRACTED → SUPERSEDED
```

- PENDING: candidate, not yet canonical fact;
- ACTIVE: currently canonical relation;
- RETRACTED: assertion withdrawn; replacement not required;
- SUPERSEDED: historically legitimate relation replaced by newer canonical relation.

Challenge/review alone does not automatically demote ACTIVE.

## FP-L2/07 — Activation authority belongs to relation semantics
**Status:** ACCEPTED

The authority contract required to activate a relation is part of the canonical relation definition. Domain Authority owns semantic truth; Provenance Infrastructure owns recording/integrity/lifecycle mechanics/retrieval.

## FP-L2/08 — Relation lifecycle and Evidence Assurance are separate axes
**Status:** ACCEPTED

Evidence degradation does not automatically retract/supersede a relation. Evidence assurance is represented through immutable Evaluation Results; current assurance is a projection over applicable evaluations. Domain Authority decides lifecycle consequence.

A relation may therefore remain ACTIVE while latest evidence assurance is DEGRADED/INSUFFICIENT.

---

# E. L3 — Artifact Protocol core

## FP-L3/01 — Artifact is first-class
**Status:** ACCEPTED

Artifact is a first-class logical identity, not merely a file/blob/result label.

## FP-L3/02 — Artifact Version is immutable
**Status:** ACCEPTED

A logical Artifact may have immutable versions. Historical references SHALL point to concrete immutable versions where historical reproducibility matters.

## FP-L3/03 — Artifact identity is semantic-purpose + contract based
**Status:** ACCEPTED

Content similarity is not Artifact identity. A radically changed document may remain a new version of the same Artifact if it continues the same semantic purpose under the same Artifact Contract. A semantically different purpose is a different Artifact even when derived from the first.

## FP-L3/04 — Understanding may assist classification but is not Artifact authority
**Status:** ACCEPTED

Artifact identity/version classification MAY require semantic Understanding. Understanding SHALL NOT create the version/identity consequence directly. Evaluation applies the applicable Artifact Contract/versioning policy; Artifact Domain Authority owns NEW_VERSION / NEW_ARTIFACT / review consequence.

Deterministic cases need not invoke LLM Understanding.

## FP-L3/05 — Immutability and stateful governance are independent
**Status:** ACCEPTED

Do not label the Artifact itself simply stateful/stateless. Artifact Contract determines whether durable governance/lifecycle tracking is required around an immutable Artifact Version.

Mutable review/approval status belongs to separate governance/lifecycle records when required; Artifact Version content remains immutable.

## FP-L3/06 — Artifact ↔ Evidence separation
**Status:** ACCEPTED

An Artifact Version may support one or many Evidence records without becoming Evidence and without `is_evidence` mutation. Challenging Evidence does not mutate the referenced Artifact Version.

## FP-L3/07 — Artifact ↔ Knowledge separation
**Status:** ACCEPTED

Artifact and Knowledge are independent first-class concepts. A complete Artifact Version SHALL NOT transform into or automatically become a Knowledge Object.

Knowledge may be derived from/supported by/reference immutable Artifact Versions through governed publication and explicit provenance.

## FP-L3/07-A — Knowledge extraction is semantic, not mechanical chunking
**Status:** ACCEPTED

Do not mechanically split a document and call chunks Knowledge. Identify semantically independent assertions/units. One Knowledge Object may originate from one sentence, several paragraphs, or multiple parts of an Artifact.

## FP-L3/08 — Knowledge Candidate
**Status:** ACCEPTED

Knowledge Candidate is a structured, immutable/provenance-linked potential knowledge unit that is not yet canonical Knowledge. Do not create a large state machine solely because a candidate exists.

Understanding may identify/classify a candidate but SHALL NOT own publication authority.

## FP-L3/09 — Knowledge Publication Resolution
**Status:** ACCEPTED

Publication is not binary ACCEPT/REJECT. Evaluation resolves semantic relation to existing canonical Knowledge using controlled outcomes:

- CREATE;
- REVISE;
- CONFIRM;
- DUPLICATE;
- CONFLICT;
- REJECT.

Publication Resolution and Publication Consequence are distinct. Domain Authority owns the consequence and may still require governance approval.

## FP-L3/10 — Knowledge conflict stability
**Status:** ACCEPTED

CONFLICT detection SHALL NOT automatically weaken/overwrite current ACTIVE Knowledge.

Forbidden automatic conflict rules:

- last writer wins;
- higher LLM confidence wins;
- newer Artifact wins.

Current ACTIVE Knowledge remains canonical until appropriate authority resolves the conflict.

A dedicated stateful Knowledge Conflict Case is not required by default merely to preserve auditability; existing Candidate/Knowledge/Evaluation/Evidence/Provenance/Authority results may represent the history. When explicit authority routing is required, Claim provides the cross-boundary subject.

## FP-L3/11 — Artifact Contract
**Status:** ACCEPTED

Every canonical Artifact Type operates under a versioned Artifact Contract defining at least:

- qualification;
- semantic purpose/type;
- identity policy;
- versioning policy;
- persistence policy;
- integrity requirements;
- governance/lifecycle policy;
- governance/lifecycle authority;
- publication/downstream rules where applicable.

Artifact Infrastructure SHALL NOT invent these semantics ad hoc at runtime.

## FP-L3/12 — Materialization & Payload
**Status:** ACCEPTED

Artifact Version is the canonical metadata/identity record; it is not necessarily the blob itself. Payload may be inline or externally stored as immutable content. Artifact Version references payload using stable reference and content digest. The logical Artifact model is storage-technology independent.

## FP-L3/13 — Artifact Integrity
**Status:** ACCEPTED

Persistent Artifact Version content must have verifiable integrity.

```text
same Artifact Version = same immutable content identity
```

Different payload means a new Version or integrity failure, never silent in-place modification.

## FP-L3/14 — Composition & Dependencies
**Status:** ACCEPTED

Composite Artifacts may reference other concrete immutable Artifact Versions. Do not build a second Artifact dependency graph; represent dependency/derivation using L2 Provenance/Causality relations such as `used` and `derived_from`.

Do not depend on mutable `latest` where immutable historical identity is required.

## FP-L3/15 — Artifact Applicability
**Status:** ACCEPTED

Historical legitimacy and present-purpose applicability are different. Applicability may be determined through immutable Evaluation Result over Artifact Version + intended use + current context/state + scope/policy.

Do not mutate Artifact Version with generic VALID/INVALID status.

## FP-L3/16 — Retention, Availability & Scope
**Status:** ACCEPTED

Historical Artifact identity/provenance is distinct from physical payload retention/availability. Policy may archive/remove payload without rewriting historical identity/provenance.

Artifact use is L0 scope-bound. L3 SHALL NOT create a second authorization engine.

## FP-L3/17 — Protocol Boundary
**Status:** ACCEPTED

L3 may recognize an unresolved condition requiring external/domain authority resolution, but L3 SHALL NOT own cross-domain authority resolution. The subject crosses into L4 communication semantics.

---

# F. Result / Outcome / Projection / Claim / Resolution

## FP-X/01 — Result, Outcome and Projection are distinct
**Status:** ACCEPTED

- **Result:** concrete output of processing/execution, e.g. Understanding Result, Evaluation Result, Execution Result.
- **Outcome:** domain-interpreted consequence, e.g. Mission Outcome, Knowledge Publication Outcome.
- **Projection:** controlled representation prepared for another domain, e.g. Conversation Projection.

Do not name all three `Result`.

## FP-X/02 — Claim may be first-class
**Status:** ACCEPTED

Claim may be a first-class, scope-bound governed assertion when ambiguity/conflict requires explicit responsibility/decision authority. Claim carries enough semantics to identify who/what authority is required.

A deterministic conflict does not require ceremonial Claim creation.

## FP-X/03 — Claim is not L3 resolution mechanism
**Status:** ACCEPTED

Claim belongs as a payload/subject that can cross the protocol boundary when authority resolution is required.

## FP-X/04 — Resolution is one interaction pattern
**Status:** ACCEPTED

Resolution is not the definition of L4. Resolution Request/Result is one Factory Message interaction pattern among many.

---

# G. L4 — Factory Message Protocol

## FP-L4/01 — L4 is Factory Message Protocol
**Status:** ACCEPTED

L4 is a general Factory Message Protocol capable of transporting multiple interaction types. It is not a Resolution-only protocol.

## FP-L4/02 — Factory Message is used at genuine domain/protocol boundaries
**Status:** ACCEPTED

Do not turn every internal method/service call into a Factory Message. Factory Message is required when information crosses a real domain/protocol boundary.

## FP-L4/03 — Envelope / Delivery-Interaction / Payload separation
**Status:** ACCEPTED

Conceptual message structure:

```text
Factory Message
├── Envelope
├── Delivery / Interaction Semantics
└── Payload Contract
```

Payload may carry Input/Message, Result, Outcome, Projection, Claim, Resolution Request/Result and future domain-specific payloads without redefining the common protocol.

## FP-L4/04 — L4 Transport owns A→B communication information at its level
**Status:** ACCEPTED

L4 handles information required to move a message from logical A to logical B and applies L4 communication authorization. It SHALL NOT absorb all business/domain authorization or responsibilities of other layers.

## FP-L4/05 — Layer responsibility isolation
**Status:** ACCEPTED

Each protocol layer owns its own responsibility and need not know the internal implementation/responsibility of lower layers.

## FP-L4/06 — Packet is layered and directly interpretable at each relevant level
**Status:** ACCEPTED

The complete packet carries layered semantics; information required at a given layer should be directly readable/interpretable at that level rather than requiring knowledge of unrelated lower-layer internals.

## FP-L4/07 — Enrich only when a boundary creates a relevant new fact
**Status:** ACCEPTED

Do not fabricate Evidence/Artifact on every hop. A domain/boundary produces or forwards information belonging to its responsibility; a layer is enriched only when a relevant new fact exists.

---

# H. FactoryIP

## FIP-01 — FactoryIP names the complete L0–L4 communication stack
**Status:** ACCEPTED

FactoryIP is the Factory domain/protocol-boundary communication model/stack. It is not merely routing and not a CRUD API.

## FIP-02 — Factory Packet is the layered carried unit
**Status:** ACCEPTED

The complete carried unit may be called Factory Packet. It contains the layered FactoryIP semantics and payload; FFS resolves delivery without redefining the packet semantics.

## FIP-03 — FactoryIP Node is a LAN-addressable logical service boundary
**Status:** ACCEPTED

Node is the logical addressable service boundary through which a participant exposes FactoryIP services.

## FIP-04 — Node is not Domain/Service/Process/Deployment/Instance synonym
**Status:** ACCEPTED

A domain may be represented through a Node, but the concepts are not identical. Multiple physical instances do not automatically create multiple logical Nodes. Internal deployment topology is not Factory LAN topology.

## FIP-05 — No Internal Reach-Through
**Status:** ACCEPTED

Another Node/external adapter SHALL NOT reach through the FactoryIP boundary to mutate canonical internal state directly.

## FIP-06 — Published semantic services only
**Status:** ACCEPTED

Cross-Node access occurs through published semantic services. FactoryIP SHALL NOT degrade into generic database/CRUD access.

## FIP-07 — External protocols are adapters, not alternate internal authority paths
**Status:** ACCEPTED

MCP, HTTP, WebSocket and similar technologies may expose/access services, but they SHALL NOT bypass FactoryIP canonical Node boundaries. MCP is an external/technical access protocol, not a replacement for FactoryIP.

## FIP-08 — Factory Chat is an independent FactoryIP Node/boundary
**Status:** ACCEPTED

Factory Chat must be addressable for inbound/outbound communication, while remaining UI/interaction boundary rather than Runtime and without owning Conversation canonical state.

## FIP-09 — Conversation is an independent FactoryIP Node
**Status:** ACCEPTED

Conversation is represented on the Factory LAN through its own logical Node/service boundary.

## FIP-10 — Conversation semantic service families
**Status:** ACCEPTED

Canonical service families:

- `conversation.interaction` — accepts Conversation-relevant interactions semantically;
- `conversation.context` — provides purpose-bound authoritative Conversation context;
- `conversation.projection` — accepts/produces controlled representation of external-domain facts in Conversation semantics.

## FIP-11 — Conversation CRUD/state mutation services are forbidden as canonical FactoryIP semantics
**Status:** ACCEPTED

Do not expose generic `conversation.create/update/delete`, `message.create/update`, or external `state.set/transition` authority as canonical FactoryIP service semantics.

---

# I. Factory Fabric Service (FFS)

## FFS-01 — Name and role
**Status:** ACCEPTED

**Factory Fabric Service (FFS)** is the FactoryIP routing/name-resolution control-plane concept. It maps logical FactoryIP identity/service to transport binding/target.

## FFS-02 — FactoryIP defines communication; FFS resolves delivery
**Status:** ACCEPTED

FFS SHALL NOT redefine FactoryIP semantics. Changing future routing/discovery implementation must not require changing the FactoryIP protocol model.

## FFS-03 — FFS is control plane, not data-plane proxy
**Status:** ACCEPTED

Factory Packets do not flow through FFS. FFS provides registry/resolution/communication-policy information; transport performs delivery using the resolved target.

## FFS-04 — Logically authoritative, physically not necessarily singleton
**Status:** ACCEPTED as conceptual direction; MVP simplification controls implementation

There is one logical authoritative FFS view. Physical HA/replication may exist later without creating competing logical authorities.

## FFS-05 — MVP FFS is part of AI Bridge and may be static/thin
**Status:** ACCEPTED

MVP does not require separate service-mesh infrastructure. Static configuration/resolution is acceptable.

## FFS-06 — HA is not an MVP goal
**Status:** ACCEPTED

Dynamic discovery, endpoint leases, heartbeat infrastructure, load balancing, HA clustering/failover are not mandatory MVP scope. They remain future evolution possibilities.

---

# J. Zoning / firewall

## ZONE-01 — Use Zoning rather than overlapping Envelope Authority
**Status:** ACCEPTED

Avoid two competing communication-authorization models. Zoning is the FactoryIP/L4 communication-policy mechanism.

## ZONE-02 — Zoning answers identity-to-identity communication permission
**Status:** ACCEPTED

Zoning determines whether one FactoryIP identity may communicate with another. It does not interpret payload business semantics and is not domain/business authorization.

## ZONE-03 — Detailed Zoning is deferred until topology is known
**Status:** ACCEPTED / DEFERRED DETAIL

First determine reviewed Nodes, their published services and required communication paths. Derive detailed zones afterward.

## ZONE-04 — Firewall principle
**Status:** DIRECTION ACCEPTED; exact policy OPEN

Firewall-style communication control is the baseline direction. Exact deny-by-default/service-level policy remains open for final topology/Zoning review and SHALL NOT be falsely recorded as already approved.

---

# K. AI Kernel boundary

## KERNEL-01 — AI Kernel is not Cognitive Processing
**Status:** ACCEPTED / terminology correction

AI Kernel is the post-admission operational execution core, not Conversation Understanding/Cognitive Processing/CSE/Mission Resolution.

## KERNEL-02 — Kernel executes; it does not decide
**Status:** ACCEPTED / reinforced invariant

Business/domain decision authority remains outside Kernel.

## KERNEL-03 — Context construction is outside Kernel
**Status:** ACCEPTED

Kernel consumes an already prepared immutable Context Package. Context Builder/Assembly is not Kernel internal state or a Kernel Manager.

---

# L. Section boundaries and sequencing

## SCOPE-02/03-01 — 02 and 03 are distinct review scopes
**Status:** ACCEPTED

02 = Conversation Understanding.

03 = Conversation State & Mission Resolution.

Concrete Conversation State axes, CSE transition rules, Mission readiness and Mission Resolution outcome semantics SHALL NOT be silently re-approved/redesigned in 02 merely because the current Constitution combines them.

## SEQ-01 — Factory Protocol foundation blocks later Mission/MSM convergence
**Status:** ACCEPTED

L0–L4, FactoryIP, Node model and FFS must be constitutionalized as baseline before later Mission/MSM convergence relies on them. Later domains are integrated into the established FactoryIP foundation section-by-section.

## SEQ-02 — Do not integrate unreviewed future domains into Factory LAN
**Status:** ACCEPTED methodology

Only reviewed/known domains and services are added to the LAN model. Do not invent Nodes/services for later course sections before those sections are reviewed.

---

# M. Explicit OPEN / DEFERRED items — MUST NOT be converted into approvals

1. Final owner/Node of Context Assembly.
2. Concrete final consumer of `conversation.context`.
3. Profile-resolution ambiguity/fallback/clarification policy unless separately approved later.
4. Final canonical schema details of Understanding Result beyond the accepted semantic distinctions.
5. Exact reusable Evidence Evaluation capability contract beyond accepted Evaluation separation.
6. Exact final Zoning rule set, including whether final policy is deny-by-default and exact service granularity.
7. Remaining FactoryIP Nodes/services for domains not yet reviewed.
8. Concrete Conversation State/CSE/Mission Resolution model — belongs to 03.
9. Detailed HA/dynamic FFS architecture — future, not MVP.
10. Any implementation schema/table/API choice not explicitly approved as architecture.

---

# N. Non-loss invariants for closure

Codex and final closure review SHALL prove that the constitutionalization preserves every ACCEPTED entry above or explicitly documents a Product Owner-approved supersession. In particular, closure fails if it:

- reintroduces standalone Context Profile beside Cognitive Profile;
- treats User Intent as pre-Understanding routing input;
- grants Understanding/Evaluation/Kernel authority to mutate business state;
- permits semantic retrieval before tenant/scope eligibility;
- collapses Evidence, Artifact and Knowledge into one object model;
- treats complete Artifacts as AKB Knowledge by default;
- removes Knowledge Publication Resolution outcomes;
- uses last-writer/newest-artifact/highest-confidence conflict resolution;
- mutates Artifact Version content/status for applicability/evidence use;
- creates a second Artifact dependency graph instead of L2;
- collapses Result/Outcome/Projection;
- makes Resolution the definition of L4;
- turns FactoryIP into CRUD/API semantics;
- equates Node with deployment/process/domain;
- allows internal reach-through;
- routes Factory Packets through FFS as mandatory proxy;
- treats Zoning as domain authorization;
- prematurely canonicalizes unreviewed 03+ domain topology.

This ledger is the approval-preservation source for the 02 closure package. Summaries may be shorter; they SHALL NOT be semantically weaker.
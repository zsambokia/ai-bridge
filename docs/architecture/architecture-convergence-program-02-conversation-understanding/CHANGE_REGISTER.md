# Architecture Convergence 02 — Change Register

Status: WORKING / NON-CANONICAL UNTIL CLOSURE
Owner: Product Owner
Branch: `architecture/02-conversation-understanding-convergence`

## Purpose

This is the live convergence register for Architecture Convergence 02. It records accepted architectural deltas while design continues. Acceptance here means Product Owner acceptance within the 02 working change-set; it does not make the change canonical on `main` until closure review and merge.

The detailed decision semantics live in `FOUNDATION_DECISIONS.md`. This register answers a different question: **what changes relative to the current repository baseline must be carried forward?**

## Working rules

- Architecture first: understanding → architecture → decision → implementation.
- `main` remains canonical until closure and merge.
- Current implementation never overrides target architecture merely for compatibility.
- Accepted decisions, proposals, open questions, current implementation and target architecture remain explicitly separated.
- Cross-cutting foundation discovered during 02 must be constitutionalized before later Mission/MSM convergence treats it as baseline.
- The course boundary remains: 02 = Conversation Understanding; 03 = Conversation State & Mission Resolution.
- Zoning is finalized only after relevant FactoryIP Node + service topology is sufficiently known.

## Change-set summary

### CR-02-001 — Generalize Conversation Understanding into Cognitive Processing

**Change type:** REFINE / GENERALIZE

Replace a Conversation-only mental model with a reusable stateless Cognitive Processing model. Conversation Understanding becomes one application of the general model.

Required concepts include Cognitive Profile, Effective Cognitive Profile, Processing Purpose, Context Assembly, immutable Context Package, Understanding Result and Evaluation Result.

### CR-02-002 — Replace standalone Context Profile with Cognitive Profile

**Change type:** SUPERSEDE / GENERALIZE

The standalone Context Profile abstraction introduced during earlier convergence is superseded by a versioned, scope-aware Cognitive Profile containing Context Policy, Understanding Policy and Evaluation Policy. Effective profile composition remains auditable without automatically introducing another first-class domain object.

### CR-02-003 — Separate Processing Purpose from discovered User Intent

**Change type:** ADD INVARIANT

Profile resolution must use known invocation/routing facts; it cannot depend on User Intent before Understanding has produced that result.

### CR-02-004 — Make Understanding/Evaluation results explicit immutable outputs

**Change type:** ADD / REFINE

Understanding Result and Evaluation Result are structured immutable outputs. Understanding preserves observation/inference/assumption/reference/ambiguity distinctions. Evaluation applies the relevant contract/policy but does not own domain consequence.

### CR-02-005 — Introduce Factory Protocol L0

**Change type:** ADD FOUNDATION

Add L0 — Effective Operational Scope & Isolation. Canonical ownership hierarchy is Organization/Tenant → Workspace → Project. Repository/branch/revision/environment belong to Resource Context rather than automatically forming additional scope levels. Application Default Rules sit above scope resolution without becoming a tenant/scope.

L0 resolves effective scope/resource/policy/profile bindings before semantic retrieval. Semantic similarity cannot override isolation.

### CR-02-006 — Introduce Factory Protocol L1

**Change type:** ADD FOUNDATION

Add L1 — Evidence Protocol. Architecturally significant handoffs/transitions produce immutable Evidence. Evidence proves/supports historical facts; Evaluation assesses sufficiency/applicability; Domain Authority owns the consequence. Evidence Infrastructure records proof but does not become business authority.

### CR-02-007 — Introduce Factory Protocol L2

**Change type:** ADD FOUNDATION

Add L2 — Provenance & Causality Protocol. It records immutable historical semantic relations using controlled Relation Families/specializations, append-oriented history and explicit authority contracts.

Relation lifecycle and Evidence Assurance are separate axes. Accepted lifecycle vocabulary: PENDING, ACTIVE, RETRACTED, SUPERSEDED.

### CR-02-008 — Introduce Factory Protocol L3

**Change type:** ADD FOUNDATION

Add L3 — Artifact Protocol. Artifact is first-class logical identity with immutable Artifact Versions. Canonical model includes Artifact Contract, qualification/authority, stateful-vs-stateless governance selected by contract, materialization/payload, integrity, composition/dependencies, applicability, retention/availability/scope and protocol boundary.

Artifact Version is immutable; mutable approval/review lifecycle belongs in separate governance/lifecycle records where required.

### CR-02-009 — Separate Artifact, Evidence and Knowledge

**Change type:** ADD INVARIANTS

Artifact does not become Evidence by mutation and complete Artifact does not automatically become AKB Knowledge. Evidence may reference Artifact Versions. Knowledge Publication extracts semantically independent provenance-linked Knowledge Candidates/Objects under Knowledge authority.

Knowledge conflict does not use last-writer-wins, newest-artifact-wins or highest-LLM-confidence-wins.

### CR-02-010 — Separate Result, Outcome and Projection

**Change type:** ADD CROSS-CUTTING SEMANTICS

Result is a processing/execution output; Outcome is a domain-interpreted consequence; Projection is a controlled representation for another domain. Do not collapse these into one generic Result concept.

### CR-02-011 — Introduce Claim as governed assertion where required

**Change type:** ADD CROSS-CUTTING SEMANTICS

Claim may be first-class when disagreement/uncertainty requires explicit responsible decision authority. Straightforward deterministic conflict need not create a Claim merely for ceremony. Claim is not an L3 resolution mechanism.

### CR-02-012 — Introduce Factory Protocol L4 / Factory Message Protocol

**Change type:** ADD FOUNDATION

L4 is the Factory Message Protocol, not a Resolution-only layer. Factory Message separates common Envelope, Delivery/Interaction Semantics and Payload Contract. Payload types may include Input/Message, Result, Outcome, Projection, Claim and Resolution interactions.

Factory Messages are required at genuine domain/protocol boundaries, not for arbitrary internal method calls. Each protocol layer remains responsible for its own semantics.

### CR-02-013 — Introduce FactoryIP

**Change type:** ADD PLATFORM FOUNDATION

FactoryIP is the name of the complete L0–L4 Factory communication stack and semantic inter-domain communication model. It is not CRUD/API semantics.

### CR-02-014 — Introduce FactoryIP Node model

**Change type:** ADD PLATFORM FOUNDATION

FactoryIP Node is a stable LAN-addressable logical service boundary, distinct from Domain/component/process/deployment/instance. Nodes publish semantic services and hide internal implementation/canonical state mechanics.

**No Internal Reach-Through:** another Node or external adapter cannot directly mutate internal canonical state across the boundary.

### CR-02-015 — Position external protocols as adapters to FactoryIP

**Change type:** REFINE BOUNDARY

MCP/HTTP/WebSocket and similar technologies may expose/access services but do not replace or bypass FactoryIP authority boundaries. MCP remains an external/integration protocol; canonical internal Factory communication follows FactoryIP semantics.

### CR-02-016 — Define Factory Chat as FactoryIP Node/boundary

**Change type:** REFINE 00/01 BASELINE

Factory Chat is addressable as its own FactoryIP interaction Node/boundary while remaining UI/interaction boundary, not Runtime and not owner of Conversation canonical state.

### CR-02-017 — Define Conversation as FactoryIP Node

**Change type:** REFINE 01/02 BASELINE

Conversation exposes semantic service families:

- `conversation.interaction`
- `conversation.context`
- `conversation.projection`

Do not expose generic Conversation/message CRUD or external state mutation as canonical FactoryIP semantics. Concrete consumer of `conversation.context` remains open until Context Assembly ownership is designed.

### CR-02-018 — Introduce Factory Fabric Service (FFS)

**Change type:** ADD PLATFORM FOUNDATION

FFS is FactoryIP routing/name-resolution control plane. It resolves logical FactoryIP identity/service to transport binding/target. Factory Packets do not flow through FFS; it is not a data-plane proxy.

MVP: thin/static, part of AI Bridge, no mandatory dynamic discovery/leases/heartbeats/load balancing/HA clustering. HA remains future context, explicitly not MVP scope.

### CR-02-019 — Introduce Zoning as FactoryIP communication policy concept

**Change type:** ADD FOUNDATION / DEFER DETAILED POLICY

Prefer one Zoning/firewall model over overlapping Envelope Authority. Zoning answers whether one FactoryIP identity may communicate with another; it does not replace domain authorization or interpret payload business semantics.

Detailed Zoning is intentionally deferred until Node + published-service topology is known. Firewall thinking is baseline; exact deny-by-default policy remains to be explicitly closed.

### CR-02-020 — Correct AI Kernel terminology and boundary

**Change type:** CORRECT / CONVERGE

AI Kernel is not Cognitive Processing. It is the post-admission operational execution core after Operational Foundation admits an immutable Execution Request. The Kernel executes; it does not decide. Context construction remains outside Kernel; Kernel consumes immutable prepared Context Package.

### CR-02-021 — Preserve 02/03 course responsibility boundary

**Change type:** MOVE / DEFER

Concrete Conversation State axes, CSE transition rules, Mission readiness and Mission Resolution outcome semantics belong to 03 review. Their presence in the current combined Article IV does not make them silently re-approved by 02.

### CR-02-022 — Make Factory Protocol foundation a blocker for later Mission/MSM convergence

**Change type:** GOVERNANCE / SEQUENCING

L0–L4, FactoryIP, Node model and FFS must become canonical baseline before later Mission/MSM architecture relies on them. Later sections integrate their domains into this foundation rather than redesigning the communication substrate ad hoc.

## Explicit closure blockers

1. Evidence-backed completeness audit against the entire 02 training/review history.
2. Existing-Constitution impact matrix: ADD / REFINE / SUPERSEDE / MOVE / NO CHANGE.
3. Existing canonical diagrams impact review.
4. Resolve any accepted decisions not yet represented in `FOUNDATION_DECISIONS.md`.
5. Reconcile exact naming and definitions across Change Register, Decision Register and Constitution Amendment.
6. Perform 03-scope leakage audit.
7. Produce final section Mermaid only after the above review.
8. Product Owner final closure approval.

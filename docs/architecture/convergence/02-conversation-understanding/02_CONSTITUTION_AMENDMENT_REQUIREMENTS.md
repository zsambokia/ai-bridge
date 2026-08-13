# 02 — Constitution Amendment Requirements

Status: **APPROVED AMENDMENT SPECIFICATION**

This document specifies what the canonical architecture must express after the section-02 convergence is applied. It intentionally does not claim exhaustive repository coverage; Codex must perform that traversal before and after amendment.

## 1. Conversation / pre-Mission architecture

The Constitution must remove or amend any rule that makes Conversation Understanding a stateful business authority. It must express the separation between durable Conversation/Conversation State and stateless cognitive processing.

Any numeric `0–100 maturity` model or mandatory single linear Conversation progression that conflicts with the approved 00/01 model must be removed/replaced by the approved semantic-state, lifecycle-status and readiness-condition model.

`Knowledge Recording` must not be a Conversation lifecycle state when it represents governed Knowledge Publication. `Mission Evaluation` must not be a Conversation lifecycle state when it represents the Mission Resolution boundary.

## 2. Cognitive Processing constitutionalization

Canonical architecture must define:

- stateless Context Assembly, Understanding and Evaluation responsibilities;
- immutable Context Package, Understanding Result and Evaluation Result boundaries;
- Cognitive Profile as a versioned processing contract;
- Effective Scope/Profile/Policy resolution before stateless processing;
- the invariant `Understanding/Evaluation do not own domain consequence`;
- applicability/reprocessing semantics for historical immutable results.

The canonical diagrams must not place Cognitive Processing inside the AI Kernel. The AI Kernel remains post-admission operational execution infrastructure.

## 3. Factory Protocol L0–L4

The Constitution must define each layer explicitly. It is insufficient to define only `FactoryIP = L0–L4` without defining the layers themselves.

### L0
Define Effective Operational Scope & Isolation, including the separation of Scope identity from resolved resource/policy/profile bindings and provenance.

### L1
Define Evidence as immutable proof/support, not logging or authority; domain-fact ownership versus Evidence Infrastructure ownership; evidence sufficiency evaluation; integrity and retrieval requirements.

### L2
Define the Provenance/Causality Graph, Relation Registry/Definition, relation family/specialization semantics, authoritative direction, append-only lifecycle, authority ownership, activation evidence contracts, evidence challenge/re-evaluation, assurance outcomes, and conditional promotion from typed edge to first-class Relation Record.

### L3
Define Artifact Contract, stable Artifact Identity, immutable Artifact Version, payload separation, integrity, identity/version qualification, lifecycle/governance ownership, Evidence use by reference, and the Artifact → Knowledge Candidate → Publication Resolution boundary.

### L4
Define the Transport Layer for semantic boundary communication and the Factory Packet. Do not turn L4 into a generic internal service-call wrapper.

## 4. FactoryIP / Factory LAN

Canonical architecture must define:

- FactoryIP as the complete L0–L4 semantic communication stack;
- Factory Packet as the transported unit;
- FactoryIP Node as a logical, addressable service boundary;
- Node identity ≠ service identity ≠ endpoint/location;
- semantic published services rather than CRUD reach-through;
- the no-internal-reach-through invariant for external adapters;
- FFS as resolution/control plane, not data-plane proxy;
- Zoning as the transport-level communication permission mechanism, separate from domain authorization;
- zoning finalization only after topology is known.

The Constitution must not prematurely prescribe an MVP-disproportionate distributed service mesh, active-active FFS cluster or dynamic lease system.

## 5. Conversation FactoryIP boundary

Canonical diagrams/contracts must expose the Conversation Node through semantic service families:

- `conversation.interaction`
- `conversation.context`
- `conversation.projection`

The architecture must forbid direct cross-domain CRUD/state mutation of Conversation internals.

The concrete consumer(s) of `conversation.context` may remain unresolved until the Context Assembly/domain topology is finalized; documentation must mark this as an explicit open topology question rather than inventing a dependency.

## 6. Knowledge architecture

Existing AKB documentation must be reconciled so that:

- a document/Artifact is not itself automatically a Knowledge Object;
- Knowledge is represented as semantically independent, versioned, provenance-linked units;
- Knowledge Candidate is pre-publication and non-canonical;
- Publication Resolution distinguishes `CREATE`, `REVISE`, `CONFIRM`, `DUPLICATE`, `CONFLICT`, `REJECT`;
- publication consequence belongs to Knowledge Domain Authority;
- conflict detection does not automatically overwrite/retract canonical Knowledge.

Any older language saying an approved Artifact simply “becomes” a Knowledge Object must be amended to the publication/extraction model.

## 7. Resolution / Claim

Canonical cross-cutting architecture must reserve a Resolution Protocol boundary for unresolved authority work. Claim must be modeled as one governed Resolution Subject, not as the universal representation of all unresolved cases.

The final placement/naming of Resolution Protocol within the broader protocol/domain documentation may be chosen during Codex amendment if repository structure suggests a cleaner canonical home, but its semantics must remain consistent with the approved decision register.

## 8. Existing constitutions and diagrams to reconcile

Codex must at minimum inspect and reconcile the documents covering:

- root Architecture Constitution;
- Conversation-to-Mission / Conversation architecture;
- AI Kernel architecture;
- Scope architecture;
- AKB / Knowledge object and lifecycle architecture;
- Evidence architecture;
- Operational Foundation / Execution / Provider architecture where FactoryIP or protocol boundaries affect handoffs;
- canonical architecture diagrams and indexes/READMEs/ADRs that declare conflicting or superseded rules.

This is a minimum list, **not** an exhaustive file list.

## 9. Amendment quality bar

After amendment there must be one coherent target architecture, not a new document layered on top of contradictory old rules. Codex must update, supersede or explicitly deprecate conflicting canonical text and diagrams.

No backward-compatibility wording may preserve an architecturally rejected concept solely because current code implements it. Current implementation must be reported separately as implementation gap.

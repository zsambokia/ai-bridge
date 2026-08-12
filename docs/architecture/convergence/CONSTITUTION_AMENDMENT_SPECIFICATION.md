# Constitution Amendment Specification

Status: Product Owner-approved target specification for Codex application
Companion: `CONSTITUTION_IMPACT_MATRIX.md`

## Purpose

This document describes WHAT must change in the canonical Architecture Constitution. It intentionally does not claim exact current repository section numbers. Codex owns repository traversal, exact placement, conflict discovery, amendment application and verification.

## Amendment A — Conversation and interaction boundary

The Constitution SHALL state that Factory Chat is an interaction/access boundary. It MAY own UI/session/preferences state, but SHALL NOT own canonical business state, create Missions directly, start workflows directly, or control the lifecycle of durable Conversation, Mission or Execution objects.

Conversation SHALL remain a durable first-class domain object. Conversation History and Conversation State SHALL be distinct. Conversation State SHALL be structured, controlled domain state representing current understanding, accepted decisions, active challenges, unresolved questions, readiness and lifecycle; it SHALL NOT be an unconstrained LLM summary.

Numeric 0-100 conversation maturity and a single mandatory linear progression SHALL be superseded by explicit semantic state, lifecycle status and readiness conditions. Knowledge Publication and Mission Resolution SHALL be separate governed boundaries rather than Conversation states.

## Amendment B — Cognitive Processing foundation

The Constitution SHALL introduce Cognitive Processing as a reusable stateless processing architecture. Conversation Understanding is one use of this architecture, not a separate stateful authority.

The canonical processing pattern SHALL be:

`Effective Scope/Profile -> Context Assembly -> immutable Context Package -> Understanding -> immutable Understanding Result -> Evaluation -> immutable Evaluation Result -> Domain Authority -> consequence/projection`.

Understanding SHALL distinguish explicit observations, inferences, assumptions, resolved references and ambiguities. Understanding SHALL never mutate canonical domain state. Historical interpretation validity SHALL be distinguished from applicability to a later intended consequence.

A Cognitive Profile SHALL be a versioned processing contract, not merely a prompt. It SHALL define at least Context Policy, Understanding Policy and Evaluation Policy. Effective profile resolution SHALL occur before stateless processing begins.

## Amendment C — Cross-cutting authority model

The Constitution SHALL consistently distinguish:

- Understanding: what does the input/context mean?
- Evaluation: how does that interpreted result qualify against a contract/policy?
- Domain Authority: what canonical consequence is authorized?

Result, Outcome and Projection SHALL be distinct terms. Infrastructure services SHALL not acquire domain authority merely because they record, evaluate, route or persist a fact.

## Amendment D — Factory Protocol / FactoryIP foundation

The Constitution SHALL introduce the Factory Protocol as a layered semantic communication foundation and `FactoryIP` as the canonical name of the complete L0-L4 stack.

The layers SHALL be defined individually, not merely referenced by name.

### L0 — Effective Operational Scope & Isolation

L0 SHALL bind the effective Organization/Workspace/Project scope, effective resource bindings, effective policy bindings, effective Cognitive Profile binding and resolution provenance required for the handoff. Stateless services SHALL NOT independently invent or resolve their operating scope.

### L1 — Evidence Protocol

L1 SHALL define Evidence as proof of architecturally significant facts/handoffs/transitions according to applicable contracts and policies. Evidence Records SHALL preserve historical facts, immutable/versioned references and verifiable integrity.

The domain owns the semantic fact; Evidence Infrastructure records proof. Evidence SHALL NOT be authority and SHALL NOT be presumed sufficient merely because it exists. Evidence sufficiency is evaluated; consequence remains with the relevant Domain Authority.

### L2 — Provenance & Causality Protocol

L2 SHALL define a logical provenance/causality graph between first-class objects. Evidence and provenance SHALL remain distinct: a relation states how objects are historically/causally connected; Evidence supports/proves the relevant fact.

Relation definitions SHALL be canonical, versioned and registry-governed. A small stable set of relation families MAY have controlled specializations. Every relation has one authoritative direction; inverse forms are query/navigation projections.

Materialized relations SHALL be append-only historical facts. Source, target and canonical semantics SHALL NOT be rewritten. Lifecycle SHALL support `PENDING`, `ACTIVE`, `RETRACTED`, `SUPERSEDED`. `PENDING` is a governance state, not a mandatory initial state.

Relation definitions SHALL declare activation authority, activation policy and Activation Evidence Contract. Activation MAY be deterministic or governed. Evidence challenge SHALL NOT automatically retract an active relation. Evidence assurance SHALL be represented by immutable Evaluation Results using canonical outcomes such as `SUFFICIENT`, `DEGRADED`, `INSUFFICIENT`, `INDETERMINATE`.

A relation is normally a typed graph edge. A first-class Relation Record SHALL be required only where the canonical Relation Definition requires independent identity, persistence, authority, evidence or lifecycle handling.

### L3 — Artifact Protocol

L3 SHALL define Artifact qualification by versioned Artifact Contract/policy. A producer cannot self-declare arbitrary output as canonical Artifact.

Artifact Identity SHALL be stable. Artifact Versions SHALL be immutable. Historical references SHALL target concrete Artifact Versions, not mutable `latest` identities. New version versus new Artifact SHALL be resolved by semantic purpose and the applicable Artifact Contract, using the standard Understanding -> Evaluation -> Authority pattern where semantic interpretation is needed.

The Artifact Contract SHALL define qualification, semantic purpose, identity/versioning policy, persistence, payload/materialization policy, integrity, governance/lifecycle and lifecycle authority.

Artifact Version SHALL be separable from payload storage. Persistent versions SHALL have verifiable content identity/integrity. Artifact Infrastructure owns materialization, persistence, integrity and version mechanics; contract-selected Domain Authority owns any semantic governance lifecycle.

Artifact SHALL NOT become Evidence merely because an Evidence Record references it. Artifact SHALL NOT become Knowledge merely because its content is approved.

### L4 — Transport / Factory Message Protocol

L4 SHALL define semantic communication across genuine domain/protocol boundaries. Not every internal function/service call is a FactoryIP handoff.

The complete carried unit SHALL be a `Factory Packet`. Each layer handles its own responsibility and SHALL NOT require interpretation of unrelated lower-layer semantics. Payloads MAY carry requests, results, claims, artifacts, resolution subjects and other canonical interaction types.

FactoryIP SHALL NOT be a CRUD API for domain internals.

## Amendment E — FactoryIP Node, services, FFS and Zoning

A FactoryIP Node SHALL represent a stable, addressable service boundary toward the Factory LAN. Node identity, service identity and technical endpoint/location SHALL be distinct concepts. A component/domain qualifies as a Node only when it exposes a meaningful stable cross-domain service boundary and can hide its internal implementation behind published contracts.

Published FactoryIP services SHALL be semantic services, not direct state mutation/CRUD endpoints. External adapters such as HTTP, MCP or WebSocket MAY bridge into FactoryIP but SHALL NOT bypass canonical Node/domain authority by reaching directly into internal persistence.

The initial Conversation Node service families SHALL include:

- `conversation.interaction`
- `conversation.context`
- `conversation.projection`

`Factory Fabric Service (FFS)` SHALL be the FactoryIP control-plane name/resolution mechanism mapping logical FactoryIP identity/service to the applicable transport binding/target. Factory Packet payload traffic SHALL NOT traverse FFS merely because FFS resolved the destination.

MVP FFS SHALL remain intentionally thin. Dynamic discovery, leases, active/passive HA, service-mesh behavior and similar advanced mechanisms MAY be added later when required; they are not required by the current constitutional baseline.

Zoning SHALL be the single canonical FactoryIP communication allow/deny mechanism. Detailed zone policy SHALL be finalized only after the Node/service topology is sufficiently complete.

## Amendment F — Scope architecture

The canonical durable scope hierarchy SHALL be `Organization -> Workspace -> Project`. Every durable domain object SHALL belong to exactly one effective Scope. Scope and Resource SHALL remain distinct: Project is a Scope; Repository and similar attached entities are Resources/bindings.

## Amendment G — Knowledge publication

Knowledge SHALL remain composed of independently identifiable, versioned semantic Knowledge Objects rather than whole documents.

An Artifact Version MAY be processed into one or more immutable, provenance-linked `Knowledge Candidate` objects. A Knowledge Candidate is not canonical Knowledge and Cognitive Processing SHALL NOT publish directly into the AKB.

Publication Evaluation SHALL support at least `CREATE`, `REVISE`, `CONFIRM`, `DUPLICATE`, `CONFLICT`, `REJECT`. Publication Resolution SHALL remain separate from Publication Consequence. `CONFLICT` SHALL NOT automatically replace active canonical Knowledge.

## Amendment H — Claim and Resolution

The Constitution SHALL introduce `Claim` as a first-class governed assertion where independent scope, authority, applicable policy/contract, provenance and resolution obligation are required.

Claim SHALL NOT be treated as the complete resolution mechanism. It is one Resolution Subject. Resolution SHALL be extensible to subjects such as Claim, Decision Request, Input Request and future governed unresolved subjects. Resolution identifies the required authority, supplies relevant context/evidence, captures an authoritative Resolution Result and returns the authorized consequence to the originating domain/projection path.

Resolution interactions MAY be carried by FactoryIP/L4; L4 itself is not limited to Resolution.

## Amendment I — AI Kernel alignment

The existing AI Kernel role as technical execution core SHALL be preserved. The Kernel begins after Operational Foundation admission of an immutable Execution Request and owns technical execution lifecycle, capability/provider coordination, leases/recovery/telemetry/evidence/security as already canonically defined.

Hard invariant: `The Kernel executes; it does not decide.`

Cognitive Processing and business Context Assembly SHALL remain outside the Kernel. The Kernel consumes already-built immutable Context Packages. Capability-first, provider-independent execution SHALL be preserved. Provider SHALL remain a stateless definition; Provider Executor owns provider-specific runtime execution state.

## Amendment J — Governance

Architecture Convergence and Implementation Convergence SHALL remain separate governed programs. Architecture Convergence defines what AI Bridge SHALL be without deriving the target from accidental current-repository constraints. Implementation Convergence subsequently determines how the repository/runtime converges to the approved target.

Codex repository traversal SHALL be evidence gathering and amendment application, not a reopening of Product Owner-approved target architecture.

## Codex placement rule

Codex SHALL map these amendments into the existing canonical document structure with minimal duplication. Where an existing canonical section already owns the responsibility, Codex SHOULD amend that section rather than create a competing second constitution. New foundation documents MAY be created when no current canonical owner exists, but all canonical indexes/maps and diagrams must then be updated.
# Canonical Terminology Delta

Status: target terminology register for Architecture Convergence

This register prevents Codex from treating newly approved concepts as accidental synonyms of older repository terminology.

| Canonical term | Required meaning | Forbidden conflation |
|---|---|---|
| Cognitive Processing | Reusable stateless Context -> Understanding -> Evaluation processing architecture | stateful Conversation engine; AI Kernel |
| Cognitive Profile | Versioned processing contract defining Context/Understanding/Evaluation policy | prompt text; persona; provider configuration |
| Understanding Result | Immutable structured interpretation artifact | domain decision; state transition |
| Evaluation Result | Immutable qualification against contract/policy | domain authority consequence |
| Domain Authority | Owner authorized to create/change canonical domain consequence | evaluator; recorder; router |
| Effective Operational Scope | Pre-resolved scope/resource/policy/profile operating boundary | ad-hoc service lookup |
| Factory Protocol | Layered L0-L4 semantic communication foundation | ordinary HTTP/API stack |
| FactoryIP | Canonical name of complete L0-L4 Factory Protocol communication stack | FFS; a concrete network protocol implementation |
| Factory Packet | Complete carried unit across FactoryIP layers | payload alone; HTTP packet |
| L0 Scope & Isolation | Effective operational scope and isolation semantics | authorization UI/session state |
| Evidence Record | Verifiable proof record for a fact/handoff/transition | log line; provenance relation; authority decision |
| Provenance/Causality Relation | Typed semantic historical/causal connection between objects | Evidence itself |
| Relation Registry | Versioned canonical relation semantics/authority/evidence definitions | caller-created ad-hoc relation names |
| Artifact | Canonical qualified materialized result | every output; Evidence subtype; Knowledge Object |
| Artifact Identity | Stable logical identity across versions | mutable content record |
| Artifact Version | Immutable concrete materialization | latest alias |
| Artifact Contract | Versioned behavioral contract for Artifact qualification, identity, persistence, integrity and governance | MIME type; output schema alone |
| Knowledge Candidate | Immutable provenance-linked candidate semantic unit not yet canonical Knowledge | draft Knowledge Version; whole Artifact |
| Knowledge Publication Resolution | Semantic relation of candidate to canonical Knowledge | automatic AKB mutation |
| Claim | Governed assertion requiring independent authority/resolution handling | every statement; every request |
| Resolution Subject | Governed unresolved subject routed to authority | Claim only |
| FactoryIP Node | Stable addressable service boundary on Factory LAN | every module/process/class |
| Published Service | Semantic capability exposed by a Node | CRUD endpoint; direct state setter |
| Factory Fabric Service (FFS) | FactoryIP name/service resolution control plane | packet proxy; data plane; FactoryIP itself |
| Zoning | Canonical FactoryIP communication allow/deny policy | domain authorization; separate envelope authority |
| Scope | Durable ownership/isolation boundary (Organization/Workspace/Project) | Resource |
| Resource | Entity bound into a Scope, e.g. Repository | Project/Workspace/Organization |

## Explicit supersession / removal guidance

Codex SHALL search for older terminology that encodes conflicting semantics, not merely identical words. In particular it SHALL investigate and either align, supersede or explicitly preserve:

- numeric Conversation maturity and mandatory linear Conversation progression;
- Conversation-owned Knowledge Recording;
- Conversation-owned Mission Evaluation;
- any stateful `Conversation Understanding` component that owns durable state;
- Context Builder represented as an AI Kernel manager/service if it performs business Context Assembly;
- Evidence used as a synonym for Artifact, log, provenance relation or authority decision;
- Provider used as a stateful runtime execution object rather than stateless definition;
- direct provider-name routing instead of Capability-based resolution;
- CRUD-like cross-domain APIs that bypass semantic FactoryIP service boundaries;
- external adapters that reach canonical domain persistence directly;
- any separate communication allow/deny authority that duplicates Zoning.

## New-delta evidence note

Product Owner evidence explicitly classifies Cognitive Profile, Factory Protocol L0-L4, FactoryIP, Artifact Contract, Claim and related terminology as newly created during the current convergence. Absence from historical `main` is expected and is not evidence that these concepts should be dropped.
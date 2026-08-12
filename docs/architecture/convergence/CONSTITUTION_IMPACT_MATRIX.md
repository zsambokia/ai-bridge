# Constitution Impact Matrix

Status: Product Owner approved convergence input
Purpose: normative change map for Architecture Convergence; repository traversal and completeness verification are delegated to Codex.

## Evidence classification

The Product Owner explicitly confirmed that the following terminology did not exist in the canonical architecture before the current convergence work: Cognitive Profile, Factory Protocol L0-L4, FactoryIP, Artifact Contract, Claim, and the related foundation model. These are therefore NEW CONSTITUTIONAL DELTA, not rediscovery or renaming of an existing canonical element.

## Disposition vocabulary

- ADD — introduce a new canonical rule/concept.
- REFINE — preserve the existing concept while making its boundary precise.
- SUPERSEDE — replace an existing canonical rule with the approved target.
- MOVE — preserve the concept but move ownership/responsibility.
- CORRECT — repair an inconsistency or incorrect placement.
- NO CHANGE — explicitly preserve the current rule.
- DEFER — intentionally leave the detail for a later architecture closure.

## Impact matrix

| ID | Approved convergence decision | Impact | Required constitutional treatment | Primary target area | Risk if missed |
|---|---|---|---|---|---|
| CIM-001 | Factory Chat is an interaction/UI boundary, not runtime/domain authority | REFINE | State explicit negative invariants | Conversation / Interaction | UI can accidentally own business state |
| CIM-002 | UI lifecycle must not control Conversation, Mission, or Execution lifecycle | ADD | Add lifecycle independence invariant | Conversation / Runtime | Closing UI could terminate durable work |
| CIM-003 | Conversation is a durable first-class domain object | REFINE | Preserve and strengthen ownership | Conversation | Transcript/session conflation |
| CIM-004 | Conversation history answers what was said; Conversation State answers what is currently understood | ADD | Define Conversation State separately from history | Conversation | Reinterpretation from raw history on every turn |
| CIM-005 | Conversation State is controlled structured state, not an LLM summary | SUPERSEDE | Remove summary-as-state semantics | Conversation State | Non-deterministic state drift |
| CIM-006 | Conversation State uses semantic state, lifecycle status, readiness conditions; numeric maturity is removed | SUPERSEDE | Replace numeric maturity/progression model | Conversation State | False precision and rigid progression |
| CIM-007 | Knowledge Recording is not a Conversation state | MOVE | Move to governed Knowledge Publication | Conversation / Knowledge | Conversation engine becomes knowledge authority |
| CIM-008 | Mission Evaluation is not a Conversation state | MOVE | Move to Mission Resolution boundary | Conversation / Mission | Conversation state machine creates missions implicitly |
| CIM-009 | Accepted decisions remain active while challenges/exploration are evaluated | ADD | Add challenge/proposal/supersession semantics | Conversation / Governance | Accepted decisions oscillate during exploration |
| CIM-010 | Conversation can close, defer, or be intentionally abandoned without being FAILED | ADD | Add lifecycle terminal/parking semantics | Conversation | Business discussion treated as execution failure |
| CIM-011 | Understanding is a general stateless capability, not a stateful Conversation authority | SUPERSEDE | Generalize Conversation Understanding into Cognitive Processing | Cognitive Processing | Hidden state and authority in AI interpretation |
| CIM-012 | Cognitive Processing works from immutable Context Package | ADD | Require immutable processing input | Cognitive Processing / Context | Non-reproducible AI decisions |
| CIM-013 | Understanding Result is immutable, structured, evidence-linked interpretation | ADD | Define first-class result contract | Cognitive Processing | Free-form interpretation cannot be audited |
| CIM-014 | Explicit observation, inference, assumption, resolved reference, ambiguity are distinct | ADD | Define interpretation categories | Cognitive Processing | Inference presented as fact |
| CIM-015 | Understanding is not Domain Authority | ADD | Add hard authority boundary | Cognitive Processing | AI interpretation mutates canonical state |
| CIM-016 | Historical validity of Understanding Result differs from later applicability | ADD | Add applicability evaluation rule | Cognitive Processing | Old interpretation reused after context changed |
| CIM-017 | Cognitive Profile is a versioned processing contract, not a prompt | ADD | Define Cognitive Profile | Cognitive Processing | Prompt configuration becomes implicit architecture |
| CIM-018 | Cognitive Profile contains Context, Understanding and Evaluation policies | ADD | Define profile composition | Cognitive Processing | Processing phases diverge across domains |
| CIM-019 | Profile resolution happens before stateless processing | ADD | Define Effective Cognitive Profile binding | L0 / Cognitive Processing | Services self-resolve hidden operating context |
| CIM-020 | Profile resolution failure due to configuration is a system/governance gap, not automatically a PO clarification | ADD | Define failure routing | Cognitive Processing | Internal config defects pushed to user |
| CIM-021 | Understanding -> Evaluation -> Domain Authority is the canonical consequence pattern | ADD | Add cross-cutting processing invariant | Architecture Constitution | Evaluation and authority collapse into one service |
| CIM-022 | Result, Outcome and Projection are distinct concepts | ADD | Define cross-cutting terminology | Architecture Constitution | Stored result confused with consequence/UI projection |
| CIM-023 | Factory Protocol L0 is Effective Operational Scope & Isolation | ADD | Add full L0 protocol constitution | Factory Protocol | No canonical scope at handoff boundaries |
| CIM-024 | L0 binds Organization/Workspace/Project identity, effective resources, policies and profile provenance | ADD | Define L0 contract | Factory Protocol L0 | Cross-scope leakage and hidden resolution |
| CIM-025 | Stateless services do not resolve their own scope/profile | ADD | Add negative invariant | Factory Protocol L0 | Non-deterministic operating environment |
| CIM-026 | Factory Protocol L1 is Evidence Protocol | ADD | Add full L1 protocol constitution | Factory Protocol | Evidence remains ad-hoc logging |
| CIM-027 | Evidence is created for architecturally significant handoffs/transitions according to contract/policy | ADD | Define evidence granularity | L1 | Either evidence explosion or audit gaps |
| CIM-028 | Evidence Record preserves historical facts, immutable/versioned refs and verifiable integrity | ADD | Define Evidence Record | L1 | Evidence cannot prove historical state |
| CIM-029 | Domain owns the fact; Evidence Infrastructure records proof | ADD | Define authority boundary | L1 | Evidence service becomes business authority |
| CIM-030 | Evidence is not automatically sufficient; Evaluation assesses sufficiency; Domain Authority owns consequence | ADD | Define sufficiency chain | L1 / Evaluation | Evidence auto-triggers state changes |
| CIM-031 | Factory Protocol L2 is Provenance & Causality Protocol | ADD | Add full L2 protocol constitution | Factory Protocol | No reconstructable causal chain |
| CIM-032 | Provenance/Causality Graph is a separate logical model between first-class objects | ADD | Define graph semantics | L2 | Evidence and provenance are conflated |
| CIM-033 | Canonical relation families use stable semantics plus controlled versioned specialization | ADD | Define Relation Registry model | L2 | Ad-hoc relation taxonomy |
| CIM-034 | Relations have one authoritative direction; inverse is query/navigation projection | ADD | Define direction invariant | L2 | Duplicate contradictory facts |
| CIM-035 | Materialized provenance relations are append-only historical facts | ADD | Define temporal semantics | L2 | History can be rewritten |
| CIM-036 | Relation lifecycle includes PENDING, ACTIVE, RETRACTED, SUPERSEDED | ADD | Define lifecycle semantics | L2 | No governed correction history |
| CIM-037 | PENDING is a governance state, not mandatory initial state | ADD | Define deterministic vs governed activation | L2 | Deterministic facts require artificial approval |
| CIM-038 | Relation activation authority is declared by canonical relation definition | ADD | Define authority contract | L2 | Producers self-authorize provenance facts |
| CIM-039 | Relation family may provide default authority; specialization may refine without violating parent semantics | ADD | Define authority inheritance | L2 | Inconsistent relation governance |
| CIM-040 | Each relation definition declares Activation Evidence Contract | ADD | Define evidence requirements | L2 | ACTIVE relation lacks proof contract |
| CIM-041 | Evidence challenge does not automatically retract relation | ADD | Separate evidence assurance from lifecycle | L2 | Loss of one proof rewrites canonical fact |
| CIM-042 | Evidence assurance is immutable Evaluation Result with canonical outcomes | ADD | Define SUFFICIENT/DEGRADED/INSUFFICIENT/INDETERMINATE | L2 | Second mutable assurance state machine |
| CIM-043 | Relation is normally typed edge; promote to first-class Relation Record only when registry contract requires it | ADD | Define representation rule | L2 | Every edge becomes heavyweight domain object |
| CIM-044 | Factory Protocol L3 is Artifact Protocol | ADD | Add full L3 protocol constitution | Factory Protocol | Outputs have no canonical lifecycle/identity model |
| CIM-045 | Output becomes canonical Artifact only when contract/policy qualifies it | ADD | Define Artifact Qualification | L3 | Producers self-declare canonical artifacts |
| CIM-046 | Artifact Identity is stable; Artifact Versions are immutable | ADD | Define identity/version split | L3 | Historical artifact content changes in place |
| CIM-047 | Historical references point to concrete Artifact Version, not mutable latest identity | ADD | Add reference invariant | L3 | Execution/context reconstruction breaks |
| CIM-048 | New version vs new Artifact is based on semantic purpose and Artifact Contract | ADD | Define versioning resolution | L3 | Unrelated outputs are versioned together |
| CIM-049 | Understanding may interpret semantic continuity but cannot decide Artifact identity/version consequence | ADD | Apply Understanding/Evaluation/Authority pattern | L3 | AI interpretation mutates artifact identity |
| CIM-050 | Artifact Contract is versioned and defines qualification, purpose, identity/versioning, persistence, integrity, governance/lifecycle and authority | ADD | Define Artifact Contract | L3 | Artifact behavior is implicit/ad-hoc |
| CIM-051 | Artifact Version is metadata/identity record; payload may be inline or external immutable content | ADD | Define materialization/payload split | L3 | Artifact model coupled to storage technology |
| CIM-052 | Persistent Artifact Version must have verifiable content integrity | ADD | Define digest/integrity invariant | L3 | Immutability cannot be verified |
| CIM-053 | Artifact Infrastructure owns storage/integrity/version mechanics; contract-selected Domain Authority owns governance lifecycle | ADD | Define ownership boundary | L3 | Central Artifact Manager becomes god service |
| CIM-054 | Artifact does not become Evidence; Evidence Record may reference Artifact Version for a proof purpose | ADD | Define Artifact-Evidence relation | L1/L3 | EvidenceArtifact subtype proliferation |
| CIM-055 | Artifact does not become Knowledge; Knowledge Publication extracts semantic Knowledge Candidates | ADD | Define Artifact-Knowledge relation | L3 / Knowledge | Whole documents are treated as atomic knowledge |
| CIM-056 | Knowledge Candidate is first-class, immutable, provenance-linked, but not canonical Knowledge | ADD | Define Knowledge Candidate | L3 / Knowledge | Understanding publishes directly to AKB |
| CIM-057 | Knowledge Publication Resolution outcomes: CREATE, REVISE, CONFIRM, DUPLICATE, CONFLICT, REJECT | ADD | Define publication resolution | Knowledge | Binary accept/reject loses semantic relation to existing knowledge |
| CIM-058 | Publication Resolution is not Publication Consequence | ADD | Keep Evaluation separate from Knowledge Authority | Knowledge | Evaluation directly mutates AKB |
| CIM-059 | Conflict does not automatically alter active canonical Knowledge | ADD | Define conflict invariant | Knowledge | New challenger silently replaces accepted knowledge |
| CIM-060 | Claim is a first-class governed assertion with scope, authority, policy, provenance and resolution obligation | ADD | Define Claim | Resolution / Governance | Unresolved assertions cannot be routed/audited |
| CIM-061 | Claim is one Resolution Subject, not the whole resolution mechanism | ADD | Define Resolution abstraction | Resolution / L4 | Claim model overloaded for inputs/decisions |
| CIM-062 | Resolution can also carry Decision Request, Input Request and future subject types | ADD | Define extensible Resolution Subject taxonomy | Resolution | Missing input and business choice forced into Claim semantics |
| CIM-063 | L4 is Transport / Factory Message Protocol; Resolution is one interaction carried by it | ADD | Add full L4 constitution | Factory Protocol | Transport conflated with one workflow |
| CIM-064 | FactoryIP is the canonical name for the complete L0-L4 communication stack | ADD | Define FactoryIP | Architecture Foundation | Protocol stack has no canonical identity |
| CIM-065 | Factory Packet is the carried unit across the FactoryIP stack | ADD | Define packet model | L4 | Layer metadata and payload lack common carrier |
| CIM-066 | FactoryIP is semantic inter-domain communication, not CRUD/API | ADD | Add negative invariant | L4 | Internal domain state exposed as CRUD endpoints |
| CIM-067 | FactoryIP is required for genuine domain/protocol boundary crossing, not every internal service call | ADD | Define boundary qualification | L4 | Protocol applied to every function call |
| CIM-068 | Each FactoryIP layer handles only its own responsibility and need not interpret lower-layer semantics | ADD | Define layer independence | L0-L4 | Cross-layer coupling |
| CIM-069 | External HTTP/MCP/WebSocket adapters may access FactoryIP services but cannot bypass canonical domain state | ADD | Define access-adapter boundary | FactoryIP | External adapter reaches directly into domain persistence |
| CIM-070 | FactoryIP Node is a stable addressable service boundary toward the Factory LAN | ADD | Define Node | FactoryIP | Internal modules are exposed as network topology |
| CIM-071 | Node identity, service identity and technical location are distinct | ADD | Define addressing model | FactoryIP | Logical service coupled to deployment location |
| CIM-072 | Node qualification requires stable service boundary, legitimate cross-node communication and hidden internal implementation | ADD | Define Node qualification | FactoryIP | Every component becomes a Node |
| CIM-073 | Node publishes semantic service contracts, not CRUD/state mutation endpoints | ADD | Define published-service invariant | FactoryIP | Domain authority bypassed |
| CIM-074 | Conversation Node publishes conversation.interaction, conversation.context, conversation.projection | ADD | Add initial service model | Conversation / FactoryIP | Conversation LAN boundary remains undefined |
| CIM-075 | Factory Fabric Service (FFS) resolves FactoryIP logical identity/service to transport binding/target | ADD | Define FFS | FactoryIP | Routing/name resolution becomes ad-hoc |
| CIM-076 | FFS is control plane; payload does not traverse FFS | ADD | Add data-plane separation | FactoryIP | FFS becomes bottleneck/proxy |
| CIM-077 | MVP FFS is intentionally thin; dynamic discovery/leases/HA/service mesh are not required baseline | DEFER | Preserve extension points without overbuilding MVP | FFS | Premature distributed infrastructure |
| CIM-078 | Zoning is the single canonical FactoryIP communication allow/deny mechanism | ADD | Define zoning purpose | FactoryIP | Multiple conflicting communication authorities |
| CIM-079 | Zoning is finalized after Node/service topology, not guessed domain-by-domain | DEFER | Require topology-first closure | FactoryIP | Policies encode incomplete architecture |
| CIM-080 | Scope Architecture uses Organization -> Workspace -> Project | REFINE | Preserve/align scope hierarchy | Scope | Durable objects lack ownership boundary |
| CIM-081 | Every durable domain object belongs to exactly one Scope | ADD | Add no-floating-object invariant | Scope | Orphan state and ambiguous policy inheritance |
| CIM-082 | Scope and Resource are distinct; Repository is a Resource, Project is a Scope | ADD | Define taxonomy | Scope | Container/resource semantics are mixed |
| CIM-083 | AI Kernel remains the technical execution core after Operational Foundation admission | REFINE | Preserve and align with new pre-runtime foundation | AI Kernel | Cognitive Processing accidentally moved into Kernel |
| CIM-084 | AI Kernel executes; it does not decide | NO CHANGE | Retain hard invariant | AI Kernel | Runtime becomes business decision authority |
| CIM-085 | Context Assembly/Builder is outside AI Kernel; Kernel consumes already-built immutable Context Package | CORRECT | Remove/avoid Kernel ownership of Context Builder | Context / AI Kernel | Kernel contains higher-level business context construction |
| CIM-086 | Capability-based execution and provider-independent Kernel remain canonical | NO CHANGE | Preserve existing runtime architecture | AI Kernel | New foundation regresses provider independence |
| CIM-087 | Provider is stateless definition; Provider Executor owns runtime state | REFINE | Align Provider constitution with convergence terminology | Provider | Provider mixes definition and execution state |
| CIM-088 | Capability is independent from Provider | NO CHANGE | Preserve capability-first routing | Capability / Provider | Routing hard-coded to provider names |
| CIM-089 | Architecture Convergence and Implementation Convergence are separate governed programs | REFINE | Ensure canonical governance separation | Governance | Current repository constrains target architecture |
| CIM-090 | Architecture target is defined before repository gap/migration analysis | ADD | Add architecture-first invariant | Governance | Accidental implementation becomes architecture |

## Codex verification obligations

Codex SHALL perform the repository traversal and evidence binding. For every CIM item it SHALL identify all current canonical clauses, diagrams, ADRs, contracts and terminology affected, including conflicts and duplicate definitions. Codex SHALL not redesign accepted decisions while doing this traversal.

Required audits:

1. Decision -> Constitution coverage.
2. Constitution -> Decision reverse coverage.
3. Repository-wide terminology search, including legacy synonyms.
4. Canonical diagram coverage.
5. Negative-invariant coverage.
6. L0-L4 layer completeness.
7. Cross-layer responsibility/authority conflicts.
8. 02/03 scope and ownership boundaries.
9. Duplicate or contradictory canonical definitions.
10. Orphan references to superseded concepts.

The matrix is a planning authority input. Exact file/section evidence discovered by Codex SHALL be attached without changing the Product Owner-approved target semantics.
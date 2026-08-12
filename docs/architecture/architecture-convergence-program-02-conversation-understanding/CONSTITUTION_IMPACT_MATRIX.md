# Architecture Convergence 02 — Constitution Impact Matrix

Status: WORKING / IMPACT ANALYSIS
Branch: `architecture/02-conversation-understanding-convergence`

## Purpose

This matrix maps the accepted 02 convergence decisions to the current constitutional/canonical architecture areas that must be added, refined, superseded, moved, or explicitly left unchanged.

Important evidence note: the Product Owner confirms that the new concepts introduced during this convergence — including Cognitive Profile, Factory Protocol L0–L4, FactoryIP, Artifact Contract, Claim and related terminology — did not exist previously in canonical architecture. They therefore enter this matrix as genuine convergence deltas, not rediscovered legacy terminology.

This is an impact map, not final constitutional wording. `CONSTITUTION_AMENDMENT.md` carries candidate wording; `FOUNDATION_DECISIONS.md` carries the accepted semantics.

## Impact classifications

- **ADD** — new constitutional concept/invariant required.
- **REFINE** — existing canonical concept remains but its boundary/definition changes.
- **SUPERSEDE** — earlier abstraction is replaced by the accepted model.
- **MOVE** — material belongs to another convergence section/responsibility.
- **CORRECT** — current terminology/boundary is misleading or wrong and must be corrected.
- **NO CHANGE** — existing invariant remains valid and should be preserved.
- **DEFER** — direction accepted but detailed constitutionalization intentionally waits for later topology/domain review.

## Matrix

| Impact ID | Accepted decision/change | Current constitutional/canonical area affected | Impact | Required target treatment | Risk if missed |
|---|---|---|---|---|---|
| CIM-001 | Cognitive Processing is generalized stateless processing | Conversation Understanding / cognitive processing wording | REFINE | Define Conversation Understanding as one use of reusable Cognitive Processing; durable state remains with invoking domain | Conversation-specific implementation becomes accidental architecture |
| CIM-002 | Cognitive Profile replaces standalone Context Profile | Earlier Context Profile baseline from 01 | SUPERSEDE | Replace Context-only profile abstraction with versioned Cognitive Profile containing Context/Understanding/Evaluation policies | Two overlapping profile systems survive |
| CIM-003 | Processing Purpose ≠ User Intent | Conversation Understanding routing/intent semantics | ADD | Make Processing Purpose known invocation input; User Intent is Understanding output | Circular routing: intent required before intent is understood |
| CIM-004 | Effective Cognitive Profile composition is auditable | Context/cognitive policy resolution | ADD | Require version/hash/snapshot evidence for effective composition without forcing new domain entity | Non-reproducible cognitive behavior |
| CIM-005 | Cognitive invocation is a contract, not automatic domain object | Conversation Understanding invocation model | REFINE | Keep invocation explicit/auditable through execution/evidence rather than unnecessary entity lifecycle | Object-model inflation |
| CIM-006 | Understanding Result immutable and structured | Conversation Understanding result model | REFINE | Preserve observation/inference/assumption/reference/ambiguity distinctions and evidence links | Confidence/interpretation becomes implicit authority |
| CIM-007 | Evaluation separate from Understanding and authority | Conversation Understanding / CSE boundary | REFINE / MOVE | Keep Evaluation stateless; move domain consequence/state transition to responsible authority and 03 where applicable | Cognitive processor mutates domain state |
| CIM-008 | L0 Scope & Isolation | No prior Factory Protocol layer | ADD | Add Effective Operational Scope & Isolation as foundation | Scope/tenant isolation becomes scattered implementation detail |
| CIM-009 | Organization/Tenant → Workspace → Project hierarchy | Scope/project constitutional definitions | REFINE | Canonicalize hierarchy; repository stays Resource Context unless later explicitly promoted | Repository incorrectly becomes ownership/security scope |
| CIM-010 | Application Default Rules above scope | Policy/default resolution | ADD | Separate overrideable defaults and non-overridable invariants from tenant scope | Defaults become accidental tenant authority |
| CIM-011 | Isolation before semantic retrieval | Context/AKB/retrieval boundaries | ADD | Require eligibility/isolation before semantic search/ranking | Cross-project/tenant semantic leakage |
| CIM-012 | Multilingual language context | Context architecture | ADD | Allow interaction/artifact/code/source language distinctions | One global language field distorts context semantics |
| CIM-013 | L1 Evidence Protocol | Existing Evidence constitutional references | REFINE / GENERALIZE | Elevate Evidence into common protocol layer for significant handoffs/transitions; keep it distinct from logging | Evidence remains subsystem-specific and inconsistent |
| CIM-014 | Domain Authority owns fact; Evidence Infrastructure records proof | Evidence / authority boundaries | ADD | Separate fact authority from evidence recording infrastructure | Evidence store becomes accidental decision authority |
| CIM-015 | Evidence existence ≠ sufficiency | Evaluation / Evidence semantics | ADD | Evidence supports/proves; Evaluation assesses contract sufficiency; authority decides consequence | Presence of evidence treated as automatic acceptance |
| CIM-016 | L2 Provenance & Causality | Existing evidence/lineage references | ADD / GENERALIZE | Add common provenance relation model rather than domain-local lineage implementations | Fragmented causality models |
| CIM-017 | Controlled Relation Families/specializations | Provenance vocabulary | ADD | Canonical stable families; controlled versioned specializations; prohibit runtime ad-hoc relation types | Semantic graph becomes ungoverned taxonomy |
| CIM-018 | Append-oriented immutable provenance facts | Provenance lifecycle | ADD | Corrections append facts; do not rewrite history; inverse may be projection | Historical causality becomes mutable/unreliable |
| CIM-019 | PENDING/ACTIVE/RETRACTED/SUPERSEDED | Provenance lifecycle | ADD | Canonicalize relation lifecycle semantics | Each domain invents incompatible lifecycle |
| CIM-020 | Relation lifecycle ≠ Evidence Assurance | Evidence/provenance interaction | ADD | Keep semantic relation state and assurance state independent | Evidence degradation silently rewrites history |
| CIM-021 | L3 Artifact Protocol | Existing Artifact references | REFINE / GENERALIZE | Elevate Artifact to common protocol layer with logical identity + immutable versions | Artifact remains loose synonym for files/results |
| CIM-022 | Artifact Contract | No prior canonical concept | ADD | Add versioned contract governing qualification/purpose/versioning/persistence/integrity/governance/authority | Artifact types require hard-coded behavior |
| CIM-023 | Artifact qualification authority separation | Artifact / cognitive boundary | ADD | Understanding classifies, Evaluation applies contract, Artifact Authority decides consequence | LLM classification becomes lifecycle authority |
| CIM-024 | Contract-driven stateful/stateless governance | Artifact lifecycle | ADD | Do not force one lifecycle on all Artifacts; mutable review lifecycle separate from immutable version | Immutable Artifact gets mutable status semantics |
| CIM-025 | Artifact ↔ Evidence separation | Evidence + Artifact | ADD | Evidence may reference Artifact Version; no `is_evidence` mutation/type exception | Evidence artifacts get divergent handling |
| CIM-026 | Artifact ↔ Knowledge separation | AKB / Knowledge publication | ADD | Full Artifact never automatically becomes AKB; extract semantic knowledge units with provenance | AKB becomes document dump/vector store |
| CIM-027 | Knowledge Candidate | Knowledge lifecycle | ADD | Add structured potential knowledge unit without oversized state machine | Publication semantics hidden in ingestion code |
| CIM-028 | Knowledge conflict stability | Knowledge authority/conflict | ADD | ACTIVE knowledge remains canonical until responsible authority resolves conflict; no last/newest/confidence wins | Non-deterministic knowledge truth |
| CIM-029 | Materialization & payload separation | Artifact storage | ADD | Artifact Version metadata references immutable inline/external payload by stable reference + digest | Storage technology leaks into domain identity |
| CIM-030 | Artifact integrity | Artifact storage/evidence | ADD | Same version = same content identity; verify persistent payload integrity | Version identifiers cease to be trustworthy |
| CIM-031 | Artifact composition uses L2 | Artifact dependency/lineage | ADD | Composite Artifacts reference immutable versions; dependencies recorded via provenance rather than second graph | Competing dependency graphs diverge |
| CIM-032 | Applicability ≠ historical legitimacy | Artifact validation | ADD | Evaluate intended use/current context/policy without mutating Artifact Version | Historical artifacts become retroactively invalidated |
| CIM-033 | Retention/availability ≠ historical identity | Artifact retention | ADD | Payload may archive/expire by policy while identity/provenance remains historical | Deletion rewrites audit history |
| CIM-034 | L3 protocol boundary | Artifact/authority | ADD | L3 may detect need for external authority but does not resolve it | Artifact layer grows into orchestration/resolution engine |
| CIM-035 | Result ≠ Outcome ≠ Projection | Result/return-path vocabulary across Constitution | ADD / REFINE | Establish cross-cutting semantic distinction and update affected diagrams/text | Everything becomes ambiguous `Result` |
| CIM-036 | Claim as governed assertion | No prior canonical concept | ADD | Add Claim where explicit responsible decision authority is required; avoid ceremonial Claim creation | Conflicts lack explicit ownership or become over-modeled |
| CIM-037 | Resolution is one interaction pattern | Claim/resolution communication | ADD | Resolution Request/Result belongs under general message protocol, not Artifact layer | L4 becomes resolution-specific dead end |
| CIM-038 | L4 Factory Message Protocol | No prior Factory Protocol layer | ADD | Add general cross-domain message protocol | Domains invent bespoke message contracts |
| CIM-039 | Envelope / Delivery-Interaction / Payload separation | Cross-domain messaging | ADD | Standardize common envelope separately from interaction semantics and payload contracts | Transport metadata and business payload become coupled |
| CIM-040 | Layered packet enrichment | Cross-domain handoff/evidence | ADD | Each layer contributes only relevant facts; no fabricated Evidence/Artifact per hop | Protocol produces ceremonial objects/noise |
| CIM-041 | L4 communication authorization only | Authorization boundaries | ADD | L4 carries/enforces communication-level authority only; domain authorization remains with domain | Transport becomes global business authorization engine |
| CIM-042 | FactoryIP = complete L0–L4 stack | No prior canonical concept | ADD | Add FactoryIP as named Factory communication stack/model | New layers remain disconnected concepts |
| CIM-043 | FactoryIP is not CRUD/API | API/service architecture | ADD INVARIANT | Require semantic domain services rather than generic state CRUD | LAN becomes distributed database API |
| CIM-044 | FactoryIP Node | Domain/component/deployment architecture | ADD | Add stable logical addressable service boundary distinct from domain/process/instance | Deployment topology becomes semantic topology |
| CIM-045 | Published semantic services / no reach-through | Domain boundaries | ADD INVARIANT | All cross-Node interaction through published services; prohibit direct canonical-state mutation | Encapsulation and authority collapse |
| CIM-046 | External MCP/HTTP/WebSocket are adapters | MCP/API constitutional integration | REFINE | External protocols access FactoryIP services but do not bypass canonical boundaries | MCP becomes parallel internal architecture |
| CIM-047 | Factory Chat is FactoryIP Node/boundary | Factory Chat Article/baseline | REFINE | Make Factory Chat addressable interaction boundary while preserving UI-not-Runtime invariant | Return/inbound path has no canonical logical endpoint |
| CIM-048 | Conversation is FactoryIP Node | Conversation Article/baseline | REFINE | Define Conversation Node and its published semantic services | Conversation internals exposed ad hoc |
| CIM-049 | `conversation.interaction` | Conversation inbound contract | REFINE | Semantic interaction intake instead of message CRUD | External callers own message/state mechanics |
| CIM-050 | `conversation.context` | Conversation context/read contract | ADD | Purpose-bound authoritative Conversation context service | Consumers reach into Conversation storage |
| CIM-051 | `conversation.projection` | Conversation return/update path | ADD | Controlled projection of external-domain facts into Conversation semantics | Other domains mutate Conversation state directly |
| CIM-052 | No Conversation/message CRUD or external state transition | Conversation boundary | ADD NEGATIVE INVARIANT | Explicitly prohibit generic CRUD/state-set FactoryIP services | Semantic Node degenerates into CRUD service |
| CIM-053 | FFS routing/name service | No prior canonical concept | ADD | Add Factory Fabric Service as FactoryIP control-plane name/routing resolution | Routing logic scattered across Nodes |
| CIM-054 | FFS not data-plane proxy | FactoryIP transport | ADD INVARIANT | Packets travel directly after resolution; FFS supplies resolution/policy information | Central bottleneck and accidental service mesh |
| CIM-055 | FFS MVP static/thin/internal | MVP deployment/operations | ADD MVP CONSTRAINT | No mandatory HA, leases, heartbeat, dynamic discovery or LB in MVP | Foundation becomes prematurely over-engineered |
| CIM-056 | Zoning over Envelope Authority | FactoryIP communication authorization | ADD / SUPERSEDE PROPOSAL | Use one zoning/firewall concept instead of overlapping authority mechanisms | Duplicate authorization models |
| CIM-057 | Zoning after topology | Factory LAN design process | DEFER | Complete Node/service topology first; derive zones afterward | Policy invented without communication graph |
| CIM-058 | Firewall baseline | Factory LAN security | ADD DIRECTION | Treat communication authorization as firewall-like policy; exact deny-by-default/service granularity remains open | Security boundary stays implicit |
| CIM-059 | AI Kernel ≠ Cognitive Processing | AI Kernel constitutional definition | CORRECT | Restore Kernel as operational execution core after OF admission | Kernel becomes catch-all AI intelligence layer |
| CIM-060 | Kernel executes; does not decide | AI Kernel authority | NO CHANGE / REINFORCE | Preserve as explicit invariant while correcting surrounding terminology | Runtime takes business authority |
| CIM-061 | Context construction outside Kernel | Context Architecture / Kernel | REFINE | Kernel consumes prepared immutable Context Package; Context Assembly belongs above/outside | Stateful persona/context leaks into Engine/Kernel |
| CIM-062 | 02 vs 03 boundary | Current combined Conversation Article | MOVE / REFINE | Keep Understanding changes in 02; re-review Conversation State/CSE/Mission Resolution in 03 | 03 decisions become accidentally frozen without review |
| CIM-063 | Foundation before Mission/MSM | Architecture Convergence sequencing | ADD GOVERNANCE | L0–L4/FactoryIP/Node/FFS must be canonical baseline before Mission/MSM integration | Later domains build against moving communication substrate |
| CIM-064 | Do not integrate unreviewed domains into LAN | Factory LAN diagrams | ADD GOVERNANCE | Add Nodes/services section-by-section only after canonical review | Future-domain assumptions become accidental decisions |

## Constitutional areas requiring direct amendment

### 1. Global / cross-cutting constitutional foundation

A new constitutional foundation section is required for:

```text
Factory Protocol
├── L0 — Scope & Isolation
├── L1 — Evidence
├── L2 — Provenance & Causality
├── L3 — Artifact
└── L4 — Factory Message Protocol

FactoryIP
├── Node
├── Published Semantic Service
├── FFS
└── Zoning [policy detail deferred]
```

This should not be buried inside the Conversation article because later Mission, MSM, Operational Foundation, Context, Capability, Execution and Knowledge domains will depend on it.

### 2. Factory Chat constitutional area

Amend to add FactoryIP addressability/Node-boundary semantics while preserving:

- Factory Chat is UI/interaction boundary;
- Factory Chat is not Runtime;
- Factory Chat does not own Conversation canonical state.

### 3. Conversation constitutional area

Amend to add:

- Conversation as independent FactoryIP Node;
- `conversation.interaction`;
- `conversation.context`;
- `conversation.projection`;
- no CRUD/state reach-through invariant.

### 4. Conversation Understanding constitutional area

Amend/generalize to:

- Cognitive Processing;
- Cognitive Profile;
- Processing Purpose;
- Context → Understanding → Evaluation separation;
- immutable Understanding/Evaluation Results;
- explicit authority boundary.

### 5. Conversation State / Mission Resolution constitutional area

Do **not** silently rewrite during 02. Mark current combined wording for 03 convergence review. Only cross-cutting protocol/authority terminology that is already accepted may be prepared for later application.

### 6. AI Kernel constitutional area

Correct any wording that equates AI Kernel with cognitive/understanding processing. Preserve the execution-only authority invariant and immutable Context Package consumption boundary.

### 7. Artifact / Evidence / Knowledge constitutional areas

Where these concepts already appear later in the Constitution, they must be reconciled with the new cross-cutting protocol foundation rather than independently redefined. In particular:

- Evidence must align with L1;
- provenance/causality with L2;
- Artifact with L3;
- AKB publication must preserve Artifact/Knowledge separation;
- return/result vocabulary must respect Result/Outcome/Projection.

## Diagram impact checklist

Every canonical diagram touched by the following concepts must be audited:

- Product Owner → Factory Chat → Conversation boundary;
- Conversation → Understanding → State/Mission Resolution chain;
- Context Assembly / Context Package position;
- AI Kernel position;
- Result/Outcome/Projection return path;
- Evidence/Artifact/Knowledge flows;
- MCP/external adapter placement;
- Factory LAN / Node topology;
- any diagram implying direct Engine-to-Engine or Node-internal reach-through.

No final LAN diagram should introduce future Nodes whose domain has not yet been reviewed.

## High-risk omission zones

The final completeness audit must pay special attention to:

1. **Earlier 00/01 decisions** that are now refined by FactoryIP but must not be accidentally erased.
2. **Article IV combined responsibilities**, because 02 and 03 are now intentionally separated.
3. **Evidence terminology**, which may appear in many later articles and can silently conflict with L1.
4. **Artifact/Result terminology**, where old generic wording may conflict with L3 and Result/Outcome/Projection.
5. **AI Kernel references**, because previous wording may use the term for a broader cognitive concept.
6. **MCP/API diagrams**, which may accidentally show direct domain/internal access.
7. **Knowledge/AKB ingestion wording**, which must not imply full-artifact ingestion as canonical knowledge.
8. **Authorization language**, to prevent L4 Zoning from swallowing domain/business authority.

## Required final audit passes

Before `SECTION CLOSED`, perform all of the following independently:

1. **Decision → Constitution audit:** every ACCEPTED decision has a constitutional treatment or an explicit reason why it is non-constitutional.
2. **Constitution → Decision audit:** every changed constitutional statement traces back to an accepted decision.
3. **Baseline → Target diff audit:** every affected current paragraph/diagram is classified ADD/REFINE/SUPERSEDE/MOVE/NO CHANGE.
4. **Terminology audit:** old/new terms are searched repository-wide and conflicts enumerated.
5. **Diagram audit:** canonical diagrams match textual authority/boundary semantics.
6. **Negative-invariant audit:** prohibited paths (CRUD reach-through, state mutation, Kernel decision authority, semantic isolation bypass) are explicitly preserved.
7. **Layer completeness audit:** L0, L1, L2, L3 and L4 each have purpose, ownership, inputs/outputs/boundaries and non-responsibilities.
8. **Cross-layer audit:** no responsibility is duplicated between L0–L4, FactoryIP, FFS, Zoning and domain authority.
9. **02/03 scope audit:** no unreviewed Conversation State/Mission Resolution decision is accidentally canonicalized.
10. **Future-section compatibility audit:** later course sections can consume the new foundation without requiring assumptions about unreviewed domains.

Only after these passes should the final Constitution Amendment and final section Mermaid be presented for Product Owner closure approval.

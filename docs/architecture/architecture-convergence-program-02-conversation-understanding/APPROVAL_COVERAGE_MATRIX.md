# Architecture Convergence 02 — Approval Coverage Matrix

Status: WORKING VERIFICATION ARTIFACT
Purpose: prove that individually approved Product Owner decisions survive the multi-day convergence without semantic loss.
Canonical effect: NONE until constitutional closure/merge.

## 1. Verification model

This matrix is intentionally independent from the prose summaries. It triangulates four evidence classes:

1. sequential Product Owner approval / P4 accepted-decision inventory;
2. `LOSSLESS_APPROVED_DECISION_LEDGER.md` decision ID;
3. approved/reconciled Mermaid evidence where available;
4. required constitutional target.

Coverage states:

- `COVERED` — approved semantic is explicitly preserved in the lossless ledger;
- `COVERED+DIAGRAM` — ledger plus diagram evidence;
- `SUPERSEDED-PRESERVED` — earlier approved form remains traceable but a later approved refinement controls final wording;
- `DEFERRED` — direction/history preserved, detail intentionally belongs to a later convergence section;
- `OPEN` — not approved and MUST NOT be silently constitutionalized.

## 2. Cognitive Processing coverage

| Approval semantic | Ledger | Diagram / secondary evidence | Constitutional target | Coverage |
|---|---|---|---|---|
| Understanding consumes explicit immutable Context Package | CU-01 | Context Package / Cognitive Processing diagrams | Cognitive Processing | COVERED+DIAGRAM |
| Structured immutable Understanding Result | CU-02 | Conversation Understanding diagram | Cognitive Processing | COVERED+DIAGRAM |
| Observation / Inference / Assumption / Resolved Reference / Ambiguity remain distinct | CU-02 | Conversation Understanding diagram | Understanding Result contract | COVERED+DIAGRAM |
| Understanding is not Domain Authority | CU-03 | Cognitive Processing chain | Authority boundary | COVERED+DIAGRAM |
| Conversation Understanding generalizes to stateless Cognitive Processing | CU-04 | working/final Cognitive Processing diagrams | Cognitive Processing foundation | COVERED+DIAGRAM |
| one Cognitive Profile with Context/Understanding/Evaluation Policy | CU-05 | Cognitive Profile diagrams | Cognitive Profile | COVERED+DIAGRAM |
| standalone Context Profile superseded | CU-05 | older Context Package diagram retained as historical evidence | 01 amendment + 02 canonical | SUPERSEDED-PRESERVED |
| Profile declares requirements, not LLM workflow | CU-06 | processing discussion | Cognitive Profile invariants | COVERED |
| Processing Purpose is not User Intent | CU-07 | Profile Resolution diagram | Profile Resolution | COVERED+DIAGRAM |
| resolution only from known pre-processing inputs | CU-07 | Profile Resolution diagram | Profile Resolution | COVERED+DIAGRAM |
| Cognitive Profile is versioned/scope-aware declarative definition | CU-08 | Profile diagrams | Cognitive Profile | COVERED+DIAGRAM |
| Effective Profile may be composed | CU-09 | Profile Resolution diagrams | Profile composition | COVERED+DIAGRAM |
| effective composition auditable | CU-09 | profile snapshot/hash discussion | Execution/Evidence linkage | COVERED |
| Effective Profile not automatically first-class | CU-10 | decision discussion | negative invariant | COVERED |
| Processing Request is invocation contract, not automatically domain entity | CU-11 | decision discussion | invocation boundary | COVERED |
| Context → Understanding → Evaluation separation | CU-12 | Cognitive Processing diagram | Cognitive Processing | COVERED+DIAGRAM |
| Evaluation is qualification, not consequence authority | CU-13 | Cognitive Processing diagram | Evaluation/Authority boundary | COVERED+DIAGRAM |
| Understanding Result historical validity ≠ current applicability | CU-14 | dedicated applicability diagram | Result lifecycle/applicability | COVERED+DIAGRAM |
| applicability evaluated; old result remains history; reprocessing may create new result | CU-15 | dedicated applicability diagram | Evaluation/reprocessing | COVERED+DIAGRAM |

## 3. L0 coverage

| Approval semantic | Ledger | Constitutional target | Coverage |
|---|---|---|---|
| L0 = Effective Operational Scope & Isolation | FP-L0/01 | Factory Protocol L0 | COVERED |
| Organization/Tenant → Workspace → Project | FP-L0/02 | Scope + Factory Protocol | COVERED |
| Project primary working/domain scope | FP-L0/02 | Scope | COVERED |
| Repository/Branch/Revision/Environment are Resource Context, not automatic Scope | FP-L0/03 | Scope reconciliation | COVERED |
| Application Default Rules are above scope but not Scope/Tenant | FP-L0/04 | Scope/default rules | COVERED |
| defaults may be overrideable; architecture/security invariants non-overridable | FP-L0/04 | policy/default rules | COVERED |
| effective bindings resolved before stateless processing | FP-L0/05 | L0 + Cognitive Processing | COVERED |
| tenant/scope/resource/policy eligibility precedes semantic retrieval | FP-L0/06 | isolation invariant | COVERED |
| semantic similarity cannot override isolation | FP-L0/06 | isolation invariant | COVERED |
| no implicit sibling-project leakage | FP-L0/06 | isolation invariant | COVERED |
| Language Context is multidimensional | FP-L0/07 | Localization reconciliation | COVERED |

## 4. L1 coverage

| Approval semantic | Ledger | Constitutional target | Coverage |
|---|---|---|---|
| significant architectural handoff/transition produces immutable Evidence | FP-L1/01 | Factory Protocol L1 | COVERED |
| Evidence is proof, not generic logging | FP-L1/01 | L1 invariant | COVERED |
| Evidence uses immutable/versioned references and integrity | FP-L1/02 | Evidence Record | COVERED |
| Artifact can be referenced by Evidence without becoming Evidence | FP-L1/02, FP-L3/06 | L1/L3 boundary | COVERED |
| Domain Authority owns fact; Evidence Infrastructure records proof | FP-L1/03 | authority boundary | COVERED |
| Evidence existence does not imply sufficiency | FP-L1/04 | Evidence/Evaluation boundary | COVERED |
| Evaluation assesses sufficiency/applicability; authority decides consequence | FP-L1/04 | L1/Cognitive Processing | COVERED |

## 5. L2 coverage

| Approval semantic | Ledger | Constitutional target | Coverage |
|---|---|---|---|
| L2 records derivation/production/use/trigger/causality | FP-L2/01 | Factory Protocol L2 | COVERED |
| L2 is not business decision engine | FP-L2/01 | negative invariant | COVERED |
| small controlled Relation Families + versioned specialization | FP-L2/02 | Relation taxonomy | COVERED |
| no runtime ad-hoc relation types | FP-L2/02 | Relation invariant | COVERED |
| relation is first-class auditable historical semantic fact | FP-L2/03 | Relation model | COVERED |
| source/target/type semantics immutable | FP-L2/03 | Relation integrity | COVERED |
| one authoritative direction; inverse is projection | FP-L2/04 | Relation direction | COVERED |
| corrections append rather than rewrite history | FP-L2/05 | temporal semantics | COVERED |
| PENDING / ACTIVE / RETRACTED / SUPERSEDED distinctions | FP-L2/06 | Relation lifecycle | COVERED |
| challenge alone does not demote ACTIVE | FP-L2/06 | lifecycle invariant | COVERED |
| activation authority is part of relation definition | FP-L2/07 | authority contract | COVERED |
| Domain Authority vs Provenance Infrastructure ownership | FP-L2/07 | ownership boundary | COVERED |
| authority defaults inherit Family → specialization | FP-L2/07-A | relation specialization | COVERED |
| lifecycle and Evidence Assurance are separate axes | FP-L2/08 | L1/L2 boundary | COVERED |
| ACTIVE relation + DEGRADED assurance is valid | FP-L2/08 | assurance projection | COVERED |
| evidence degradation does not auto-retract relation | FP-L2/08 | negative invariant | COVERED |

## 6. L3 coverage

Every FP-L3/01–17 item is individually represented in the lossless ledger. Closure MUST NOT replace this block with a generic “immutable/versioned Artifact” statement.

| Decision | Core preserved semantic | Coverage |
|---|---|---|
| FP-L3/01 | contract/policy qualifies Artifact; producer naming is insufficient | COVERED |
| FP-L3/02 | logical identity + immutable versions; historical refs bind concrete versions | COVERED |
| FP-L3/03 | semantic-purpose + contract identity; content similarity ≠ identity | COVERED |
| FP-L3/04 | Understanding may assist; Evaluation + Artifact Authority own consequence | COVERED |
| FP-L3/05 | immutability ≠ statefulness; governance state separate from immutable content | COVERED |
| FP-L3/06 | Artifact ≠ Evidence; no evidence flag/subtype mutation | COVERED |
| FP-L3/07 | Artifact ≠ Knowledge; full Artifact does not become Knowledge | COVERED |
| FP-L3/07-A | semantic knowledge extraction, not mechanical chunking | COVERED |
| FP-L3/08 | first-class immutable provenance-linked Knowledge Candidate | COVERED |
| FP-L3/09 | CREATE/REVISE/CONFIRM/DUPLICATE/CONFLICT/REJECT; Resolution ≠ Consequence | COVERED |
| FP-L3/10 | ACTIVE Knowledge stable on conflict; no last-writer/confidence/newest wins | COVERED |
| FP-L3/11 | complete versioned Artifact Contract | COVERED |
| FP-L3/12 | Artifact Version metadata/identity ≠ payload; stable ref + digest | COVERED |
| FP-L3/13 | same Version = same content identity | COVERED |
| FP-L3/14 | composition via concrete versions + L2; no second dependency graph / mutable latest | COVERED |
| FP-L3/15 | historical legitimacy ≠ applicability; no mutable VALID/INVALID Artifact status | COVERED |
| FP-L3/16 | identity/provenance ≠ payload retention/availability; L0 scope governs use | COVERED |
| FP-L3/17 | unresolved authority exits L3; L3 does not own cross-domain resolution | COVERED |

## 7. Cross-layer semantic payload coverage

| Approval semantic | Ledger | Coverage |
|---|---|---|
| Result ≠ Outcome ≠ Projection | FP-X/01 | COVERED |
| Claim can become first-class when authoritative resolution is required | FP-X/02 | COVERED |
| deterministic cases do not require ceremonial Claim | FP-X/02 | COVERED |
| Claim carries responsibility/required-authority semantics | FP-X/02 | COVERED |
| Claim is not an L3 resolution mechanism | FP-X/03 | COVERED |
| Resolution is one interaction pattern, not definition of L4 | FP-X/04 | COVERED |

## 8. L4 coverage and terminology evolution

A specific evolution must remain visible:

```text
Resolution Protocol
→ Factory Message Protocol
→ explicit Transport responsibility at L4
```

The later decision does not erase the earlier accepted requirement that L4 is a general message protocol; the final Constitution must reconcile the **Factory Message Protocol name** with the **Transport Layer responsibility** without losing either semantic.

| Approval semantic | Ledger | Coverage |
|---|---|---|
| L4 is general Factory Message/upper communication protocol, not Resolution-only | FP-L4/01 | SUPERSEDED-PRESERVED |
| Factory Message only at genuine domain/protocol boundaries | FP-L4/02 | COVERED |
| Envelope / Delivery-Interaction / Payload Contract separation | FP-L4/03 | COVERED |
| payload may carry Message/Result/Outcome/Projection/Claim/Resolution etc. | FP-L4/03 | COVERED |
| L4 owns A→B transfer information at its level | FP-L4/04 | COVERED |
| L4 communication authorization ≠ domain/business authorization | FP-L4/05 | COVERED |
| no duplicate Layer Bindings abstraction | FP-L4/06 | COVERED |
| each layer owns only its responsibility | FP-L4/07 | COVERED |
| layer-relevant information directly interpretable | FP-L4/08 | COVERED |
| enrich only on relevant new fact; no ceremonial Evidence/Artifact per hop | FP-L4/09 | COVERED |

## 9. FactoryIP / Node coverage

| Approval semantic | Ledger | Coverage |
|---|---|---|
| FactoryIP = complete L0–L4 Factory communication stack | FIP-01 | COVERED |
| Factory Packet = complete layered carried unit | FIP-02 | COVERED |
| Node = LAN-addressable logical service boundary | FIP-03 | COVERED |
| Node ≠ Domain ≠ Service ≠ Process ≠ Deployment ≠ Instance | FIP-04 | COVERED |
| physical/internal topology is not Factory LAN topology | FIP-04 | COVERED |
| Node Qualification requires legitimate stable published boundary | FIP-05 | COVERED |
| first-class/service/engine/deployable alone does not make Node | FIP-05 | COVERED |
| unreviewed future domains are not automatically Nodes | FIP-05 + sequencing | COVERED |
| No Internal Reach-Through | FIP-06 | COVERED |
| only published semantic services across Node boundary | FIP-07 | COVERED |
| FactoryIP is not CRUD API | FIP-07 | COVERED |
| MCP/HTTP/WebSocket are adapters, not alternate authority paths | FIP-08 | COVERED |
| Factory Chat independently addressable but UI/not Runtime/no Conversation state ownership | FIP-09 | COVERED+DIAGRAM |
| Conversation is independent FactoryIP Node | FIP-10 | COVERED+DIAGRAM |
| `conversation.interaction` | FIP-11 | COVERED |
| `conversation.context` | FIP-12 | COVERED; concrete consumer OPEN |
| `conversation.projection` | FIP-13 | COVERED |
| external domains send facts, not presentation instructions | FIP-13 | COVERED |
| Conversation decides representation; Factory Chat presents | FIP-13 | COVERED+DIAGRAM |
| Conversation transition remains internal authority | FIP-14 | COVERED |
| no canonical Conversation/message CRUD or external state-set/transition service | FIP-15 | COVERED |

## 10. FFS coverage

| Approval semantic | Ledger | Coverage |
|---|---|---|
| Factory Fabric Service = Factory routing/name-resolution control plane | FFS-01 | COVERED |
| FactoryIP defines communication; FFS resolves delivery | FFS-02 | COVERED |
| logical FactoryIP identity/service resolves to transport binding/target | FFS-02 | COVERED |
| Factory Packet does not normally flow through FFS | FFS-03 | COVERED |
| avoid mandatory central data-plane bottleneck | FFS-03 | COVERED |
| one logical authoritative FFS view | FFS-04 | COVERED |
| physical HA may evolve later without competing logical authority | FFS-04 | COVERED |
| MVP FFS is part of AI Bridge, not separate service-mesh infrastructure | FFS-05 | COVERED |
| static/thin MVP resolution acceptable | FFS-05 | COVERED |
| dynamic discovery/leases/heartbeat/LB/distributed registry/HA not MVP requirements | FFS-06 | COVERED |

## 11. Zoning coverage

| Approval semantic | Ledger | Coverage |
|---|---|---|
| use Zoning instead of overlapping Envelope Authority model | ZONE-01 | COVERED |
| Zoning asks whether FactoryIP identity A may communicate with B | ZONE-02 | COVERED |
| Zoning does not interpret payload | ZONE-02 | COVERED |
| Zoning is not business/domain authorization | ZONE-02 | COVERED |
| detailed zones only after Node + Service topology | ZONE-03 | DEFERRED |
| firewall direction accepted | ZONE-04 | COVERED |
| exact deny-by-default/service granularity not yet approved | ZONE-04 | OPEN |

## 12. Conversation LAN reconciliation coverage

The approved LAN interpretation is semantic, not CRUD/data-access topology.

```text
Factory Chat Node
  -- FactoryIP / conversation.interaction -->
Conversation Node

Conversation Node
  -- FactoryIP / conversation.projection -->
Factory Chat Node
```

`conversation.context` is an authoritative purpose-bound read service for eligible future consumers; its exact consumer is intentionally not invented in 02.

Preserved Conversation ownership from approved diagrams:

- durable Conversation interaction record;
- Messages;
- Attachments;
- Participants;
- Conversation metadata;
- no UI ownership of canonical Conversation state;
- stateless context assembly outside durable Conversation state;
- controlled projection back toward interaction/UI.

Later FactoryIP semantics refine the meaning of diagram arrows: they are published semantic service communication, never direct object/database reach-through.

Coverage: `COVERED+DIAGRAM`, with 03 state semantics explicitly deferred.

## 13. AI Kernel boundary coverage

| Approval semantic | Ledger | Coverage |
|---|---|---|
| AI Kernel ≠ Cognitive Processing | KERNEL-01 | COVERED |
| Kernel is post-admission operational execution core | KERNEL-01 | COVERED |
| Kernel executes; it does not decide | KERNEL-02 | COVERED |
| Context construction is outside Kernel | KERNEL-03 | COVERED |
| Kernel consumes prepared immutable Context Package | KERNEL-03 | COVERED |

## 14. Section-boundary / sequencing coverage

| Approval semantic | Coverage |
|---|---|
| 02 Conversation Understanding and 03 Conversation State & Mission Resolution remain distinct convergence scopes | COVERED |
| current 03 state/CSE/Mission Resolution material is input, not silently re-approved by 02 | COVERED |
| Factory Protocol L0–L4 + FactoryIP + Node + FFS must become constitutional baseline before later Mission/MSM convergence depends on it | COVERED |
| later domains are integrated into the LAN only after their own review | COVERED |
| do not invent future Nodes/services in 02 | COVERED |

## 15. Explicit gaps / unresolved items

These are **not approval gaps**; they are intentionally unresolved and must remain so:

1. final owner/Node of Context Assembly;
2. concrete final consumer(s) of `conversation.context`;
3. profile-resolution ambiguity/fallback/clarification policy;
4. final complete Understanding Result schema beyond approved distinctions;
5. exact reusable Evidence Evaluation capability contract;
6. final Zoning rule set and exact deny-by-default/service granularity;
7. Nodes/services for unreviewed later domains;
8. detailed Conversation State/CSE/Mission Resolution model — 03;
9. detailed dynamic/HA FFS architecture — post-MVP;
10. implementation-specific tables/classes/endpoints not explicitly approved.

## 16. Coverage conclusion for this pass

The current lossless ledger covers the recovered P4 foundation inventory and the detailed L0–L4 / FactoryIP / FFS / Conversation LAN decisions found in the source material reviewed in this pass.

This is **not yet the final completeness declaration**. Final closure still requires:

- another source-history sweep for earlier sequential approvals and negative invariants;
- reconciliation of all approved Mermaid diagrams;
- Codex repository-wide Decision→Constitution and Constitution→Decision traversal;
- explicit Product Owner review of any discovered semantic mismatch.

Final rule:

> **An accepted decision without a ledger ID and constitutional destination is a closure defect. A constitutional statement without an accepted decision source is also a closure defect.**

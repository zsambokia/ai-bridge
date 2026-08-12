# Architecture Convergence 02 — Exhaustive Codex Closure Specification

Status: READY FOR ASSESSMENT / NOT YET CANONICAL
Authority: Product Owner-approved convergence decisions
Execution target: repository-wide architecture/documentation convergence

## 1. Objective

Converge the AI Bridge canonical architecture corpus to the complete set of Product Owner-approved decisions from Architecture Convergence 02 **without losing, compressing away, or silently changing any approved semantic detail**.

This is primarily a constitutional/documentation convergence task. Existing implementation is evidence of current state, not authority over target architecture.

## 2. Authoritative input package

Codex MUST read all files in:

`docs/architecture/architecture-convergence-program-02-conversation-understanding/`

At minimum:

1. `LOSSLESS_APPROVED_DECISION_LEDGER.md` — granular approval-preservation source; every ACCEPTED entry is mandatory.
2. `FOUNDATION_DECISIONS.md` — detailed target semantics and explanatory model.
3. `DECISION_REGISTER.md` — accepted/open classification.
4. `CHANGE_REGISTER.md` — current→target delta inventory.
5. `CONSTITUTION_IMPACT_MATRIX.md` — impact classification and omission-risk map.
6. `REPOSITORY_IMPACT_EVIDENCE.md` — known repository impact evidence.
7. `CONSTITUTION_AMENDMENT.md` — working candidate amendment wording.
8. `OPEN_QUESTIONS.md` — items that MUST remain open/deferred unless independently approved.
9. this `CODEX_CLOSURE_SPECIFICATION.md`.

No single summary document is sufficient on its own.

## 3. Non-negotiable architectural invariants

Codex MUST preserve the complete semantics in the Lossless Approved Decision Ledger, including all sub-decisions for:

- Cognitive Processing and Cognitive Profile;
- L0 Effective Operational Scope & Isolation;
- L1 Evidence Protocol;
- L2 Provenance & Causality Protocol;
- L3 Artifact Protocol, including FP-L3/01 through FP-L3/17 and Knowledge Publication semantics;
- Result / Outcome / Projection;
- Claim and Resolution boundary;
- L4 Factory Message Protocol;
- FactoryIP and Factory Packet;
- FactoryIP Node semantics;
- Factory Chat Node/boundary;
- Conversation Node and semantic service families;
- FFS;
- Zoning/firewall direction and its intentionally deferred details;
- AI Kernel boundary correction;
- 02/03 scope separation and later-section sequencing.

## 4. Assessment — mandatory full repository traversal

Before editing, perform a repository-wide architecture corpus assessment.

### 4.1 Discover all architecture-governed sources

Search at minimum for:

- Constitution / constitutional / Article;
- ADR;
- canonical diagrams;
- architecture indexes/registers;
- Conversation / Factory Chat / Conversation Understanding / CSE / Mission Resolution;
- Context Profile / Context Package / Context Builder / Context Assembly;
- Evidence / provenance / causality / lineage;
- Artifact / Result / Outcome / Projection;
- Knowledge / AKB / Knowledge Candidate / publication;
- AI Kernel / Engine / Operational Foundation;
- MCP / HTTP / WebSocket / API / adapter;
- Scope / Organization / Workspace / Project / Repository;
- localization/language;
- authority / authorization / permission / routing;
- network/LAN/service/node terminology.

Do not assume the pre-existing `REPOSITORY_IMPACT_EVIDENCE.md` is exhaustive. Treat it as seed evidence and independently rediscover the corpus.

### 4.2 Build an evidence-backed impact table

For every affected file/section/diagram record:

```text
path
section / line range
current canonical statement
related decision IDs
impact: ADD / REFINE / SUPERSEDE / MOVE / CORRECT / NO CHANGE / DEFER
required treatment
conflict/omission risk
```

### 4.3 Verify prior constitutional relationships

Explicitly inspect and reconcile at least:

- global Architecture Constitution / hierarchy;
- Conversation→Mission Constitution / Article IV;
- AI Kernel Constitution / Article III;
- Scope Constitution / Article VI;
- Localization Constitution / Article VII;
- AKB Knowledge Object/Lifecycle constitutional material;
- canonical Conversation Layer diagram;
- canonical Full Architecture diagram;
- MCP execution/context architecture;
- Context Package / cognitive flow docs;
- Knowledge pipeline/foundation docs;
- runtime constitutions;
- terminology convergence matrices/reports;
- architecture corpus/concept registers.

If file names/locations have changed, locate their current equivalents.

## 5. Architecture Challenge — mandatory before implementation

Codex MUST critically test the approved target model against the repository baseline.

Report separately:

1. genuine contradiction;
2. duplicate/overlapping ownership;
3. terminology collision;
4. hidden implementation assumption promoted to architecture;
5. accepted decision that cannot be represented coherently without changing another accepted decision;
6. apparent better architecture.

If a better architecture would alter an ACCEPTED Product Owner decision, STOP and request Product Owner decision. Do not silently improve/supersede it.

If the issue is merely wording/placement and does not alter semantics, proceed with the cleanest constitutional representation and document the rationale.

## 6. Required constitutional structure

The final corpus MUST give the cross-cutting communication foundation a constitutional home outside a Conversation-only article.

Required conceptual hierarchy:

```text
Factory Protocol / FactoryIP foundation
│
├── L0 — Effective Operational Scope & Isolation
├── L1 — Evidence Protocol
├── L2 — Provenance & Causality Protocol
├── L3 — Artifact Protocol
└── L4 — Factory Message Protocol

FactoryIP
├── Factory Packet
├── FactoryIP Node
├── Published Semantic Service
├── FFS — Factory Fabric Service
└── Zoning — detail intentionally deferred until topology completion
```

The exact file/article split may follow repository governance, but the semantics MUST NOT be buried solely inside Conversation Understanding.

## 7. Required detailed semantic coverage

### 7.1 Cognitive Processing

Final canonical material must explicitly cover:

- stateless generalized Cognitive Processing;
- immutable Context Package input;
- Understanding Result distinctions: observation/inference/assumption/resolved reference/ambiguity;
- Understanding ≠ authority;
- Context → Understanding → Evaluation separation;
- one Cognitive Profile with Context/Understanding/Evaluation policies;
- supersession of standalone Context Profile;
- profile declares goal/requirements, not LLM workflow;
- Processing Purpose ≠ User Intent;
- profile resolution known-input rule;
- profile fragment composition;
- auditability of effective composition;
- Effective Cognitive Profile not automatically first-class object;
- invocation contract not automatically domain entity;
- Evaluation ≠ consequence authority.

### 7.2 L0

Must explicitly cover:

- Organization/Tenant → Workspace → Project;
- Repository/Branch/Revision/Environment as Resource Context;
- Application Default Rules ≠ Scope/Tenant;
- overrideable defaults vs non-overridable invariants;
- effective resource/policy/profile bindings;
- stateless service receives resolved environment;
- isolation/eligibility before semantic retrieval;
- semantic similarity never overrides isolation;
- no implicit sibling-project leakage;
- multidimensional Language Context, reconciled with Localization Constitution.

### 7.3 L1

Must explicitly cover all four approved decisions:

1. significant handoff/transition → immutable Evidence;
2. Evidence Record uses immutable/versioned refs + verifiable integrity;
3. Domain Authority owns fact; Evidence Infrastructure records proof;
4. Evidence existence ≠ sufficiency; Evaluation assesses; authority decides.

### 7.4 L2

Must explicitly cover:

- purpose/non-responsibility;
- controlled Relation Families + versioned specializations;
- no runtime ad-hoc relation types;
- immutable historical relation facts;
- one authoritative relation direction + inverse projection;
- append-oriented correction/history;
- PENDING / ACTIVE / RETRACTED / SUPERSEDED semantics;
- challenge does not auto-demote ACTIVE;
- activation authority contract;
- Domain Authority vs Provenance Infrastructure ownership;
- relation lifecycle vs Evidence Assurance separation;
- immutable assurance Evaluation Results/current assurance projection;
- no automatic relation lifecycle mutation from evidence degradation.

### 7.5 L3

Every FP-L3/01–17 decision from the Lossless Ledger must be represented. Do not summarize L3 merely as “immutable/versioned Artifact”.

Particular mandatory details:

- semantic-purpose + Artifact Contract identity;
- content similarity is not identity;
- deterministic vs Understanding-assisted classification;
- Evaluation and Artifact Domain Authority separation;
- immutable Artifact Version + independent stateful governance;
- Artifact↔Evidence separation;
- Artifact↔Knowledge separation;
- semantic knowledge extraction, not chunking;
- Knowledge Candidate semantics;
- CREATE/REVISE/CONFIRM/DUPLICATE/CONFLICT/REJECT Publication Resolution;
- Resolution ≠ Consequence;
- ACTIVE Knowledge conflict stability;
- forbidden last-writer/confidence/newest-artifact rules;
- complete Artifact Contract fields;
- Artifact Version ≠ payload;
- stable payload ref + digest;
- verifiable integrity;
- composite Artifact using L2 relations, no second dependency graph;
- no mutable `latest` dependency for historical composition;
- applicability via Evaluation, not VALID/INVALID mutation;
- historical identity vs payload retention;
- L0 scope-bound use, no second authorization engine;
- unresolved authority need exits L3 into L4.

### 7.6 Result / Outcome / Projection / Claim / Resolution

Must define distinct semantics and update generic `Result` wording where necessary.

Claim must preserve responsibility/authority semantics and must not become mandatory ceremony for deterministic cases.

Resolution must remain one L4 interaction pattern, not L4 itself.

### 7.7 L4

Must explicitly cover:

- general Factory Message Protocol;
- real domain/protocol boundary trigger;
- Envelope / Delivery-Interaction Semantics / Payload Contract separation;
- multiple payload types;
- L4 A→B communication responsibility;
- L4 communication authorization only, not all business authorization;
- per-layer responsibility isolation;
- direct interpretability of relevant layer information;
- enrich only when new relevant fact exists; no ceremonial Evidence/Artifact generation.

### 7.8 FactoryIP / Node

Must explicitly cover:

- FactoryIP = complete L0–L4 communication stack/model;
- Factory Packet;
- FactoryIP is not CRUD API;
- Node = stable logical LAN-addressable service boundary;
- Node ≠ Domain ≠ Service ≠ Process ≠ Deployment ≠ Instance;
- internal implementation topology ≠ Factory LAN topology;
- No Internal Reach-Through;
- published semantic services only;
- MCP/HTTP/WebSocket as adapters that cannot bypass FactoryIP.

### 7.9 Factory Chat / Conversation Node

Must preserve Factory Chat UI-not-Runtime and no Conversation-state ownership while making it addressable through FactoryIP.

Conversation Node must expose:

- `conversation.interaction`;
- `conversation.context`;
- `conversation.projection`.

Must explicitly forbid generic Conversation/message CRUD and external state-set/transition authority.

### 7.10 FFS

Must explicitly cover:

- Factory Fabric Service naming;
- logical routing/name resolution role;
- “FactoryIP defines communication; FFS resolves delivery” separation;
- control plane, not mandatory data-plane proxy;
- one logical authoritative view;
- MVP inside AI Bridge;
- static/thin acceptable;
- HA/dynamic discovery/leases/heartbeats/LB not MVP requirements.

### 7.11 Zoning

Must explicitly cover accepted semantics while preserving open details:

- one Zoning model instead of overlapping Envelope Authority;
- identity-to-identity communication permission;
- not payload semantics;
- not domain/business authorization;
- detailed policy after Node/service topology;
- firewall direction accepted;
- exact deny-by-default/service-granularity remains OPEN unless Product Owner later approves it.

### 7.12 AI Kernel

Must preserve/correct:

- Kernel is post-OF-admission operational execution core;
- Cognitive Processing is not Kernel;
- Kernel executes, does not decide;
- Context construction outside Kernel;
- Kernel consumes prepared immutable Context Package;
- cross-cutting L1 Evidence must not accidentally become Kernel-exclusive ownership.

## 8. Cross-constitution collision checks

Codex MUST explicitly resolve or report:

1. Kernel `Evidence` object terminology vs cross-cutting L1 Evidence Protocol.
2. AKB `Evidence` specialized Knowledge type vs Artifact/Evidence/Knowledge separation.
3. AKB relationship graph vs L2 provenance relation graph — prevent two competing graphs with ambiguous ownership.
4. Knowledge lifecycle vs L2 relation lifecycle vs Artifact governance lifecycle — keep distinct.
5. Effective Operational Scope vs canonical Scope hierarchy — do not create a fourth Scope type.
6. Language Context vs Localization Constitution — complement, do not duplicate.
7. Context Profile references — all canonical remnants must be classified for supersession/migration.
8. Generic `Result` vocabulary — classify where Result means Result, Outcome or Projection.
9. `Resolution` terminology — distinguish generic L4 interaction pattern from domain concepts such as Mission Resolution.
10. `Node`, `service`, `domain`, `component`, `process`, `instance` terminology — prevent synonym drift.
11. MCP/API diagrams — prevent direct canonical-state reach-through.

## 9. 02 / 03 boundary

Do not redesign or silently approve in this task:

- Conversation State axes;
- detailed CSE transitions;
- Mission readiness;
- Mission Resolution outcome/state model.

Mark them as 03 convergence inputs where current Article IV contains them.

Cross-cutting foundation terminology may be applied where necessary without deciding their 03 semantics.

## 10. Diagram requirements

Identify every canonical diagram affected. At minimum review Conversation Layer and Full Architecture.

Update diagrams only to the extent supported by reviewed/approved domains.

Required visual truths include:

- Factory Chat and Conversation addressable boundaries;
- Conversation published semantic services where appropriate;
- Cognitive Processing separation;
- no Context Profile remnant where superseded;
- no direct CRUD/state reach-through;
- correct AI Kernel position;
- protocol/FactoryIP representation at an appropriate abstraction;
- no invented future Nodes;
- existing 03 CSE/Mission Resolution details clearly treated as later review input if shown.

## 11. Implementation plan gate

After Assessment + Architecture Challenge, produce a concrete file-by-file Implementation Plan.

For each file specify:

- why it changes;
- decision IDs implemented;
- sections/diagrams changed;
- whether content is added/refined/superseded/moved;
- migration/supersession notes;
- verification method.

If repository governance requires Product Owner approval before state-changing implementation, STOP after the plan and request approval with a durable reference/hash.

## 12. Verification — mandatory second independent traversal

After edits, perform a fresh repository-wide verification, not merely a diff review.

### 12.1 Decision → Constitution
Every ACCEPTED Lossless Ledger entry must map to final canonical text/diagram or explicit approved non-constitutional treatment.

### 12.2 Constitution → Decision
Every new/changed canonical statement must trace to an accepted decision or be clearly marked non-normative editorial clarification.

### 12.3 Terminology sweep
Search old and new terms repository-wide. Report all remaining canonical conflicts, especially:

- Context Profile;
- Cognitive Profile;
- FactoryIP / Factory Packet / Factory Message;
- Evidence;
- provenance/lineage;
- Artifact;
- Knowledge Candidate;
- Result/Outcome/Projection;
- Claim;
- Resolution;
- Node/service/domain;
- FFS;
- Zoning;
- Kernel/Cognitive Processing.

### 12.4 Negative invariant verification
Prove absence of canonical architecture that permits:

- cross-domain direct state writes;
- Conversation/message CRUD as FactoryIP canonical service model;
- semantic retrieval before scope eligibility;
- Understanding/Evaluation/Kernel business authority;
- full Artifact automatic AKB publication;
- Evidence/Artifact/Knowledge identity collapse;
- mutable Artifact Version applicability/governance semantics;
- duplicate Artifact dependency graph;
- FactoryIP internal reach-through;
- mandatory FFS data-plane proxy;
- Zoning as domain authorization;
- premature 03+ Node topology.

### 12.5 Layer completeness
For each L0–L4 prove the final corpus defines:

- purpose;
- owner/authority boundary;
- inputs/outputs or carried semantics;
- invariants;
- non-responsibilities;
- relation to adjacent layers.

### 12.6 Diagram/text consistency
Every normative diagram must agree with normative text. No stale canonical diagram may remain active.

## 13. Required Closure Report

Produce a closure report containing:

1. executive result: PASS / BLOCKED / FAIL;
2. baseline commit and final commit;
3. changed file list;
4. file/line evidence for every decision family;
5. Decision → Constitution traceability table;
6. Constitution → Decision traceability table;
7. superseded terminology list;
8. remaining OPEN/DEFERRED items;
9. 03 handoff list;
10. future-section impacts;
11. diagram verification evidence;
12. repository-wide terminology search evidence;
13. negative-invariant verification;
14. any architecture challenge requiring Product Owner decision;
15. explicit statement whether **every ACCEPTED entry in `LOSSLESS_APPROVED_DECISION_LEDGER.md` is represented**.

Closure MUST NOT report PASS if any accepted decision is missing, weakened, contradicted, or silently converted into an open/proposal state.

## 14. Final rule

**Decision loss is a closure failure.**

The goal is not to produce a short Constitution. The goal is to produce a coherent Constitution whose normative wording can be traced back to every individually approved Product Owner decision while still avoiding duplicated ownership and unnecessary implementation detail.
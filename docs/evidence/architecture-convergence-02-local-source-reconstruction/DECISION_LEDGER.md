# Source-derived decision ledger

The IDs below are reconstruction IDs. They deliberately do not reuse unstable
historical `CU-*` / `FP-*` names as decision identity. Evidence locators are
deterministic (`CHAT-####`); quoted words are short semantic labels, not a copy
of the private corpus.

| ID | Final approved semantic | Principal evidence / lineage | State |
|---|---|---|---|
| R-01 | Before MVP, an incorrect architecture may be replaced; backward compatibility is not itself a veto. | `CHAT-0003`–`0004` | Approved |
| R-02 | Architecture Convergence defines target semantics; Implementation Convergence implements the delta and must not redefine the target. | `CHAT-0011`–`0012`, `0063`–`0074` | Approved |
| R-03 | Conversation is a bridge between Product Owner interaction and Mission; it does not itself decide or own Mission semantics. | `CHAT-0031`–`0032` | Approved |
| R-04 | Conversation semantic state and lifecycle state are distinct concerns; a new idea enters proposal/challenge rather than unstable ping-pong state. | `CHAT-0033`–`0038`, `0061`–`0062` | Approved |
| R-05 | Persona is not Context Profile. A canonical Context Package and profile-resolution process provide relevant context to consumers. | `CHAT-0045`–`0058` | Approved |
| R-06 | Conversation Understanding (CU) is a stateless Context Package consumer, not Conversation State authority. | `CHAT-0083`–`0085` | Approved |
| R-07 | Understanding Result is immutable, structured interpretation/evidence; it is distinct from observed facts and has no direct write authority over Conversation State. | `CHAT-0085`–`0086`, `0131`–`0134`, `0147`–`0150` | Approved |
| R-08 | Cognitive processing is a reusable stateless capability. A processing request is an invocation contract, not automatically a first-class durable Artifact. | `CHAT-0093`–`0096`, `0107`–`0108` | Approved |
| R-09 | Effective scope resolves applicable profile/policy, supports tenant/language variation, and carries non-overridable architecture/security invariants. | `CHAT-0113`–`0118`, `0173`–`0178` | Approved |
| R-10 | Profile resolution diagnoses resolution failure; it does not solicit the user, skip controls, or directly repair the state. | `CHAT-0123`–`0128` | Approved |
| R-11 | Evaluation is a generic stateless service. Historical interpretation and present applicability are separate assessments. | `CHAT-0131`–`0138` | Approved |
| R-12 | CSM orchestrates Conversation state transitions; it is not a top-level universal master orchestrator. Feedback reaches the right actor through event/outcome semantics rather than irrelevant stack traces to the PO. | `CHAT-0139`–`0146` | Approved |
| R-13 | Artifact is an immutable end product. Persistence is contract-driven: non-central, unconnected material need not be durable. | `CHAT-0155`–`0160` | Approved |
| R-14 | Evidence proves that an Artifact was warranted and how it was produced; Evidence is a first-class concern, not merely incidental logging. | `CHAT-0161`–`0164`, `0179`–`0192` | Approved |
| R-15 | Factory Protocol is layered. L0 Effective Scope, L1 Evidence, L2 Provenance/Causality, L3 Artifact/Knowledge, and L4 Factory Message are separate canonical packages. | `CHAT-0165`–`0178`, `0241`–`0244`, `0301`–`0304`, `0381`–`0382` | Approved |
| R-16 | L1 records evidence at contract-defined handoffs, with defined granularity, contents, recording authority, and sufficiency. | `CHAT-0180`–`0192` | Approved |
| R-17 | L2 represents causal/provenance relations with canonical families, directional/inverse semantics, temporal/version lifecycle and explicit activation authority/evidence. | `CHAT-0194`–`0228` | Approved |
| R-18 | Relations are never erased to hide history: they receive lifecycle status and append history. RETRACTED is distinct from an unresolved/pending condition. | `CHAT-0209`–`0216` | Approved |
| R-19 | Relation evidence can be challenged and re-evaluated; assurance is an Evaluation output with canonical result states. | `CHAT-0229`–`0240` | Approved |
| R-20 | Artifacts are immutable and versioned. A new version is a new materialization of the same identity/meaning/contract; contract defines lifecycle/governance and state handling. The approved Artifact Contract covers qualification, semantic purpose, identity/versioning, persistence, integrity, governance/lifecycle and authority. Version metadata is distinct from an inline or externally held immutable payload; payload change requires a new version/integrity failure. Composition uses concrete immutable versions and L2 is the canonical provenance/causality mechanism. Historical validity is distinct from current applicability; retention/availability changes do not rewrite history; unresolved external authority is handed to L4. | `CHAT-0245`–`0262`, `0293`–`0295`, `0412`–`0417` | Approved; `CHAT-0295` direct approval restores the previously missing detail locator |
| R-21 | An Artifact is not copied wholesale into knowledge. Semantically independent knowledge candidates are resolved for publication. | `CHAT-0263`–`0272` | Approved |
| R-22 | Claim merits first-class treatment when it carries explicit accountable decision ownership (for example PO or Domain); ambiguous conflicts may require it, simple workflow-resolvable ones need not. | `CHAT-0275`–`0282` | Approved |
| R-23 | L4 is not resolution-only. It is Factory Message Protocol: envelope, delivery/interaction semantics, and payload contract at genuine domain/protocol boundaries. | `CHAT-0285`–`0304` | Approved |
| R-24 | FactoryIP is the full L0–L4 boundary stack. A Factory Packet carries the layers between source and destination; each domain contributes its boundary information. | `CHAT-0301`–`0308`, `0327`–`0330` | Approved |
| R-25 | FFS is logically one authoritative fabric service but not necessarily one physical instance. In MVP it is a thin/static name-routing control plane, not a data-plane proxy; HA is deferred. | `CHAT-0311`–`0328` | Approved |
| R-26 | Zoning is the canonical source-to-destination communication authorization mechanism. It is distinct from domain authorization and replaces a separate inbound/outbound/forbidden communication contract. | `CHAT-0322`–`0328`, `0355`–`0358` | Approved; correction applied |
| R-27 | A FactoryIP Node exposes services to the LAN. Node qualification is explicit. Factory Chat is its own addressable FactoryIP Node while remaining a UI boundary, not Runtime or Conversation owner. | `CHAT-0339`–`0350` | Approved |
| R-28 | No unreviewed domain is integrated into the LAN model. AI Kernel is not Cognitive Processing; it must retain its separately defined meaning. | `CHAT-0351`–`0354`, `0365`–`0370` | Approved correction |
| R-29 | The current Constitution is baseline, not automatic target; approved convergence decisions may be absent from it and must be compared only after source reconstruction. | `CHAT-0369`–`0372` | Approved |
| R-30 | The full cross-cutting foundation (each L0–L4 layer, FactoryIP, FFS, Nodes) is a prerequisite canonical convergence change before continuing to 04/MSM. | `CHAT-0377`–`0382` | Approved |
| R-31 | Existing closure/ledger material was incomplete and over-compressed. Reconstruction must preserve approval detail, distinguish intermediate Mermaid states, and not trust current decision IDs. | `CHAT-0396`–`0423` | Approved remediation direction |

## Audit note

The ledger records materially approved semantics, not every assistant proposal.
Where an assistant merely suggests a model and no later Product Owner acceptance
is visible, the item is not promoted to an approved target decision.

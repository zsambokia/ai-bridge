# Chronological conversation timeline

There are no source timestamps. Chronology is therefore the verified
`acquisition_sequence`, shown as inclusive locator ranges.

| Range | Discussion and resulting state |
|---|---|
| `CHAT-0001`–`CHAT-0028` | Convergence method: pre-MVP can replace incorrect architecture; target architecture is separated from implementation convergence. Conversation / Factory Chat / Conversation Understanding become the opening domain boundary. |
| `CHAT-0029`–`CHAT-0076` | Conversation semantics: Conversation bridges Product Owner chat to Mission without deciding itself; semantic state, lifecycle, persona/context/profile distinctions, Context Package and FDM/implementation-delta handling are developed. |
| `CHAT-0077`–`CHAT-0150` | Conversation Understanding: stateless consumer; immutable Understanding Result; scope/profile resolution, evaluator and CSM boundaries; authority and feedback limits. |
| `CHAT-0151`–`CHAT-0178` | Cross-cutting Artifact/Evidence definitions and approval of a layered Factory Protocol; L0 Effective Scope is closed. |
| `CHAT-0179`–`CHAT-0244` | L1 Evidence and L2 Provenance/Causality: evidence contract, relations, temporal lifecycle, activation authority, challenge/re-evaluation and assurance. |
| `CHAT-0245`–`CHAT-0300` | L3 Artifact/Knowledge/Claim and the transition to L4: immutable versioned artifacts; knowledge candidates; claims need accountable decision ownership; L4 cannot be resolution-only. `CHAT-0293`–`0295` is the explicit L3 closure sequence: seven remaining Artifact proposals are reviewed and individually accepted by the Product Owner; `CHAT-0297` later refines L4 so it is not resolution-only. |
| `CHAT-0301`–`CHAT-0330` | L4 Factory Message/Packet, FactoryIP, FFS and Zoning. FFS is simplified to a thin control-plane service; MVP high availability is deferred; LAN review starts. |
| `CHAT-0331`–`CHAT-0374` | Node model and Factory Chat as an independently addressable UI node. Explicit corrections: AI Kernel is not Cognitive Processing; no unreviewed domains are imported; Zoning is the canonical communications gate. Constitution is a baseline, not automatic target. |
| `CHAT-0375`–`CHAT-0425` | Closure direction: the approved 02 changes, including each L0–L4 layer, FactoryIP, FFS and Nodes, must become canonical before proceeding toward MSM. Existing reconstructions are found incomplete/compressed; decision IDs show semantic drift. |
| `CHAT-0426`–`CHAT-0443` | Evidence-acquisition discussion: a six-message corpus is rejected as incomplete; marker-based local capture is designed and tested. These messages explain why this local acquisition exists; they do not supersede the architecture decisions above. |

## Decision-lineage rule used

For every target claim, the analysis follows proposal → Product Owner reaction
→ accepted semantic → later correction/refinement. Assistant labels such as
`CU-06` or `FP-L3/…` are evidence aids only; they do not define decision
identity. A later explicit correction (for example `CHAT-0351`–`CHAT-0356`)
supersedes an earlier assistant formulation.

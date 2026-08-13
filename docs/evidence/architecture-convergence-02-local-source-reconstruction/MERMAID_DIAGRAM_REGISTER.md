# Mermaid diagram register

The normalized source contains 106 `mermaid` fenced blocks. The acquisition
does not preserve attachment metadata or a separate diagram identity, so the
reproducible identifier is `MMD-CHAT-####-NN`, where `####` is the containing
message locator and `NN` is its one-based Mermaid-block ordinal.

## Classification rule

Each block must be classified as one of: proposal, explanatory example,
intermediate accepted state, or final semantic evidence. A diagram is never
final merely because it was supplied as a Mermaid attachment; later prose and
explicit corrections determine supersession.

## Material diagram regions

| Region | Likely subject | Treatment |
|---|---|---|
| `CHAT-0031`–`0062` | Conversation state, context and lifecycle | supports R-03–R-05; validate against later state separation. |
| `CHAT-0083`–`0150` | CU/Cognitive Profile/CSM flows | supports R-06–R-12; result authority limits prevail. |
| `CHAT-0165`–`0304` | Factory Protocol L0–L4 and Artifact/Knowledge flows | supports R-13–R-24; preserve layer separation. |
| `CHAT-0301`–`0370` | Factory Packet, FactoryIP, FFS, Node and LAN views | supports R-24–R-29; apply FFS/Zoning/AI-Kernel corrections. |
| `CHAT-0402`–`0407` | Attached earlier Mermaid materials reviewed during reconstruction | explicitly potentially intermediate; do not auto-promote to final. |

The source attachments themselves are not copied into Git. Future diagram
reconciliation should reference source locators and this scheme, and must
record a decision-level conclusion for all 106 blocks before declaring visual
coverage complete.

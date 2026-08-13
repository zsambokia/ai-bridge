# Mermaid evolution register

The corpus contains many diagrams embedded in an iterative design discussion.
This register records the controlling evolution rules before diagram-level
reconciliation; it does not fabricate final diagram semantics from filenames
or assistant prose.

| Diagram family | Earlier / intermediate risk | Final source control |
|---|---|---|
| Conversation state | State, semantic state and lifecycle were progressively separated. | R-03–R-05; `CHAT-0031`–`0062` |
| CU flow | A diagram can overstate CU authority. | R-06–R-12; Understanding has no direct state write. |
| Protocol stack | Early numbering/frame can conflate L0–L4 concerns. | R-15–R-24; each layer stays distinct. |
| Artifact/knowledge | A drawing can suggest full Artifact → AKB transfer. | R-20–R-22; only semantic candidate/publication flow. |
| Factory/LAN | Earlier FFS or endpoint diagrams may over-centralize the fabric. | R-24–R-27; FFS thin control-plane, Zoning canonical. |
| AI Kernel / LAN | Assistant introduced an unreviewed/incorrect coupling. | R-28; do not include that coupling. |
| Later supplied diagrams | User considered them final, but review found some intermediate. | `CHAT-0402`–`0407`; diagram finality requires lineage verification. |

No diagram is recreated here because this evidence package must not turn a
private, evolving source diagram into an unaudited new canonical artifact.

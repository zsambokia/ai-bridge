---
diagram: 01 Conversation Layer
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Conversation Layer.drawio
constitution: Article IV; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 01 — Conversation Layer
```mermaid
flowchart LR
    PO[Product Owner] --> UI[Factory Chat] --> C[Conversation]
    C --> U[Conversation Understanding] --> CB[Context Builder] --> MR[Mission Resolution]
    C --> CSE[Conversation State Engine] --> MR
    CP[Immutable Context Package] --> MR
    MR --> M[Mission]
```

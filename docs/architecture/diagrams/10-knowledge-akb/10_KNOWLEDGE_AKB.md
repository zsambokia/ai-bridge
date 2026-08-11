---
diagram: 10 Knowledge and AKB
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Knowledge and AKB.drawio
constitution: AKB Knowledge Object and Lifecycle Constitution; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 10 — Knowledge and AKB
```mermaid
flowchart LR
    S[Authoritative Sources] --> KLM[Knowledge Lifecycle Management]
    KLM --> AKB[AKB<br/>published immutable Knowledge Object versions]
    AKB --> KR[Knowledge References] --> CP[Context Package<br/>immutable and reproducible]
    O[Operational Data] -. excluded .-> AKB
```

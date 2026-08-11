---
diagram: 11 Repository Lifecycle
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Repository Lifecycle.drawio
constitution: AKB Knowledge Object and Lifecycle Constitution; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 11 — Repository Lifecycle
```mermaid
flowchart LR
    R[Project-owned Repository] --> C[Governed Change]
    C --> E[Repository / Domain Event] --> D[Knowledge Change Detection]
    D --> P[Knowledge Update Plan] --> KLM[Knowledge Lifecycle Management]
    KLM --> AKB[Published Immutable AKB Version]
    KLM --> CI[Context Invalidation]
```

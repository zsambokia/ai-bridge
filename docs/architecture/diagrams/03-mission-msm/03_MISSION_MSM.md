---
diagram: 03 Mission and MSM
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Mission and MSM.drawio
constitution: Article IV; State Machine Constitution; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 03 — Mission and MSM
```mermaid
flowchart LR
    I[Mission Intake Decision] --> M[Mission]
    M --> MSM[Mission State Machine<br/>exclusive lifecycle authority]
    MSM --> E[Mission Events and Evidence]
    MSM --> OWI[Authorized Immutable Operational Work Item]
```

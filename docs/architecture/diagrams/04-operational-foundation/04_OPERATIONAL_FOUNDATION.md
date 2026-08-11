---
diagram: 04 Operational Foundation
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Operational Foundation.drawio
constitution: Operational Foundation Constitution; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 04 — Operational Foundation
```mermaid
flowchart LR
    OWI[Immutable Operational Work Item] --> ADM[Admission] --> CR[Capability Resolution]
    CR --> CAP[Capability Registry] --> ENG[Engine Definition Registry]
    ENG --> SCH[Scheduler] --> Q[Queue] --> L[Lease Manager] --> K[AI Kernel]
    Q -. governed .-> R[Retry and Recovery]
    Q -. observed .-> T[Telemetry and Health]
```

---
diagram: 08 Execution Layer
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Execution Layer.drawio
constitution: Article III; Provider Architecture v2; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: ADR-034, ADR-038 (open)
---
# Diagram 08 — Execution Layer
```mermaid
flowchart LR
    OWI[Admitted Work] --> ER[Execution Request] --> EX[Execution<br/>Kernel-owned]
    EX --> B[Immutable Provider Binding]
    B --> PE[Provider Executor]
    PE --> R[Result] --> EX
    EX --> EE[Kernel Events and Evidence]
    EX -. same-provider only .-> REC[Recovery]
```

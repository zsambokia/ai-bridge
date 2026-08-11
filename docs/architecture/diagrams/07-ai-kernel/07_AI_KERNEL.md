---
diagram: 07 AI Kernel
architecture_status: CANONICAL
source: Mermaid
derived_drawio: AI Kernel.drawio
constitution: Article III; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: ADR-034, ADR-038 (open)
---
# Diagram 07 — AI Kernel
```mermaid
flowchart LR
    W[Admitted Operational Work] --> ER[Execution Request] --> EX[Execution<br/>Kernel-owned]
    CP[Immutable Context Package] --> EX
    EX --> CR[Capability Resolution] --> PI[Provider Integration]
    EX --> KE[Kernel Events and Evidence]
```

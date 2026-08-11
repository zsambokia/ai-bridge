---
diagram: 06 Workflow Engine
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Workflow Engine.drawio
constitution: Architecture Constitution; AI Kernel Constitution; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 06 — Workflow Engine
```mermaid
flowchart LR
    R[Authorized Work and Workflow Definition] --> WE[Workflow Engine<br/>stateless capability definition]
    CP[Immutable Context Package] --> WE
    WE --> ER[Execution Request] --> EX[Kernel-owned Execution]
    WE --> O[Results, Events, Evidence]
```

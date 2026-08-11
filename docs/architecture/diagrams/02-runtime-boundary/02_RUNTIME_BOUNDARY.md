---
diagram: 02 Runtime Boundary
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Runtime Boundary.drawio
constitution: Article IV; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 02 — Runtime Boundary
```mermaid
flowchart LR
    C[Conversation / Mission Resolution] --> M[Mission]
    A[API / MCP / Scheduler / Webhook / Automation] --> M
    subgraph RB[Runtime Boundary]
        M --> MSM[Mission State Machine] --> OWI[Immutable Operational Work Item]
    end
```

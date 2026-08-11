---
diagram: 09 Provider Layer
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Provider Layer.drawio
constitution: Provider Architecture v2; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: ADR-034, ADR-038 (open)
---
# Diagram 09 — Provider Layer
```mermaid
flowchart LR
    EX[Execution] --> PI[Provider Integration] --> PR[Provider Resolver]
    PR --> P[Provider<br/>stateless capability provider] --> PX[Provider Executor<br/>stateful runtime instance]
    PX --> X[LLM / MCP / Tool / Human / API]
    PG[Provider Gateway<br/>historical implementation adapter] -. not canonical .-> PI
```

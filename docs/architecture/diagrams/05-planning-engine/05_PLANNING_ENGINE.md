---
diagram: 05 Planning Engine
architecture_status: CANONICAL
source: Mermaid
derived_drawio: Planning Engine.drawio
constitution: Architecture Constitution; AI Kernel Constitution; Article V
last_reviewed: 2026-08-11
architecture_version: 1.0.0
related_adrs: []
---
# Diagram 05 — Planning Engine
```mermaid
flowchart LR
    R[Scope-aware Planning Request] --> PE[Planning Engine<br/>stateless capability definition]
    CP[Immutable Context Package] --> PE
    PE --> ER[Execution Request] --> EX[Kernel-owned Execution]
    PE --> O[Versioned Plan, Rationale, Evidence]
```

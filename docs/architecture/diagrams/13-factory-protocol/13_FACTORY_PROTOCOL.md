---
diagram: 13 Factory Protocol
architecture_status: CANONICAL
source: Mermaid
derived_drawio: null
constitution: Article VIII; Article V
last_reviewed: 2026-08-14
architecture_version: 1.0.0
related_adrs: ADR-038
---
# Diagram 13 - Factory Protocol

```mermaid
flowchart LR
    A[Adapter: UI / HTTP / MCP / WebSocket] --> N[Published semantic service]
    N --> L0[L0 Effective Operational Scope]
    L0 --> L1[L1 Evidence references]
    L1 --> L2[L2 Provenance / causality]
    L2 --> L3[L3 Artifact Contract or Knowledge Candidate]
    L3 --> L4[L4 Factory Packet]
    L4 --> D[Destination domain boundary]
    FFS[FFS: logical name/service resolution] -. control plane only .-> N
    Z[Zoning: transport permission] -. permits boundary traffic .-> L4
    K[AI Kernel: post-admission execution] -. not Cognitive Processing or inferred Node .-> D
```

FactoryIP is the complete L0-L4 semantic stack. FFS never proxies payloads;
Zoning is distinct from domain authorization; and no Node is implied by an
internal class, process, or endpoint.

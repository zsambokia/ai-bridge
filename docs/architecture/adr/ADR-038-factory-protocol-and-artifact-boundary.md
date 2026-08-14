---
status: ACCEPTED_TARGET
date: 2026-08-14
owner: Architecture
---

# ADR-038: Factory Protocol and Artifact Boundary

## Decision

Adopt Article VIII, FactoryIP L0-L4, Factory Packet, semantic FactoryIP Nodes,
thin FFS control-plane resolution, and Zoning as the target inter-domain
boundary model. Adopt Artifact Contract qualification and the separate
Artifact-to-Knowledge Candidate-to-Publication Resolution route.

## Consequences

Adapters may not use CRUD or shared-state reach-through to bypass a domain.
FFS is not a payload proxy, Zoning is not domain authorization, and no Node or
Kernel LAN is inferred from a component. Cognitive Processing is stateless and
separate from post-admission AI Kernel execution. Runtime schema, topology,
service matrix, and migration are intentionally not decided here.

## Diagram impact

Created Diagram 13 and updated Diagrams 01, 07, and 10. No derived Draw.io
artifact exists for Diagram 13; Mermaid is the authoritative logical source.

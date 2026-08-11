---
status: APPROVED_TARGET
owner: Architecture
classification: CONSTITUTION DIAGRAM
language: en
version: 1.0.0
---

# Diagram 01 — Conversation Layer

## Purpose

This editable draw.io diagram is the canonical visual companion to the
Conversation → Mission target architecture. It shows only the human
Conversation route and the boundary at which a governed Mission can enter the
runtime path. It is not an implementation, class, API, data-model, or
deployment diagram.

## Constitution references

- [Article IV — Conversation to Mission Architecture](../../CONVERSATION_TO_MISSION_ARCHITECTURE_CONSTITUTION.md)
- [Architecture Constitution](../../ARCHITECTURE_CONSTITUTION.md)
- Article V — Architecture Documentation Governance in the [Architecture Constitution](../../ARCHITECTURE_CONSTITUTION.md)
- [State Machine Constitution](../../STATE_MACHINE_CONSTITUTION.md)
- [AI Kernel Architecture Constitution](../../AI_KERNEL_ARCHITECTURE_CONSTITUTION.md)

## Ownership

Architecture owns the diagram. The canonical target it represents is owned by
the Architecture Constitution and its approved Constitution Book entries.
Under Article V, this diagram is a normative architecture artifact with the
same authority as its corresponding constitutional scope.

## Maintenance rules

1. Keep the source as editable native draw.io (`.drawio`) XML.
   `Conversation Layer.drawio` is the single canonical diagram source. The
   SVG in `assets/` is a derived, non-canonical review preview and MUST be
   regenerated or updated with it.
2. Preserve the component order and the explicit Runtime Boundary unless an
   approved Constitution amendment changes the target architecture.
3. Use logical components and responsibilities only. Do not add source-code
   classes, database tables, endpoints, queues, providers, or deployment
   details.
4. Keep orthogonal connectors, aligned layout, and the defined layer colors:
   blue for UI, green for Conversation Domain, orange for the Runtime Boundary,
   and purple for the Mission Domain.
5. When a change affects constitutional meaning, update the corresponding
   Article, every affected canonical diagram, and its evidence in the same
   approved documentation scope.
6. Every ADR and Architecture Convergence change affecting this diagram SHALL
   include a Diagram Impact Assessment. It SHALL record required changes,
   newly required or obsolete diagrams, or an explicit no-impact justification.
7. Keep the diagram consistent with Article IV. A conflict is an architecture
   defect, not an implementation-specific variation.

## Change policy

Changes are permitted only through the Architecture Convergence Program or a
separately approved Constitution amendment. A diagram change does not by
itself authorize implementation or modify the status of existing historical or
transitional repository artifacts.

The Article V governance amendment was assessed in
[`DIAGRAM_IMPACT_ASSESSMENT.md`](../../../evidence/architecture-documentation-governance-article-v-20260811/DIAGRAM_IMPACT_ASSESSMENT.md).
It changes this diagram's maintenance and authority rules only; the logical
architecture in `Conversation Layer.drawio` was therefore not changed.

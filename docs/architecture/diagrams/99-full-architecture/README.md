---
architecture_status: CANONICAL
constitution_book_entries: Articles III, IV, VIII
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
logical_source: 99_FULL_ARCHITECTURE.md
derived_drawio: Full Architecture.drawio
constitution: Article V — Architecture Documentation Governance
last_reviewed: 2026-08-14
architecture_version: 1.1.0
related_adrs: ADR-034, ADR-038 (open)
---
# Diagram 99 — Full Architecture

## Purpose

The cross-layer canonical target view. It composes, but does not replace, the
more precise numbered diagrams.

The Mermaid document is the canonical logical architecture source. `Full
Architecture.drawio` is its derived editable visual representation; if they
ever conflict, the Mermaid model prevails.

## Responsibility and ownership

Factory Chat is UI/interaction only. Conversation is durable; CSE owns its
state transitions. Context Assembly, Understanding and Evaluation are stateless
Cognitive Processing and have no direct domain-consequence authority. Mission
Resolution is separate, while MSM owns Mission lifecycle. Operational
Foundation owns governed delivery; AI Kernel owns Execution; Providers execute;
AKB owns published knowledge; KLM owns knowledge evolution.

## Contracts, lifecycle, and rules

Human interaction reaches Mission Resolution only through Conversation's CSE.
All entry adapters converge on Mission intake. FactoryIP L0–L4 governs semantic
boundary communication: L0 eligibility precedes retrieval, FFS resolves
name/service bindings without proxying payloads, and zoning is distinct from
domain authorization. MSM authorizes immutable Work Items, Foundation admits
them, Kernel owns Execution, and the canonical provider route is Integration
-> Resolver -> Provider -> Executor. Context Packages are immutable references
to governed knowledge.

## Failure, evidence, and open questions

Historical dashed items only document current implementation vocabulary:
`ExecutionRun`, `ExecutionJob`, and `Provider Gateway`. They are not target
objects. Their final disposition is ADR-governed.

## Related authority and maintenance

Architecture Constitution Articles III–V, Conversation-to-Mission, Provider v2,
AKB, Operational Foundation, and the Constitution Book plan. Any architecture
change requires this diagram's impact assessment.

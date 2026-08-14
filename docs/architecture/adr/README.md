---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Architecture Decision Records

## Governance

ADRs are Architecture Convergence records. They record durable architecture
decisions; implementation contracts and Sprint evidence record realization
decisions. Product Owner approval is required when an ADR materially changes a
canonical concept, ownership/responsibility boundary, invariant, lifecycle,
scope rule, security guarantee or compatibility exception. See [Architecture
and Implementation Convergence Governance](../ARCHITECTURE_IMPLEMENTATION_CONVERGENCE_GOVERNANCE.md)
for the Architecture Challenge and decision rule.

The ADRs below are the durable architectural decisions for the Orki Cognitive
Operating System. Their status describes an architectural or capability
lifecycle; it must not be read as proof of a mature, independently judged
Digital COO behavioural result.

| ADR | Decision | Current closure position |
| --- | --- | --- |
| [ADR-001](ADR-001-cognitive-state.md) | Cognitive State | Implemented and accepted in ORKI-001 |
| [ADR-002](ADR-002-decision-engine.md) | Decision Engine | Implemented and independently release-gated |
| [ADR-003](ADR-003-initiative-engine.md) | Initiative Engine | Implemented through Level 1 observation |
| [ADR-004](ADR-004-planning-intelligence.md) | Planning Intelligence | Implemented and independently release-gated |
| [ADR-005](ADR-005-memory-intelligence.md) | Memory Intelligence | Implemented in ORKI-006 |
| [ADR-006](ADR-006-recommendation-engine.md) | Recommendation Engine | Implemented and independently release-gated |
| [ADR-007](ADR-007-governance-boundary.md) | Governance Boundary | Accepted architecture boundary |
| [ADR-008](ADR-008-llm-independence.md) | LLM Independence | Accepted architecture boundary |
| [ADR-009](ADR-009-mission-evolution.md) | Mission Evolution | Accepted architecture boundary; ORKI-002 capability evidence |
| [ADR-010](ADR-010-evidence-driven-reasoning.md) | Evidence-Driven Reasoning | Accepted boundary; bounded ORKI-010 structure |
| [ADR-011](ADR-011-product-owner-cognitive-model.md) | Product Owner Cognitive Model | Implemented and foundation-accepted |
| [ADR-012](ADR-012-product-owner-model-evolution.md) | Product Owner Model Confidence and Drift | Implemented and accepted |
| [ADR-013](ADR-013-operational-reasoning-engine.md) | Operational Reasoning Engine | Implemented; full scenario certification pending |
| [ADR-014](ADR-014-architecture-constitution.md) | Architecture Constitution | Accepted target governance |
| [ADR-015](ADR-015-operational-foundation-constitution.md) | Operational Foundation Constitution | Accepted target boundary |
| [ADR-016](ADR-016-runtime-mission-coordinator.md) | Runtime as Mission coordinator only | Accepted target boundary |
| [ADR-017](ADR-017-operational-foundation-engine-boundary.md) | Operational Foundation as canonical Engine boundary | Accepted target boundary |
| [ADR-018](ADR-018-engine-constitution.md) | Common Engine Constitution | Accepted target governance |
| [ADR-019](ADR-019-state-machine-ownership.md) | State-machine ownership | Accepted target governance |
| [ADR-035](ADR-035-scope-resource-and-ownership.md) | Scope, Resource and Direct Ownership | Accepted target architecture; implementation inheritance/shared-resource details remain open |
| [ADR-037](ADR-037-localization-and-canonical-language.md) | Localization and Canonical Language | Accepted target architecture; representation mechanics remain open |
| [ADR-038](ADR-038-factory-protocol-and-artifact-boundary.md) | Factory Protocol and Artifact Boundary | Accepted target architecture; runtime topology and schema remain open |

For technical Epic closure evidence, see the
[Product Owner review package](../../evidence/orki-cognitive-operating-system-closure-20260802/PRODUCT_OWNER_REVIEW_PACKAGE.md).

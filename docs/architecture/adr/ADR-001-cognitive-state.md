# ADR-001 - Cognitive State

**Status:** Implemented in ORKI-001; Cognitive State Release Gate accepted.

## Decision

Orki shall use a persistent, project-isolated Cognitive State as its primary
working memory. Conversation messages are observations that may update state;
they are not themselves memory.

The state shall represent mission, business context, goals, constraints, facts,
evidence, assumptions, risks, opportunities, alternatives, trade-offs,
recommendations, confidence, decisions, architecture, roadmap, sprint strategy,
repository and delivery status, learned knowledge, reasoning trace, and memory.

## Consequences

State changes need provenance, confidence, correction, and lifecycle rules.
Transcript replay alone cannot reconstruct authoritative knowledge.

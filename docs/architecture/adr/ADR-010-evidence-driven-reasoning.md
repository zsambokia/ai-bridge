# ADR-010 - Evidence Driven Reasoning

**Status:** Accepted architectural boundary; ORKI-010 provides the bounded reasoning structure, while full behavioural certification remains pending.

## Decision

Material reasoning shall retain evidence references and classify statements as
fact, assumption, inference, alternative, or recommendation. Confidence is
derived from available evidence and must not conceal gaps.

## Consequences

Scenario certification can inspect why Orki made a recommendation, what it did
not know, and which decision remains with the Product Owner.

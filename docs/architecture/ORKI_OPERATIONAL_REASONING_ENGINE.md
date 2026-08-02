# Orki Operational Reasoning Engine

**Status:** Canonical architecture; ORKI-010 implementation and release-gate contract.
**Authority:** [Orki Principles](ORKI_PRINCIPLES.md) and the approved [ORKI-010 Sprint](../sprints/SPRINT_ORKI_010_OPERATIONAL_REASONING_ENGINE.md).

## Purpose

The Operational Reasoning Engine (ORE) makes the Digital COO's operational
thinking inspectable before a recommendation is recorded. It is not a prompt
format or a recommendation generator. It creates one project-scoped,
versioned Cognitive State artefact whose derived recommendation is valid only
when the reasoning contract is complete.

## Canonical reasoning cycle

```text
Mission
  -> attributable evidence + explicit assumptions + material unknowns
  -> at least three alternatives
  -> trade-offs and a counter-argument for every alternative
  -> risk, cost, long-term effect, and simplicity assessment
  -> expected impact
  -> late recommendation
  -> confidence and required Product Owner decision
```

Each alternative contains an option, concise summary, cost, risk, long-term
effect, and a simplicity score from 1 to 10. Every alternative has a separate
trade-off and counter-argument. The engine rejects a cycle with fewer than
three alternatives, missing source state, cross-project references, or a
recommendation supplied directly to the Factory Chat boundary.

## State and provenance

The canonical entry kind is `OPERATIONAL_REASONING`. Its value retains the
mission reference, evidence and assumption references, unknowns, alternatives,
trade-offs, counter-arguments, expected impact, required-decision boundary,
and transparent Product Owner Model influences. The entry's confidence is a
separate bounded state value. An attributable evidence entry records the
reasoning outcome; the derived Recommendation Engine records remain linked to
the same source state.

The Product Owner Model may adapt a safe default only when the relevant
project-scoped profile is active and evidence-bound. Its dimension, value,
confidence, and supporting evidence are included in the reasoning artefact.
It cannot alter a mission, override facts, create approval, or conceal why a
recommendation differs for another Product Owner.

## Boundary rules

- Conversation is an observation source, never the reasoning state or memory.
- The provider may propose structured reasoning but cannot write canonical
  recommendations directly through Factory Chat.
- A recommendation is persisted only by the ORE after the full contract has
  been validated; the existing Recommendation Engine is the derived
  recommendation record, not a bypass.
- An ORE cycle can identify a required business decision, but it cannot accept
  that decision or initiate governance/execution.
- Revisions supersede the active reasoning snapshot by stable reasoning key;
  state remains project-isolated and explainable.

## Measuring behaviour

The ORKI-010 Release Gate validates an executable reasoning cycle, evolution,
isolation, failure-closed validation, and the Factory Chat boundary. DCMI may
increase only after diverse, independently evidenced operational scenarios
show sustained improvement; implementation and a green unit suite alone do
not change the score.

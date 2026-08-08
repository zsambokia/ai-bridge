# AI Bridge 2.0 Sprint 07 — Cognitive & Behaviour Evolution

**Status:** APPROVED — Factory Development Mode

## Authority

This Sprint is authorised by the Product Owner decision recorded in the
execution handoff. Factory Readiness Sprint 6 is a separate operational
acceptance programme and is not an implementation precondition for this AI
Bridge 2.0 architectural Sprint.

## Objective

Implement the MVP Cognitive & Behaviour Evolution layer so AI Bridge can
accumulate evidence-bound experience from governed execution outcomes and
prepare governed behaviour improvements without changing execution authority.

## Approved scope

- Cognitive Evolution Engine
- Behaviour Evolution Model
- Experience Memory
- Behaviour Pattern Library
- Strategy Evolution
- Reasoning Improvement Loop
- Reflection Quality Evaluation
- Behaviour Candidate Governance
- Cognitive Metrics
- Canonical Cognitive E2E Acceptance Suite

## Canonical boundary

```text
Governed execution outcome
    -> CognitiveExperience
    -> BehaviourCandidate (non-authoritative)
    -> explicit governance approval
    -> active BehaviourPattern
    -> CognitiveGuidancePackage
    -> existing Reasoning consumer
```

The layer may produce evidence and bounded guidance only. It must not execute
work, create a Structured Decision, approve a candidate, mutate Runtime state,
or alter an AKB entry, embedding, vector index, or semantic result.

## Frozen components

The following components are public-contract consumers only and must not be
modified by this Sprint:

- Orki Runtime and Runtime State Machine;
- Semantic Layer;
- Knowledge Pipeline and AKB lifecycle;
- Reasoning Framework;
- Structured Decision Framework;
- Provider Gateway;
- `runtime_knowledge_compat.py`.

## Required acceptance scenarios

1. A project-scoped, evidence-bound verified outcome becomes one idempotent
   experience record; malformed or cross-project evidence is rejected.
2. An experience can create a non-active BehaviourCandidate with deterministic
   provenance and quality evaluation; candidate creation has no Runtime,
   decision, AKB, embedding, or vector side effect.
3. Only an explicit attributable governance approval activates a candidate;
   rejection cannot become active.
4. A CognitiveGuidancePackage exposes only approved project-scoped behaviour
   patterns plus evidence and metrics for a subsequent Reasoning consumer; it
   does not invoke Reasoning or Runtime.
5. The canonical E2E test proves outcome -> experience -> candidate -> approval
   -> guidance while preserving project isolation and all frozen boundaries.

## Release Gate additions

In addition to the canonical evidence-driven Sprint workflow, run the complete
repository Release Gate and the Sprint 7 cognitive acceptance suite. Evidence
is stored under
`docs/evidence/ai-bridge-2-0-sprint-07-cognitive-behaviour-evolution/`.

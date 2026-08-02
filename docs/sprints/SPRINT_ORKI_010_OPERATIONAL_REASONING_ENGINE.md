# Sprint ORKI-010 — Operational Reasoning Engine

**Status:** PASS - READY FOR PRODUCT OWNER REVIEW
**Epic:** Orki Cognitive Operating System
**Authority:** Product Owner directive, 2026-08-02
**Execution profile:** Factory Development Mode — AI Bridge self-development
**Prerequisites:** ORKI-009 Product Owner Model Evolution accepted; DCMI 66/100.

## Objective

Make structured, evidence-driven operational reasoning a canonical Orki
capability. A recommendation must be the late, inspectable output of a
reasoning cycle; it must not be admitted from a model prompt as an unsupported
stand-alone conclusion.

## Scope

- Persist a project-scoped Operational Reasoning artefact in Cognitive State.
- Require each cycle to contain mission references, evidence, explicit
  unknowns, at least three alternatives, trade-offs, counter-arguments, risk,
  cost, long-term effect, simplicity score, expected impact, confidence and a
  required-decision assessment.
- Derive the canonical recommendation from the validated reasoning artefact,
  with full provenance and without execution authority.
- Explain any Product Owner Cognitive Model influence by reference, never by
  undisclosed personalisation or transcript retention.
- Reject missing, foreign, conflicting or insufficient evidence; reject a
  recommendation that bypasses the reasoning artefact at the Factory Chat
  boundary.
- Prove evolution, explainability, project isolation, conflict handling,
  transcript exclusion and long-cycle stability with executable tests.

## Explicit exclusions

- No autonomous execution, governance approval, accepted-decision creation,
  plan creation or Product Owner decision on Orki's behalf.
- No new UI workflow, provider-specific business behaviour, personal-data
  profile, cross-project memory or transcript-as-memory store.
- No DCMI increase unless final executable evidence demonstrates a measurable
  behavioural improvement under the ORKI-010 scorecard criteria.

## Canonical reasoning contract

```text
Mission → Evidence → Unknowns → Alternatives (minimum 3) → Trade-offs
→ Counter-arguments → Risk / Cost / Long-term effect / Simplicity
→ Expected impact → Recommendation → Confidence → Required decision
```

All state references must be active, project-local Cognitive State entries.
The provider may propose structured content, but deterministic Orki validation
owns admissibility and recommendation derivation.

## Acceptance scenarios

1. A stock-optimisation mission produces three complete alternatives and a
   recommendation derived from referenced mission/evidence/assumptions.
2. A later, better-evidenced cycle supersedes the active reasoning and evolves
   recommendation confidence without erasing history.
3. Missing evidence, fewer than three alternatives, an unanalysed alternative,
   or a direct chat recommendation without reasoning is fail-closed.
4. A project cannot inspect or cite another project's reasoning or evidence.
5. A conflicting Product Owner profile cannot silently influence a cycle.
6. Reasoning projection exposes the full decision basis while excluding raw
   conversation body and grants no planning, governance or execution authority.

## Release Gate additions

In addition to the canonical evidence-driven sprint gate, PASS requires:

- independent executable Operational Reasoning acceptance scenarios;
- migration and Django system-check proof;
- Factory Chat provider-boundary proof that direct recommendation payloads are
  rejected and structured reasoning is accepted;
- documented operational runtime smoke;
- independent audit and self-critique; and
- a DCMI capability matrix update based only on final measured evidence.

## Required context

- `docs/architecture/ORKI_COGNITIVE_OPERATING_SYSTEM.md`
- `docs/architecture/ORKI_PRINCIPLES.md`
- `docs/architecture/ORKI_COGNITIVE_DATA_FLOW.md`
- `docs/architecture/ORKI_PRODUCT_OWNER_COGNITIVE_MODEL.md`
- `docs/architecture/ORKI_DCMI_SCORECARD.md`
- `docs/roadmap/ROADMAP.md`
- `docs/akb/CURRENT_STATE.md`
- `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`

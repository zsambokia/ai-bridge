# Sprint ORKI-004 - Decision Intelligence

**Status:** PASS - independent Release Gate passed; autonomous continuation to ORKI-005
**Epic:** Orki Cognitive Operating System
**Authority:** Product Owner autonomous-execution directive, 2026-08-02
**Prerequisites:** ORKI-001 accepted; ORKI-002 and ORKI-003 independent Release Gates - PASS

## Objective

Prove that Orki can turn an evidence-backed recommendation into an explainable
open decision, and can record an accepted decision only from an explicit,
attributable Product Owner decision record. Decision Intelligence is a durable
cognitive capability, not provider prose, a plan, a governance approval, or an
execution command.

## Scope

- Persist project-isolated `OPEN_DECISION` and `ACCEPTED_DECISION` Cognitive
  State with lifecycle evolution.
- Require an active same-project recommendation, its evidence, assumptions,
  alternatives, trade-offs, confidence, consequences, and materiality before
  opening a material decision.
- Make a concise required decision, options, recommendation, trade-offs,
  impact of deciding/deferment, and confidence explainable in a canonical
  projection.
- Accept an option only through an explicit Product Owner actor and durable
  confirmation reference. Provider output and raw conversation text may open a
  decision but may never accept one.
- Test decision evolution, conflicting or stale decision handling, project
  isolation, transcript separation, explainability, and the public Factory
  conversation authority boundary.

## Explicit exclusions

- No planning, roadmap, Sprint, repository, contract, governance approval, or
  execution creation.
- No implicit acceptance inferred from affirmative language, provider output,
  or a chat transcript.
- No initiative or memory capability.
- No UI redesign.

## Required behavioural scenarios

1. An evidence-backed recommendation that requires a decision produces an
   explainable, material open decision with at least two options.
2. A recommendation that does not require a Product Owner decision cannot be
   promoted into one without an explicit materiality reason.
3. A provider-originated or conversation-originated input cannot create an
   accepted decision.
4. An explicit Product Owner actor and confirmation reference accept exactly
   one active option and supersede the open decision.
5. A stale or conflicting acceptance is rejected without losing the prior,
   inspectable state.
6. Project A cannot read or accept Project B's decision; state stores source
   identifiers/hashes rather than a transcript copy.
7. The public Factory route cannot create a plan, governance action, or
   execution as a consequence of decision reasoning.

## Release Gate

PASS requires all required behavioural scenarios, focused and full backend
tests, browser E2E, schema checks, static analysis, architecture/ADR/AKB/
roadmap/documentation synchronization, an independent evidence assessment,
operational validation, and self-critique. Only then may ORKI-005 Planning
Intelligence begin automatically.

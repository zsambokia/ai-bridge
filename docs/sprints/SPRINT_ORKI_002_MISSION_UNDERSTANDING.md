# Sprint ORKI-002 - Mission Understanding

**Status:** Approved for Factory Development Mode implementation
**Epic:** Orki Cognitive Operating System
**Authority:** Product Owner decision, 2026-08-01
**Prerequisite:** ORKI-001 Cognitive State Release Gate - PASS

## Objective

Prove that Orki can construct and evolve a project-scoped Mission State from
Product Owner observations before recommendation or planning begins. This is a
measurable cognitive capability, not a chat, UI, streaming, recommendation, or
planning Sprint.

## Scope

- A canonical Mission Understanding service that consumes attributable,
  project-scoped Cognitive State observations and produces a typed proposed
  Mission State.
- Explicit separation of stated intent, inferred business goal, constraints,
  solution proposals or technology preferences, safe assumptions, and material
  unknowns.
- Deterministic semantic-equivalence rules and a bounded provider-adapter
  contract so materially equivalent Product Owner formulations produce the
  same Mission State semantics.
- A question-budget record and policy: use a safe explicit assumption or
  default unless an answer materially changes the next safe action or is a
  Product Owner decision.
- Attribution, confidence, correction/supersession, project isolation, and an
  explainable Mission projection built on ORKI-001 Cognitive State.
- Independent executable acceptance scenarios and a Mission Understanding
  Release Gate with retained evidence.

## Explicit exclusions

- Recommendation, Decision, Initiative, Planning, and Memory Intelligence.
- New Factory Chat UX, streaming behaviour, question wizard flows, approval,
  scope creation, execution, or AKB publication.
- A claim that Mission Understanding is accepted business intent; it may only
  create an attributable proposed Mission and clearly mark what remains
  unknown or requires a business decision.

## Principles

ORKI Principles 1-9, 12, 14-20 apply directly. In particular, conversation is
not state, facts and assumptions remain separate, questions are expensive, and
the Product Owner must be guided rather than interviewed.

## Required acceptance scenarios

Every scenario uses the production Cognitive State and Mission Understanding
service path, is project-isolated, and records input, evidence, resulting
state, explainability projection, and PASS/FAIL outcome.

| Scenario | Required result |
| --- | --- |
| Equivalent formulations | Two materially equivalent Product Owner formulations produce the same canonical Mission State semantics, despite different wording. |
| Hidden business objective | A request framed as a feature or technology identifies the supported business outcome as an explicitly marked inference, not a fact. |
| Attribute separation | Stated goal, implementation suggestion, technology preference, constraints, assumptions, and unknowns are stored in separate typed state. |
| Safe default | When a reversible default permits the next safe action, Orki records an explicit assumption/default and asks no question. |
| Material question | When an answer changes the next safe action or is reserved to the Product Owner, Orki records exactly one concise, purpose-bound question. |
| Correction and conflict | New attributable evidence supersedes a conflicting proposed mission element rather than silently overwriting it. |
| Explainability and isolation | A projection shows source evidence, fact/assumption/inference distinction, confidence, and question rationale; another project cannot observe it. |

## Mission Understanding Release Gate

The Sprint passes only when all are PASS:

- Engineering Acceptance and complete repository regression gates.
- Operational Acceptance appropriate to the configured local Factory
  Development Mode runtime.
- Independent Mission Understanding behavioural audit, separate from unit
  tests and exercising the canonical service through its public application
  boundary where available.
- Equivalent-formulation, hidden-goal, attribute-separation, safe-default,
  material-question, conflict, explainability, and project-isolation scenarios.
- Question Budget: every question has a durable purpose and a demonstrated
  material effect; no unnecessary question is accepted.
- COO Capability Acceptance: **Mission Understanding PASS** and only the
  applicable foundation dimensions may be assessed. No later engine may be
  claimed complete.
- Updated architecture, ADR status where implementation changes it, Product
  Owner scenarios, AKB, roadmap, self-critique, and evidence bound to the
  final state.

## Completion boundary

Only an independently evidenced Mission Understanding PASS allows ORKI-003
Recommendation Intelligence to begin. A green provider response, unit test,
or UI demo alone is insufficient.

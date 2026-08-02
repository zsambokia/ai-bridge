# Sprint ORKI-003 - Recommendation Engine

**Status:** PASS — independent Release Gate passed; autonomous continuation to ORKI-004
**Epic:** Orki Cognitive Operating System
**Authority:** Product Owner autonomous-execution directive, 2026-08-02
**Prerequisite:** ORKI-002 Mission Understanding Release Gate - PASS

## Objective

Prove that Orki can create, evolve, and explain a prioritised, evidence-based
recommendation from project-scoped Cognitive State. A recommendation is a
durable cognitive artefact, not provider prose, a chat transcript, a plan, or
an instruction to execute work.

## Scope

- A canonical Recommendation Engine that reads only attributable,
  project-scoped Cognitive State and writes independently explainable
  recommendation records back to that state.
- A bounded provider-adapter contract that can propose a recommendation but
  cannot make evidence, assumptions, decisions, plans, governance actions, or
  execution authoritative.
- Explicit priority, rationale, business impact, dependencies, next safe
  action, alternatives, trade-offs, confidence, evidence links, assumption
  links, and whether a Product Owner decision is required.
- Deterministic validation that every referenced source is active, belongs to
  the same project, and retains its fact/inference/assumption distinction.
- Evolution by attribution and supersession; a correction creates a new
  explainable recommendation state rather than silently editing history.
- A read-only Recommendation projection and executable behavioural scenarios
  through the public Factory boundary where applicable.

## Explicit exclusions

- Decision records, accepted decisions, and authority to make or approve a
  Product Owner decision (ORKI-004).
- Plans, sprint strategy, roadmap mutation, delivery or recovery planning
  (ORKI-005).
- Memory learning, initiative, governance authorisation, execution, new UI,
  chat streaming, or prompt-only behaviour.
- Legacy Factory Mission recommendations as a source of canonical Orki
  recommendation state.

## Principles

ORKI Principles 1-15 and 17-20 apply directly. Recommendations are preferred
to unnecessary questions, but they must disclose assumptions, alternatives,
trade-offs, evidence, confidence, and the boundary of Product Owner authority.
Conversation updates state; it never substitutes for recommendation evidence.

## Required acceptance scenarios

Every scenario uses the production Cognitive State and Recommendation Engine
path, is project-isolated, records inputs, explainability projection, and
PASS/FAIL outcome.

| Scenario | Required result |
| --- | --- |
| Evidence-based recommendation | A mission with attributable facts and inferences produces a prioritised recommendation linked to its active evidence. |
| Assumption disclosure | A safe default is linked as an assumption and is visibly distinct from the supporting facts. |
| Alternatives and trade-offs | At least two viable alternatives and their meaningful trade-offs are retained with the chosen recommendation. |
| Recommendation evolution | Correcting evidence or confidence supersedes the active recommendation while preserving history and provenance. |
| Insufficient or foreign evidence | Missing, stale, or another project's evidence is rejected; no recommendation is created. |
| No authority leakage | A recommendation may flag that a Product Owner decision is required, but creates no accepted decision, plan, governance action, or execution. |
| Explainability and isolation | The projection exposes rationale, confidence, sources, assumptions, alternatives, trade-offs, dependencies, and next safe action; another project cannot observe it. |
| Public-boundary behaviour | A structured Factory conversation records the same canonical recommendation and does not fall back to legacy mission recommendation or planning behaviour. |

## Recommendation Engine Release Gate

The Sprint passes only when all are PASS:

- Engineering and operational acceptance, complete repository regression, and
  scope-specific validation.
- Independent Recommendation Engine behavioural audit exercising the
  canonical service and public Factory boundary where available.
- All required scenarios above, including evidence provenance, evolution,
  isolation, no-authority-leakage, and explainability.
- COO Capability Acceptance: **Recommendation Quality PASS**; applicable
  foundation and Mission Understanding dimensions remain PASS. Decision,
  Planning, Memory, and later capability dimensions cannot be claimed.
- Updated architecture, ADR status, Product Owner scenarios, AKB, roadmap,
  self-critique, assessment, and final-state evidence.

## Completion boundary

Only an independently evidenced Recommendation Engine PASS permits ORKI-004
Decision Intelligence to begin. A fluent provider answer, isolated unit test,
or UI demonstration is insufficient.

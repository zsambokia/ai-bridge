---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Orki Initiative Maturity Model

**Status:** Canonical behavioural maturity contract.
**Authority:** Product Owner acceptance of ORKI-007, 2026-08-02.
**Current proven level:** Level 1 — Observation.

## Purpose

Initiative is not a feature that occasionally presents a suggestion. It is the
Digital COO's ability to notice, interpret and constructively advance an
operational situation before being asked. This model defines the behavioural
evidence required for that capability to mature.

A level is earned only by independently executed, retained evidence. Moving to
a higher level does not grant approval, governance, delivery, or execution
authority.

## Levels

| Level | Behaviour | Measurable acceptance | Present status |
| --- | --- | --- | --- |
| 1 — Observation | Orki independently detects a bounded project signal and makes it visible. | The observation is derived from Cognitive State rather than transcript; it has sources, rationale, confidence, priority, project isolation and a dismissible lifecycle. It is capped and has no authority. | **PASS** — ORKI-007 proves risk, opportunity and missing-evidence observations. |
| 2 — Recommendation | Orki converts a relevant observation into a safe, evidence-based operational recommendation. | It states the intended outcome, evidence, assumptions, expected impact, confidence, a safe next action and why inaction is less suitable. It must not ask a question when a safe default recommendation is possible. | Not yet implemented or scored. |
| 3 — Alternative proposal | Orki presents viable ways to resolve a material situation, not merely one preferred action. | Each alternative has dependencies, trade-offs, risks and operational consequences; the recommendation and the required Product Owner decision, if any, remain explicit. Scenario evidence must demonstrate that a changed constraint changes the proposed alternative. | Not yet implemented or scored. |
| 4 — Cross-project strategic initiative | Orki identifies a strategic opportunity or risk that spans authorized project portfolios and frames an accountable strategic proposal. | The proposal proves portfolio-level evidence, strategic impact, alternatives, trade-offs, governance boundary and explicit required decision. It must preserve project isolation: no raw project state, transcript or private knowledge crosses a boundary without explicit authorized policy. | Not yet implemented or scored. |

## DCMI rule

DCMI rises only when a level's behavioural acceptance scenarios pass with
evidence from the final state. Creating a new service, detector, UI element or
prompt does not itself change the score. Level 2 is the next eligible
Initiative improvement and may raise the Initiative dimension only after its
own independently passed Release Gate. Levels 3 and 4 can also affect Decision,
Planning, Business Thinking and Governance dimensions, but no score is assumed
in advance.

## Non-negotiable boundaries

- Conversation may update Cognitive State; it is never the input memory for
  initiative reasoning.
- Initiative is explainable, bounded, correctable and attributable.
- Product Owner business authority and governance execution authority remain
  outside the Initiative Engine.
- Cross-project insight requires an explicit authorized aggregation policy;
  project isolation remains the default.

## Next planning constraint

Any work toward Level 2 or beyond requires a separately bounded Sprint with
its own acceptance scenarios, Release Gate and evidence. ORKI-007 acceptance
proves only Level 1; it does not authorize implementation of later levels.

# ORKI-004 Decision Intelligence — Independent Release Gate

**Date:** 2026-08-02
**Authority:** Product Owner Factory Development Mode and autonomous-execution directive
**Branch / baseline:** `agent/issue-17-conversational-po` / `0f8153ad1e790f40662d5701247e6c5681ddaaa5`
**Result:** **PASS — READY FOR PRODUCT OWNER REVIEW**

## Purpose

Prove a platform-owned Decision Intelligence capability: a material,
evidence-backed recommendation becomes an explainable open decision, while an
accepted decision is possible only from explicit, attributable Product Owner
confirmation. This assessment evaluates behaviour, not only implementation.

## Independent behavioural evidence

| Capability | Evidence | Result |
| --- | --- | --- |
| Material decision boundary | A decision requires a same-project active recommendation marked as requiring a Product Owner decision, two or more options, recommendation, evidence, assumptions, alternatives, trade-offs, materiality, impacts, and a required question. | PASS |
| Explainability | The canonical projection exposes the question, options, recommendation, confidence, evidence, assumptions, alternatives, trade-offs, materiality, impacts, and lifecycle state. | PASS |
| Explicit acceptance authority | Provider output and raw conversation input can open a decision but cannot accept one. Acceptance requires `PRODUCT_OWNER_CONFIRMATION`, a `PRODUCT_OWNER` actor, actor identity, confirmation reference, a valid option, and the active open decision identifier. | PASS |
| Conflict and stale handling | An already accepted key cannot be reopened; a stale open-decision reference and an invalid option are rejected without destroying the inspectable prior state. | PASS |
| Project isolation | Reads and writes are scoped by project; a decision in Project A cannot be accepted from Project B. | PASS |
| Transcript separation | The public Factory scenario retains confidential input only in its transcript. Cognitive State uses source identifiers and hashes, not copied conversation text. | PASS |
| Governance boundary | Decision reasoning creates neither a Factory plan nor governance or execution authority. | PASS |
| Long-path operational behaviour | A public Factory conversation uses bounded Cognitive State and provider-originated decision observation to create an open decision, retaining trace and evidence while leaving acceptance under Product Owner authority. | PASS |

## Release Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| Engineering acceptance | PASS | `projects/decision_engine.py`, migration `0049_decision_intelligence_state.py`, focused engine and route tests. |
| Operational acceptance | PASS | Public Factory route behavioural scenario validates the authority boundary, trace, transcript separation, and absence of plan/governance side effects. |
| Backend regression | PASS | `manage.py test` — 71 tests passed in 62.475 seconds. |
| Browser E2E | PASS | `manage.py test projects.tests.test_factory_chat_browser_e2e` — 9 tests passed in 22.805 seconds. |
| Schema integrity | PASS | `manage.py makemigrations --check --dry-run` — no changes detected. |
| Django checks | PASS | `manage.py check` — no issues. |
| Static analysis | PASS | `python -m ruff check .` — all checks passed. |
| Architecture, ADR, documentation, AKB, roadmap | PASS | Sprint scope, ADR-002, Cognitive Data Flow, COS architecture, roadmap, AKB, and Factory record synchronized. |
| COO Capability Acceptance | FOUNDATION PASS | Decision Intelligence is independently proven; adjacent COO capabilities remain intentionally scoped to later Sprints. |
| Independent audit and self-critique | PASS | This assessment records capability-specific behavioural evidence and constraints rather than inferring capability from test count. |

## Self-critique

Decision Intelligence deliberately does not infer acceptance from affirmative
phrasing. It also does not create plans, alter the living Mission, approve
governance, or execute work. Those exclusions preserve authority boundaries;
they leave Planning Intelligence, Memory Intelligence, Initiative, and
Governance Integration as explicit subsequent capabilities rather than hidden
side effects.

## Continuation

All ORKI-004 Release Gates pass. Under the existing Product Owner autonomous
Factory Development Mode authority, ORKI-005 Planning Intelligence begins
without an approval wait.

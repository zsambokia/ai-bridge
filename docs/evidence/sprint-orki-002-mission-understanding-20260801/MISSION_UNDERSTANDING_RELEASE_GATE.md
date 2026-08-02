# ORKI-002 Mission Understanding Release Gate

**Date:** 2026-08-01
**Execution profile:** Product Owner Factory Development Mode
**Branch:** `agent/issue-17-conversational-po`
**Baseline:** `0f8153ad1e790f40662d5701247e6c5681ddaaa5`

## Scope

This gate validates only the ORKI-002 capability: creating and evolving a project-scoped, explainable **proposed** Mission State from a structured Product Owner observation. It does not validate recommendation, decision, initiative, planning, memory-intelligence, governance authorization, or execution.

## Independent behavioural evidence

The gate exercises the public Factory Chat HTTP boundary with a configured model provider double and verifies the persisted Cognitive State, rather than calling the Mission Understanding service directly.

| Capability | Evidence | Result |
| --- | --- | --- |
| Equivalent intent | Two differently worded Product Owner inputs produce the same canonical Mission State values. | PASS |
| Hidden business goal | `inferred_business_goal` is persisted as an `INFERENCE`, not copied as literal text. | PASS |
| Attribute separation | Stated intent and constraints are `FACT`s; solution proposal and technology preference remain separate `FACT`s; safe assumptions are `ASSUMPTION`s. | PASS |
| Safe assumptions | Assumptions have an explicit source, confidence and lifecycle. | PASS |
| Question budget | Exactly one question is recorded only with a material unknown, purpose and stated effect on the next step. | PASS |
| Confidence evolution | A 0.76 inferred goal is superseded by the evolved 0.91 conclusion; the active projection exposes the latter. | PASS |
| Conflict handling | Superseded entries remain auditable and are excluded from the active projection. | PASS |
| Conversation/state separation | Raw Product Owner text is hashed in allowlisted provenance only; it is absent from Cognitive State values and serialized provenance. | PASS |
| Project isolation | Three projects are exercised; their state entries and projections do not cross project boundaries. | PASS |
| No premature intelligence | The ORKI-002 structured path creates no `RECOMMENDATION` and invokes neither recommendation nor planning creation. | PASS |
| Explainability | Mission projection provides value, kind, confidence and approved provenance for each active attribute. | PASS |

## Commands and results

| Check | Result |
| --- | --- |
| `manage.py test projects.tests.test_orki_mission_understanding_release_gate` | PASS — 1 test |
| `manage.py test projects.tests.test_mission_understanding projects.tests.test_orki_mission_understanding_release_gate projects.tests.test_factory_chat_browser_e2e` | PASS — 15 tests |
| `manage.py makemigrations --check --dry-run` | PASS — no changes detected |
| `manage.py check` | PASS — no issues |
| Ruff on ORKI-002 changed Python files | PASS |
| `git diff --check` | PASS |

## Boundary and interpretation

The model-provider double deliberately makes the semantic observation deterministic. This is evidence that Orki's public integration, canonicalization, provenance policy, lifecycle, isolation and question policy behave correctly; it is **not** evidence that a particular external LLM vendor has universal semantic quality. Provider/model quality remains independently replaceable and must be assessed through provider qualification scenarios when such a provider is bound.

## Gate decision

**PASS — READY FOR PRODUCT OWNER REVIEW**

ORKI-002 independently proves the bounded Mission Understanding capability. Recommendation Intelligence remains out of scope until Product Owner review and the next approved capability Sprint.

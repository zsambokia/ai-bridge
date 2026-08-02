# CVO-001 — Independent Baseline Validation Report

**Date:** 2026-08-02
**Repository:** `zsambokia/ai-bridge`
**Branch / baseline:** `agent/issue-17-conversational-po` /
`0f8153ad1e790f40662d5701247e6c5681ddaaa5`
**Working tree:** pre-existing, unrelated modifications and untracked work were
present; no product-code mutation was made for CVO-001.

## Executive result

**ORKI-010 remains accepted for its engineering, operational and architecture
contract. The Digital COO behavioural claim does not pass this baseline.**

The 100 required scenarios are now specified, but no scenario has been
represented as executed. The current suite proves a well-formed operational
reasoning artefact can cross the Factory Chat boundary. It does not independently
prove that Orki derives a relevant mission, detects a simpler path, disagrees
when it should, economizes questions, or produces sound trade-offs in difficult
Product Owner conversations.

## Audit evidence

| Finding | Direct repository evidence | Consequence |
| --- | --- | --- |
| Completed reasoning is supplied by fixtures | `projects/tests/test_orki_recommendation_release_gate.py` patches `projects.factory_orki.model_adapter_for` and returns serialized, hand-authored reasoning. | Green test is boundary/contract evidence, not model reasoning evidence. |
| Reasoning validation is structural | `projects/operational_reasoning.py` validates required keys, state references, counts, bounded values and matching identifiers. | It cannot establish material relevance, truthful evidence use, trade-off quality, or a warranted disagreement. |
| Provider remains the reasoning producer | `projects/factory_orki.py` builds the provider prompt and invokes `model_adapter_for`; the persisted artefact is accepted after structural validation. | Current provider independence is schema/policy boundary, not demonstrated behaviour consistency across providers. |
| Raw recent messages reach provider context | `_bounded_context` includes the last 20 conversation items. | This is not evidence of persisted transcript memory, but it needs explicit trace/evaluation control so a hidden conversational influence cannot be mistaken for Cognitive State reasoning. |
| No semantic scenario scorer exists | Existing cited ORKI-010 tests use prepared artefacts, not a corpus that scores the observable criteria in CVO-001. | The required COO quality gate cannot pass yet. |

## Reproducible checks executed

| Command | Result | What it proves—and does not prove |
| --- | --- | --- |
| `PYTHON_DOTENV_DISABLED=true .\\.venv\\Scripts\\python.exe manage.py test projects.tests.test_operational_reasoning projects.tests.test_orki_recommendation_release_gate --verbosity 2` | PASS — 7 tests, 2.676s | Schema, state-reference, isolation, revision and Factory Chat boundary checks pass. The model call is mocked in the release-gate test; this is not semantic reasoning evidence. |
| Scenario-corpus identifier audit | PASS — 100 identifiers, 100 unique, CVO-001 through CVO-100 | Corpus completeness only. No Product Owner scenario was passed through a provider or independently assessed. |

The checks were executed with `PYTHON_DOTENV_DISABLED=true`; no external model
provider call was made and no credential value was read or displayed.

## Failure register

| ID | Failure | Affected dimensions | Required evidence before closure |
| --- | --- | --- | --- |
| F-001 | No governed 100-case behavioural execution exists. | All | Retained executions and independent rubrics for CVO-001 through CVO-100. |
| F-002 | Release fixtures inject the conclusion that is supposed to be assessed. | Reasoning, recommendation, explainability | Unscripted provider outputs plus state/trace assessment. |
| F-003 | No semantic validity/relevance assessment distinguishes plausible fields from COO-quality reasoning. | Mission, trade-offs, business, operations | Assessor protocol with evidence-grounding and counter-argument criteria. |
| F-004 | Question economy is a policy, not a measured challenge outcome. | Question economy, Product Owner experience | Per-scenario question-purpose and safe-default result. |
| F-005 | Simplification, duplication and strategic disagreement lack a demonstrated semantic detection path. | Initiative, simplification, architecture | Executed CVO-003/007/013/031/033/061/062 results. |
| F-006 | Provider-neutral behaviour has no comparative evidence. | LLM independence, consistency | Same-state repeat/provider comparison with semantic rubric. |
| F-007 | Recent transcript context can influence a provider response without being visible as a state-derived reasoning input. | Explainability, transcript boundary | Explicit input trace and adversarial transcript-isolation cases. |
| F-008 | The accepted DCMI score is historical; its high-level dimension values are not supportable as a current COO challenge score. | DCMI | Completed corpus results before any recalibration or increase. |

## Gate disposition and DCMI

The accepted historical **DCMI remains 66/100**. It is not reduced retroactively
by this audit, and it is **not increased**. CVO-001 issues no new DCMI score:
the user-required behavioural measurement has not yet been executed. Calling
66/100 a current proof of Digital COO behaviour would be misleading; it is a
historical, capability-level reference pending challenge validation.

The next score may change only after the execution protocol in the scenario
corpus is completed, failures are repaired in a separately bounded scope, and
the final results are independently retained. New UI, additional schemas,
prompts, or components count for zero by themselves.

## No-implementation attestation

CVO-001 makes documentation and evidence changes only. It introduces no
production code, migration, prompt change, provider call, model configuration,
or governance authority change.

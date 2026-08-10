---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Orki Digital COO Maturity Index (DCMI) Scorecard

**Status:** Historical scorecard with the CVO-002 evidence-weighted measurement transition.
**Baseline:** Executive Checkpoint B, 2026-08-02 (58/100).
**Historical measurement (DCMI v1):** Post-ORKI-007 Initiative Engine Release Gate, 2026-08-02 (66/100 across ten dimensions).
**Current measurement (DCMI v2):** Post-ORKI-008 Product Owner Cognitive Model Release Gate, 2026-08-02 (66/100 across eleven dimensions; Product Owner Understanding scores 7/10).
**Current validation discipline:** ORKI-010's bounded Operational Reasoning
release gate passed and was Product Owner accepted for engineering, operational
and architecture scope. The [CVO-001 Digital COO Validation baseline](../evidence/orki-digital-coo-validation-20260802/VALIDATION_REPORT.md)
finds that diverse final behavioural scenarios have not yet been independently
executed. DCMI therefore remains the accepted historical **66/100** reference;
no current Digital COO score or increase is claimed.
**Authority:** COO Capability Acceptance and Product Owner accepted DCMI reporting direction.

## Purpose

DCMI measures demonstrated Digital COO capability, not code volume, test
coverage, or a Sprint's implementation status. A bounded Sprint PASS proves
its contract; it does not automatically prove Epic-wide maturity. Every score
therefore has an executable measurement, retained evidence, and an explicit
limitation.

DCMI v2 normalizes the sum of eleven equally weighted dimensions (0-10 each)
to 100: `sum / 110 * 100`. The historical DCMI v1 score of 66/100 is retained
as the accepted ORKI-007 measurement. The v2 baseline was 60/100 because the
new Product Owner Understanding dimension initially added no points; ORKI-008
independent behavioural evidence raises that dimension to 7/10 and v2 to
66/100. This is a transparent capability measurement, not a score gained
through UI work. The former **85/100** condition is retained only as the
long-term Digital COO behavioural-maturity target. It is not a condition of
the completed ORKI-001-010 technical Epic closure: that closure records the
accepted implementation evidence while explicitly not claiming behavioural
certification. See the [technical Epic closure package](../evidence/orki-cognitive-operating-system-closure-20260802/PRODUCT_OWNER_REVIEW_PACKAGE.md).

## Initiative maturity and score discipline

The accepted Initiative capability is currently **Level 1 — Observation**.
The four-level behavioural path is canonical in
[Orki Initiative Maturity](ORKI_INITIATIVE_MATURITY.md): Observation,
Recommendation, Alternative proposal, and Cross-project strategic initiative.

No maturity label, implementation artefact, or planned Sprint changes DCMI by
itself. A score change requires independently executed behavioural scenarios
and final-state evidence. The present Initiative score of 8/10 reflects only
the accepted Level 1 proof; Levels 2–4 have no preallocated DCMI points.

## CVO-001 challenge-validity constraint

The 100-case [Digital COO Challenge corpus](../evidence/orki-digital-coo-validation-20260802/SCENARIO_CORPUS.md)
is now the required cross-capability measure. Until that corpus is executed
through a governed provider run and independently assessed, the values below
are retained historical capability measurements, not a claim that Orki behaves
as a mature Digital COO in open-ended Product Owner conversations. This
constraint prevents score inflation and prevents a schema-valid fixture from
being mistaken for demonstrated reasoning.

## CVO-002 evidence-weighted measurement transition

[CVO-002](../epics/CVO_002_DIGITAL_COO_IMPROVEMENT_LOOP.md) makes the next
DCMI adjudication evidence-weighted at scenario level. It does **not**
retroactively rewrite the accepted historical 66/100 score. Each future
capability claim must cite executed scenario output, a retained reasoning
trace, the applicable golden behavioural standard, and separate Business,
Architecture, and Operations judge records. The canonical evaluation and
aggregation rules are in the [COO Judge Protocol](../evidence/orki-digital-coo-validation-20260802/COO_JUDGE_PROTOCOL.md);
the comparison standard is the [Golden Scenario Corpus](../evidence/orki-digital-coo-validation-20260802/GOLDEN_SCENARIO_CORPUS.md).

No CVO-002 scenario has yet been executed. Consequently, no evidence-weighted
current DCMI is calculated or claimed here.

## Core DCMI matrix

| Capability | Current / 10 | Target / 10 | Objective measurement | Evidence and current limitation |
| --- | ---: | ---: | --- | --- |
| Mission Understanding | 9 | 10 | Equivalent mission state is produced for materially equivalent owner formulations; intent, solution preference, assumptions, and material unknowns remain separate. | [ORKI-002 assessment](../evidence/sprint-orki-002-mission-understanding-20260801/ASSESSMENT.md). PASS for its scenarios; full canonical scenario matrix remains pending. |
| Initiative | 8 | 9 | A normal Factory Chat turn can create an unprompted, project-scoped observation from structured state; the observation has deterministic priority, source, confidence, rationale, a dismissible lifecycle, no authority, and no more than five active items. | [ORKI-007 assessment](../evidence/sprint-orki-007-initiative-engine-20260802/ASSESSMENT.md). PASS for risk, opportunity and missing-evidence derivation; semantic inconsistency, duplication, reuse and simplification detectors remain future work. |
| Recommendation Quality | 9 | 10 | Recommendation carries evidence, assumptions, alternatives, trade-offs, confidence, impact, and a safe next action; it does not claim authority. | [ORKI-003 assessment](../evidence/sprint-orki-003-recommendation-engine-20260802/ASSESSMENT.md). ORKI-010 additionally requires reasoning before a Factory Chat recommendation, but no score change is claimed until diverse final scenarios are independently assessed. |
| Decision Intelligence | 8 | 9 | A material choice is separated from recommendation; options and impact are explainable; acceptance remains attributable only to the Product Owner. | [ORKI-004 assessment](../evidence/sprint-orki-004-decision-intelligence-20260802/ASSESSMENT.md). PASS; governance handoff is not yet proven. |
| Business Thinking | 7 | 9 | Scenarios show technical recommendations linked to business outcome, constraints, value, and impact rather than implementation detail alone. | ORKI-002 through ORKI-005 state and plan evidence. Partial: large-enterprise and ERP scenarios remain pending. |
| Planning Intelligence | 8 | 9 | Plan contains objective, business value, architecture, alternatives, chosen and rejected strategies, risks, dependencies, acceptance, release, operations, recovery, and evolution. | [ORKI-005 assessment](../evidence/sprint-orki-005-planning-intelligence-20260802/ASSESSMENT.md). PASS as a cognitive artefact; governed delivery integration is pending. |
| Memory Evolution | 8 | 9 | Knowledge is project-scoped, attributable, evidence-linked, correctable, and retrievable without using conversation transcript as memory. | [ORKI-006 assessment](../evidence/sprint-orki-006-memory-intelligence-20260802/ASSESSMENT.md). PASS; cross-project reuse remains intentionally out of scope. |
| Explainability | 9 | 10 | An observer can project the source state, evidence links, assumptions, alternatives, confidence, and reasoning trace for a capability outcome. | ORKI-001 to ORKI-006 release evidence and Cognitive State projections. Full end-to-end COO trace is pending. |
| Governance Discipline | 0 | 9 | Cognitive output is prepared for the existing governed lifecycle without granting approval, execution, or authority; prohibited shortcuts are tested. | Existing governance remains intact, but no cognitive-to-governance integration evidence exists. |
| Product Owner Experience | 0 | 9 | Blinded scenarios demonstrate guidance, safe defaults, useful initiative, and a justified question budget rather than wizard or questionnaire behaviour. | COO UX capability has not been independently tested. |
| Product Owner Understanding | 7 | 9 | After ten attributable interactions, the model exposes only evidence-linked operational collaboration patterns; the Product Owner can review, correct, and supersede them, and a later request receives the safe projection as bounded context for a reversible adaptive default. | [ORKI-008 assessment](../evidence/sprint-orki-008-product-owner-cognitive-model-20260802/ASSESSMENT.md) plus [ORKI-009 assessment](../evidence/sprint-orki-009-product-owner-model-evolution-20260802/ASSESSMENT.md). The latter proves weighted, explainable confidence and drift history, but DCMI remains 7/10 and 66/100 pending Product Owner acceptance and usefulness evidence. |
| **DCMI total (v2)** | **66 / 100** | **92 / 100** | `73 / 110 * 100`, rounded; DCMI v2 has eleven dimensions. | DCMI v1 remains 66/100 as the accepted ORKI-007 historical measurement. The v2 measurement rises from its recalibrated 60/100 baseline through independently proven Product Owner Understanding behaviour. |

## Supporting capability diagnostics

These metrics are mandatory leadership diagnostics but are not additional DCMI
dimensions. Product Owner Understanding is the sole new DCMI v2 dimension,
approved by the Product Owner strategic directive; future additions require
an explicit denominator and baseline decision.

| Supporting capability | Current / 100 | Target / 100 | Objective measurement | Evidence and limitation |
| --- | ---: | ---: | --- | --- |
| Cognitive State | 90 | 95 | Project isolation, transcript/state separation, evidence tracking, correction, confidence and explainable projection pass durable scenario tests. | [ORKI-001 release gate](../evidence/sprint-orki-001-cognitive-state-foundation-20260801/ASSESSMENT.md). Foundation PASS; broader scenario coverage is future work. |
| Question Budget | 70 | 90 | Each question has a material effect; safe defaults are preferred and unnecessary questioning is rejected in scenario tests. | ORKI-002 mission policy and acceptance evidence. Blinded UX measurement remains pending. |
| Operational Thinking | 55 | 90 | Plans and recommendations expose dependency, release, observability, risk, and recovery implications in operational scenarios. | ORKI-005 planning evidence. ORKI-010 adds a bounded reasoning-cycle measure; production incident, operational recovery, and multi-provider scenarios remain pending. |

## Reporting rules

- A score may increase only when the listed measurement is rerun against final
  state and the evidence reference is updated.
- A test count, implementation claim, or model response alone is not score
  evidence.
- In the CVO-002 method, a capability with no executed, independently judged
  scenario evidence is **NOT SCORED** for a new DCMI adjudication; it is never
  estimated upward. Historical values remain labelled historical.
- Every Executive Checkpoint links this scorecard, reports changes since the
  prior baseline, and names the next evidence needed to change a score.

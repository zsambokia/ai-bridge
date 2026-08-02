# CVO Failure Card Template

Create one immutable card for every **executed** scenario that fails any applicable judge criterion. Do not create a card by guessing what Orki would have said; CVO-001 systemic findings are recorded in `VALIDATION_REPORT.md`, not fabricated scenario cards.

## Identity and provenance

- Card ID / scenario ID / execution ID / rerun number
- State fixture, evidence IDs and Product Owner profile projection
- Provider, model/version, configuration revision and input-trace digest
- Timestamp, executor and the three judge records

## Expected COO behaviour

- Mission understood or material unknown explicitly bounded
- Required observable behaviours from the Golden Scenario Corpus
- Allowed safe default and the one question, if a question is justified

## Actual behaviour

- Verbatim retained response and reasoning projection references
- Judge scores, dissent and failed criteria
- Impact: misleading recommendation, missed risk, governance breach, unnecessary question, false certainty, missed simplification, or other

## Diagnosis

- Root cause, with evidence; distinguish state/evidence, reasoning policy, provider variance, evaluation defect and unknown cause
- Cognitive weakness and why the behaviour is not COO-quality
- Counterfactual: what a better reasoning sequence would have done

## Correction and proof

- Narrowly bounded required improvement and approving child Sprint
- Original scenario regression ID, declared adjacent regression cases and unchanged state-fixture rule
- Before/after judge results, remaining dissent and evidence references
- Resolution: `PASS`, `REOPENED`, or `NOT PROVEN`

No card may claim resolution merely because code changed or a response resembles the golden sample. The original scenario must be rerun and judged anew.

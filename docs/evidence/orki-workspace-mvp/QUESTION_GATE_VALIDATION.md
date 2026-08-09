# Orki Runtime question-gate validation

## Acceptance rule

The Runtime must not enter Planning while a mission has a critical unknown or
an open question. Planning requires a normalized mission confidence of at
least `0.90` and no remaining critical unknowns or open questions.

## Automated evidence

`projects/tests/test_factory_chat_runtime_integration.py` proves the rule with
these Runtime/API acceptance scenarios:

1. `test_e2e_underspecified_mission_waits_for_runtime_generated_questions`:
   a provider response that says the plan is ready is overridden; the execution
   reaches `WAITING_USER` and emits `gap_analysis.completed` and
   `questions.generated`.
2. `test_e2e_multiple_question_rounds_remain_waiting_for_user`: partial answers
   improve canonical mission confidence but preserve `WAITING_USER` and no
   plan until critical fields are complete.
3. `test_e2e_planning_starts_only_after_critical_unknowns_are_resolved`: the
   first response waits for the user; only the response containing every
   critical mission field transitions to `WAITING_APPROVAL` with a plan.

## Commands and results

- `python -m pytest projects/tests/test_factory_chat_runtime_integration.py projects/tests/test_factory_chat.py -q` — 40 passed.
- `python -m pytest projects/tests/test_factory_chat_browser_e2e.py -q` — 15 passed.
- `python -m pytest -q` — 380 passed.

The browser proof covers the conversation controls and the chat-first
projection; the Runtime integration proof is the authoritative state-transition
evidence for the question gate.

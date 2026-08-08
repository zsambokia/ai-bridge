# Runtime state-transition evidence

Scope: `bridge:ai-bridge:sprint:712aef15-2426-4f57-88b6-8b1389807b3e`
Proposal hash: `1e54604709d93af8c5be513779a7679a8503d6cc19fe6162564fc3b7827fbe6f`

The transition guard is the `_TRANSITIONS` map in `projects/orki_runtime.py`.
Every guarded transition increments `state_version`, persists the current waiting
reason, and appends an `OrkiRuntimeEvent` containing the source and target state.

| Scenario | Observed persisted result |
| --- | --- |
| Factory Chat creates a pending Factory Plan | `CREATED -> PLANNING -> WAITING_APPROVAL`; creation, plan selection and both transitions are audit events |
| Existing approval is accepted | `WAITING_APPROVAL -> WAITING_GOVERNANCE`; `APPROVAL_OBSERVED` and `SHADOW_GOVERNANCE_HANDOFF_RECORDED` are emitted |
| Owner pauses and resumes | prior state is retained in `paused_from_state`; `PAUSED` and `RESUMED` are append-only events |
| External wait is recovered | `WAITING_EXTERNAL -> PLANNING` with `RECOVERY_REQUESTED` and `RECOVERY_REASSESSMENT_STARTED` |

Validation: `projects.tests.test_orki_runtime` exercises all four scenarios and
passed in the focused suite on 2026-08-07.

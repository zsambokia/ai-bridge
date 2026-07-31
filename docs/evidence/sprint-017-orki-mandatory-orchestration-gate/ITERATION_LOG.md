# Sprint 2 iteration log

This log preserves repair iterations rather than presenting only the final
green state.

| Iteration | Detection | Repair | Verification |
| --- | --- | --- | --- |
| 1 | Initial ambiguity test used a non-existent assessment risk field. | The test was corrected to assert the persisted decision/policy outcome that is the canonical ambiguity record. | Targeted Orki suite passed. |
| 2 | Provider-trace assertion found that the public confirmation projection omitted the runtime profile. | The Orki trace projection was extended with the persisted runtime-profile hash. | Targeted MCP and Orki suites passed. |
| 3 | Ruff reported an overlong assertion after the ambiguity enhancement. | The assertion was split without changing behaviour. | Ruff was rerun successfully. |
| 4 | A real isolated worker reached `EXECUTOR_START_FAILED` although the locally authenticated Codex CLI was usable: provider health incorrectly required an `OPENAI_API_KEY`. | Codex CLI readiness now accepts the authenticated executable path; a provider-start failure is durably requeued with a bounded retry rather than terminalized. | Focused provider and execution tests passed; the real run was requeued, reprovisioned, dispatched, and completed. |
| 5 | A recovered run collided with a different active run on the same protected branch, leaving a leased job in the prior implementation. | A branch-conflicted claimed job is released to `RECOVERING`, delayed, and recorded as `EXECUTION_BRANCH_CONFLICT_DEFERRED`. | Focused execution test and a live worker run passed; after controlled cancellation of the competing run, the original recovery completed. |
| 6 | The first final Release Gate rerun found a MyPy nullable-return error in the new provider-recovery test assertion. | The test now narrows the return value before reading its primary key. | The complete final gate sequence passed: Ruff, MyPy, Django, migration, scope validation, and 209 tests. |

Operational iterations and their exact runtime observations are recorded in
`OPERATIONAL_ACCEPTANCE.md`; no failed runtime attempt is omitted.

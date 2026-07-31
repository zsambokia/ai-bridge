# Sprint 2 iteration log

This log preserves repair iterations rather than presenting only the final
green state.

| Iteration | Detection | Repair | Verification |
| --- | --- | --- | --- |
| 1 | Initial ambiguity test used a non-existent assessment risk field. | The test was corrected to assert the persisted decision/policy outcome that is the canonical ambiguity record. | Targeted Orki suite passed. |
| 2 | Provider-trace assertion found that the public confirmation projection omitted the runtime profile. | The Orki trace projection was extended with the persisted runtime-profile hash. | Targeted MCP and Orki suites passed. |
| 3 | Ruff reported an overlong assertion after the ambiguity enhancement. | The assertion was split without changing behaviour. | Ruff was rerun successfully. |

Operational iterations and their exact runtime observations are recorded in
`OPERATIONAL_ACCEPTANCE.md`; no failed runtime attempt is omitted.

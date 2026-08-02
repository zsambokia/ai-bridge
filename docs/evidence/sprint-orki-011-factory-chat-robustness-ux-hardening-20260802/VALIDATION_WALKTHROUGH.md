# ORKI-011 Completion Validation Walkthrough

This walkthrough validates the end-to-end Product Owner path against the final
repository state. It is deliberately a usability and lifecycle validation, not
a CVO reasoning-quality judgement.

| Product Owner step | Expected workspace behaviour | Executable evidence | Result |
| --- | --- | --- | --- |
| Start from an idea | Natural language is accepted in the primary conversation surface. | Factory Chat conversation and keyboard Chromium cases | PASS |
| Continue a long conversation | History remains scrollable; composer remains reachable; retry does not duplicate state. | Long-chat, idempotency and retry cases | PASS |
| Inspect current state | Mission, facts, assumptions, open decisions, recommendation, plan, roadmap and next step are visibly projected from canonical state. | Workspace rendering backend cases and status refresh path | PASS |
| Request a plan | Existing plan lifecycle creates the proposed plan, roadmap and memory artifacts. | Planning-artifact backend cases | PASS |
| Review the plan | Decision card presents summary, assumptions, alternatives, impact, recommendation and explicit decision. | Pending-plan rendering case | PASS |
| Approve safely | Approval updates plan/document state and ends at execution preparation. | `test_plan_approval_stops_at_execution_preparation` | PASS |
| Recover from a failure | Safe recovery message appears; raw HTML is hidden; draft and retry remain usable. | Safe error, failed-response and raw-HTML Chromium cases | PASS |
| Work on narrow screens | Chat remains primary and supplementary panels remain reachable on tablet/mobile. | Chromium viewport cases | PASS |

The complete final scope suite is recorded in [Release Gate](RELEASE_GATE.md):
46 passing tests in 55.752 seconds, plus Django, canonical-scope and diff
checks. The complete repository regression passed: 329 tests, executed in
four deterministic groups (125 + 61 + 97 + 46). Direct in-app browser control
was unavailable, so responsive browser evidence is provided by the passing
repository Chromium suite rather than a manual browser-control claim.

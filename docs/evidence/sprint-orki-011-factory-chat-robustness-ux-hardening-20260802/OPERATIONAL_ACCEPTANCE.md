# ORKI-011 Operational Acceptance — Factory Chat Completion

**Result:** PASS — READY FOR PRODUCT OWNER REVIEW

| Scenario | Expected operational behaviour | Evidence | Result |
| --- | --- | --- | --- |
| Natural conversation | The Product Owner starts with an idea, not a multi-page interview; Orki updates canonical project state. | Factory Chat backend and Chromium conversation cases | PASS |
| Live Cognitive State | Mission, facts, assumptions, open decisions, recommendation, plan, roadmap and next step refresh without page reload. | Workspace template, projection tests and status-refresh browser path | PASS |
| Plan review | A pending plan has an inspectable summary, assumptions, alternatives, impact, recommendation and explicit approval/change/reject choices. | Pending-plan and approval-boundary backend cases | PASS |
| Approval boundary | Approval creates document and execution-preparation state only; it cannot start repository work or execution. | `test_plan_approval_stops_at_execution_preparation` | PASS |
| Document lifecycle | Existing mission, plan and roadmap artifacts are projected from canonical state without a manual sync step. | Planning-artifact backend cases and workspace projection | PASS |
| Provider/unexpected failure | A short safe recovery message, no secret or stack trace, usable retry. | Enhanced server exception and Chromium raw-HTML tests | PASS |
| Retry/reload duplicate | Same request identifier reuses the persisted result. | Server idempotency regression | PASS |
| Refresh before send | Draft returns after refresh. | Chromium refresh scenario | PASS |
| Long conversation | Conversation scrolls independently and composer remains available. | Chromium long-chat scenario | PASS |
| Desktop/tablet/mobile | Conversation stays primary while supporting panels stay reachable. | Chromium viewport scenarios | PASS |

Direct in-app browser control was unavailable in this environment (`Browser is
not available: iab`). This is an environment limitation, not a waived gate: the
repository's Chromium Playwright suite executed the browser evidence above.

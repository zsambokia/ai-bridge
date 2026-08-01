# Issue #17 — Sprint 6: Factory Chat end-to-end acceptance

## Authority and boundary

- Authority: Product Owner Factory Development Mode for `zsambokia/ai-bridge`, with the Issue #17 Sprint 1 interaction contract explicitly accepted on 2026-08-01.
- Branch and baseline before mutation: `main` at `715d39d3506375f7105fe68881e1429e19f38afa`.
- Scope: bounded browser-level integration acceptance of the delivered Issue #17 Factory Chat surface and its canonical plan, approval, execution, Orki-context, Memory, repository-delivery, and runtime projections.

## Acceptance mission

The test mission creates an authenticated project-local plan in a real Chromium desktop session; searches approved AKB Memory; binds the resulting context package to a completed Orki session; creates the canonical consumed execution contract and completed run; and verifies the Coding projection. A second real Chromium page checks the mobile Chat projection.

It deliberately does not dispatch a provider from the browser, invent a second execution lifecycle, deploy infrastructure, or claim a public production deployment. Delivery and runtime verification reuse the existing canonical runtime-deployment and HTTP-MCP-to-contract tests.

## Deliverables and evidence

- Real browser E2E: `projects/tests/test_factory_chat_browser_e2e.py`.
- Desktop and mobile viewport assertions: the same real Chromium test.
- Orki, plan/approval, coding/execution, and Memory integration: durable canonical records exercised by that mission.
- Repository delivery and runtime/deployment verification: `projects/tests/test_remote_mcp.py::test_storybook_request_flows_from_http_mcp_to_orchestrated_contract` and `projects/tests/test_runtime_deployment.py`.
- Final results and independent audit: `docs/evidence/issue-017-sprint-6-factory-chat-end-to-end-acceptance/`.

# Sprint 8 final acceptance-scenario audit

## Required scenario

The canonical Sprint 8 scenario requires:

1. one external-project change and one AI Bridge self-development change through the canonical managed path; and
2. a new ChatGPT Business session that retrieves the resulting status and evidence.

## Result: not executed — external certification prerequisite unavailable

The second step is intentionally not substituted with a Bearer-token HTTP request, a fixture, a seeded projection, or an API/MCP direct call. Those prove bounded AI Bridge behavior but cannot prove a ChatGPT Business UI-originated request, Product Owner UI approval, Remote MCP transport, and later UI retrieval.

Sprint 6 preserves the same boundary at `BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE`. The Product Owner moved this external proof to the separate **ChatGPT Business Platform Certification** Epic and instructed that Sprint 6 evidence must remain unchanged.

## Evidence required before a full Epic verdict

- a genuine ChatGPT Business UI request and Product Owner approval;
- attributable Remote MCP invocation;
- canonical Orki session, decision, contract, run, provider, repository-delivery, and deployment receipts;
- a fresh UI session retrieving status/evidence; and
- binding of runtime revision and delivered SHA without credentials.

Accordingly, this audit does not claim Operational Acceptance for the complete factory chain and does not mark Sprint 8 or the Epic PASS.

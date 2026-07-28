# Assessment — Recover Interrupted Approval Sessions

- Contract: `bridge:ai-bridge:contract:46ee9349-ba76-4ed9-b053-132fd8e7ffb7`
- Approved scope: `docs/sprints/e626a32e-b18a-415e-bfe2-5d2baf8bf1b2-recover-interrupted-approval-sessions.md`
- Baseline: `605ef46eb71cbc16147b946dbf8ddad2372712ae` on `main`

## Findings

The canonical durable records already existed: `GovernanceApproval` for
approval authority and `ConversationOrchestration` for the conversational
execution lifecycle. The public governed MCP registry already provided
`conversation.confirm`, `scope.confirm_and_execute`, idempotency, audit events,
and orchestration advancement. The implementation extends that canonical path
with `scope.resume` and `scope.resume_confirm_and_execute`; it does not create
a new model, approval store, contract lifecycle, or execution dispatcher.

The recovery confirmation derives a caller-bound reference and idempotency key
server-side, locks the canonical scope, compares the supplied proposal version
and hash before lifecycle work, and reuses an existing orchestration where one
exists. The focused tests cover recovery from a new session, replay
idempotency, preservation of the single approval, audit recording, and a stale
hash rejection.

## Scope boundary

In scope: governed MCP recovery discovery/confirmation, tests, architecture,
AKB, roadmap, and this sprint evidence. Out of scope: a new approval system,
changes to ordinary same-session confirmation, provider selection, production
deployment, or credential handling.

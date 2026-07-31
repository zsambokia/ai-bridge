# Sprint 6 Remote MCP conversation-binding remediation

## Scope and retained failed observation

This is a repair within the approved Sprint 6 scope, not a new scope and not a
manual replay of a prior approval. The retained failed observation is scope
`bridge:ai-bridge:sprint:3b317dc6-a7a0-471d-b939-9409b8486ff2`, proposal
version `1`, proposal hash
`f0110629c7d5d67c8b66a6e08bbe1ceeb8ad9c6f885f4b71efff814b6813a658`, with
the text `Igen, jóváhagyom.`. It returned
`PRODUCT_OWNER_CONFIRMATION_REQUIRED` before an approval, contract, execution,
provider run, delivery, or runtime revision existed. That scope remains
unchanged as historical evidence.

## Root cause

The normalized Hungarian affirmative (`igen jovahagyom`) was not in the
explicit confirmation allow-list, causing a generic rejection. More
fundamentally, the Remote MCP adapter passed only a static bearer-derived
caller fingerprint. It had no durable, server-issued conversation/session
value connecting `scope.review` to `conversation.confirm`; therefore the
service could not safely derive a pending proposal solely from an affirmative
reply.

The prior staging health revision `30648dc0625fef7e6451b0b7ace9bc6422a5c96d`
is phrase-repair history only. It is not evidence that this remediation is
loaded by the public MCP process, worker, or scheduler.

## Repair

1. Add the normalized Hungarian affirmative to the strict allow-list.
2. Issue an opaque Django-signed MCP session at `initialize`, bound to the
   authenticated caller and validated with a bounded expiry.
3. Persist `McpConversationBinding` during Remote MCP `scope.review` with the
   canonical scope, exact proposal version/hash, caller fingerprint, and
   server-issued session.
4. Let Remote `conversation.confirm` accept only confirmation text and derive
   scope, exact proposal, approval reference, and retry key from that binding.
5. Require the server-owned Product Owner caller fingerprint allow-list; tool
   arguments cannot assert identity, conversation, proposal hash, or approval
   reference.
6. Persist caller/session onto `ConversationOrchestration` and mark the matched
   binding confirmed in the canonical locked approval path.

## Safe diagnostics

The public boundary does not reveal identifiers or secrets. Audit and tool
errors now distinguish `CONFIRMATION_TEXT_REJECTED`,
`CALLER_IDENTITY_MISSING`, `CONVERSATION_CONTEXT_MISSING`,
`CONVERSATION_BINDING_MISMATCH`, `PRODUCT_OWNER_AUTHORITY_MISSING`,
`PENDING_PROPOSAL_NOT_FOUND`, and `PROPOSAL_BINDING_MISMATCH`.

## Engineering evidence

The final local gate run for this remediation passed:

| Gate | Result |
| --- | --- |
| Ruff (`bridge`, `projects`) | PASS |
| MyPy (`bridge`, `projects`) | PASS — 126 source files |
| Django check | PASS |
| Migration check / plan | PASS — new `projects.0040` planned |
| Pytest | PASS — 237 tests |
| `git diff --check` | PASS |

Regression coverage includes same-session remote review/confirmation,
different-session mismatch, missing session/caller diagnostics, untrusted
caller rejection, exact version/hash binding, stale binding rejection, and
idempotent canonical orchestration/contract/run behavior. Existing governed
scope tests retain project and lifecycle isolation coverage.

## Operational boundary and next run

The in-app ChatGPT Business browser is unavailable in this execution
environment. No static bearer HTTP request is presented as final E2E proof.
Before a new UI proposal is made, deploy the committed source revision, apply
`projects.0040`, configure the Product Owner fingerprint allow-list without
recording the token/fingerprint in evidence, and independently record the
loaded revision of health, MCP process, worker, and scheduler. Then use a
fresh ChatGPT Business conversation to propose, review, affirm in the UI, and
verify the resulting approval, contract, run, provider, delivery, deployment,
retrieval, and feedback chain. Failed attempts and this retained observation
remain part of the Sprint 6 evidence trail.

**Status:** Engineering remediation PASS; Operational Acceptance not yet
demonstrated.

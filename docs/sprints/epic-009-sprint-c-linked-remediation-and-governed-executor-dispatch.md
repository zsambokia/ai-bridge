# Sprint C — Linked Remediation and Governed Executor Dispatch

Status: IMPLEMENTED

Link policy-allowed technical remediation to canonical work items and Execution Contracts. Dispatch only through the existing governed executor boundary with idempotency, cancellation, timeout, audit linkage, and no new approval bypass.

`projects.remediation` creates a durable remediation only from an `ALLOW`
ownership assessment, then links (but never generates) an existing published
scope and consumed hash-bound Execution Contract. Dispatch, cancellation, and
deadline cancellation re-verify the scope-bound `AUTHORIZE_EXECUTION` approval
and call the existing executor boundary. No LLM provider or SDK is referenced.

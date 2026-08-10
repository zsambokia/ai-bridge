---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# SHA-bound runtime deployment and operational acceptance

Sprint 5 separates repository delivery from runtime activation. A verified
`ExecutionDelivery` proves a commit reached its intended repository ref;
`RuntimeDeployment` is the one-to-one post-delivery receipt for runtime activation.

## Invariants

1. Only a `VERIFIED` delivery can be planned for activation.
2. Local final and independently read-back remote SHAs must match.
3. A plan records target identity, authority, artifact SHA and rollback target.
4. Every verification result is retained; a failure is appended to history.
5. Operational Acceptance passes only if runtime and artifact SHA match and all checks pass.
6. Admin and MCP share one read-only `RuntimeDeployment` projection.

## Runtime proof

Targets set `AI_BRIDGE_BUILD_SHA` from the immutable artifact. `/health/`
returns it unchanged and never infers a SHA from a mutable checkout.
`verify_runtime_deployment` checks public health/build SHA, migration planning,
dependency integrity, a worker tick and a scheduler tick. The scheduler
composes existing reconciliation and workspace cleanup services. Verification
does not itself claim a deployment or change a deployment receipt.

## Rollback and remediation

Rollback requires an explicit passing receipt. A mismatched SHA or failed check
is retained as a failed attempt; a repaired target records a new attempt.

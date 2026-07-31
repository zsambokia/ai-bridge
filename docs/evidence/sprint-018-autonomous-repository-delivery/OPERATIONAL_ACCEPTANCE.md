# Sprint 4 Operational Acceptance

Date: 2026-07-31.  The isolated runtime database is `.sprint4-operational-runtime/runtime.sqlite3` and is intentionally excluded from Git.

## Live projection proof

An authenticated HTTP MCP `initialize`, `contract.get_status`, and `execution.get_run_status` request completed against `127.0.0.1:8774`.  The persisted run `SPRINT4-RUNTIME-DELIVERY-001` projected `RUNNING / DELIVERY_VERIFICATION` and one canonical delivery record: `VERIFIED`, `refs/heads/main`, `force_push_allowed=false`, verifier `delivery-verifier`, and matching final/remote 40-character SHA values.  The Django Admin rendered that same `VERIFIED` record and SHA from the same isolated database.

## Delivery-chain proof

The automated operational-like integration tests create a real local Git repository and bare `origin`, start a canonical run, make and commit a scoped repository change, run the delivery verifier, perform normal `git push`, re-read the remote SHA, and complete the governed run only after verification.  They also inject dirty workspace, remote movement, unrelated change, force-push policy, evidence-SHA mismatch, and provider self-approval faults.

The live projection record is a deliberately seeded observability fixture; it is not represented as a provider-authored code change.  The actual provider executable was checked and is authenticated, while provider execution remains independently covered by the existing worker/provider lifecycle tests.  This separation prevents a synthetic Admin/MCP probe from overstating delivery evidence.

Result: **PASS**, with the above limitation explicitly retained for Product Owner review.

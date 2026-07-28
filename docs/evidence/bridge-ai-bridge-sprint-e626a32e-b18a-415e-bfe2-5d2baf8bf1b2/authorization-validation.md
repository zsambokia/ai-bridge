# Authorization validation

- `scope.resume` exposes no approval token, raw identity, or contract secret.
- `scope.resume_confirm_and_execute` accepts only a positive confirmation and
  derives the authenticated caller fingerprint, approval reference, and
  idempotency key in the Bridge service.
- The supplied proposal version and SHA-256 hash must equal the canonical scope
  values under a database lock. A stale hash produces `SCOPE_HASH_MISMATCH`.
- Existing `GovernanceApproval` and `ConversationOrchestration` records are
  reused. Replays do not mint a second approval, contract, or run.
- Recovery lookup and approval replay are recorded as safe MCP audit events;
  no secret token is placed in the audit payload.

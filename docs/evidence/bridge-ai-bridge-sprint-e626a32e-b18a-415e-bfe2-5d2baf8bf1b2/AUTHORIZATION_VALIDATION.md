# Authorization Validation

Recovery remains authenticated at the public MCP boundary. The new
`scope.resume_confirm_and_execute` schema requires an affirmative confirmation,
scope identifier, and exact proposal version/hash. The service derives the
Product Owner identity, confirmation reference, and idempotency key from the
authenticated caller; client input cannot supply those authority values.

Before reuse or creation of a lifecycle record, it locks the canonical scope
and rejects version/hash mismatches. Existing `GovernanceApproval` and
`ConversationOrchestration` records are reused rather than duplicated.
`scope.resume` exposes no approval secret. Both recovery lookup and recovery
confirmation write audit events.

Evidence: `pytest projects/tests/test_governed_mcp.py -q` passed 22 tests,
including new-session recovery, replay, stale-hash rejection, audit, and
single-approval assertions.

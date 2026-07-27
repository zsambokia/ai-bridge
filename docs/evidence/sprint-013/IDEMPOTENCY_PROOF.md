# Idempotency proof

Repeating the same natural-language `conversation.confirm` call returned
`idempotent_replay: true` with the same orchestration token, contract handoff,
and execution token. Database inspection confirmed exactly one
`GovernanceApproval`, one `ConversationOrchestration`, and one `ExecutionRun`
for the proof scope. No duplicate provider execution was created.

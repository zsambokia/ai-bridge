# Conversational Product Owner model

`scope.review` persists a proposal version and SHA-256 proposal hash. Material
clarifications create a revised review state. `conversation.confirm` accepts a
bounded natural-language affirmative response only while it is bound to the
current proposal version and exact hash; it then advances approval, publication,
preparation, contract generation, validation, issuance, consumption and provider
start through normal governed operations. The durable coordinator is
`ConversationOrchestration` and is visible read-only in Django admin.

The Sprint 011 bootstrap approval `PO-BOOTSTRAP-SPRINT-011-2026-07-26` is an
external one-time authorization for the Sprint scope only. It is not an alternate
Work Item approval path and is retired after Sprint closure.

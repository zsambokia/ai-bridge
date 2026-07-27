# Idempotency and retry proof

Provider resolution occurs after the canonical one-time contract consumption receipt. Existing active-run locking prevents concurrent branch execution, and existing `McpIdempotencyRecord` continues to protect public lifecycle calls. The provider registry adds no parallel retry or fallback lifecycle.

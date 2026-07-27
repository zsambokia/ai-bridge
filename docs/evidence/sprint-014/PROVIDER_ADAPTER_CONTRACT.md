# Provider adapter contract

Role-specific protocols separate execution (`start`, `status`, `cancel`), model inference, repository reads, and data reads. The Codex adapter preserves the prior command behavior. OpenAI and Claude implement bounded model requests; GitHub implements branch-state reads; BigQuery accepts only `SELECT`/`WITH` reads. These non-execution adapters are not selected by the execution dispatcher.

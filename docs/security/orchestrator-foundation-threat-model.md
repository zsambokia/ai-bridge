# Orchestrator foundation threat model

Threats addressed in Sprint A: prompt injection and overbroad context (bounded normalized context), provider hallucination (strict schema/evidence validation), privilege escalation (independent deterministic policy), repeated delivery (idempotency key), and secret leakage (credentials are runtime-only and excluded from persistence).

This Sprint intentionally denies production, security, privacy, irreversible, and cross-project recommendations. Provider outage, malformed JSON, missing SDK, and missing credentials fail closed into a durable failed session. Retry, circuit breaking, incident ingestion, and deployment controls are scheduled in later Sprints.

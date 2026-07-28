# Operating the orchestrator foundation

Configure `OPENAI_API_KEY` only in the runtime secret store, never in project records, sessions, decisions, evidence, or logs. `AI_BRIDGE_ORCHESTRATOR_MODEL` optionally selects the OpenAI model and defaults to `gpt-5-mini`.

`orchestrator.assess` requires a registered Project, a bounded summary, and an idempotency key. Reusing the same key returns the original durable session. `orchestrator.get_status` reads the decision; `orchestrator.cancel` can cancel only a pending session. Provider faults and malformed responses leave a durable `FAILED` session and do not create a decision or execute work.

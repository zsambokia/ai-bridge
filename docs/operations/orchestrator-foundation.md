# Operating the orchestrator foundation

Configure an enabled, active `ExecutionProvider` with the `MODEL_INFERENCE` capability through the existing provider registry. Set `AI_BRIDGE_ORCHESTRATOR_PROVIDER` to that registered provider identity (default: `openai`). Credentials and model configuration remain on the provider platform; `orchestrator.assess` does not create a separate OpenAI client.

`orchestrator.assess` requires a registered Project, a bounded summary, and an idempotency key. Reusing the same key returns the original durable session. `orchestrator.get_status` reads the decision; `orchestrator.cancel` can cancel only a pending session. Provider faults and malformed responses leave a durable `FAILED` session and do not create a decision or execute work.

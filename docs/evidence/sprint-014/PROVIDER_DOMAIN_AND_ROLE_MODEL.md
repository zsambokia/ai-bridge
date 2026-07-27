# Provider domain and role model

`ExecutionProvider` is the sole persistent provider registry. Stable `provider_id`, kind, role, status, adapter key, priority, non-secret configuration, credential reference, capabilities, and health metadata are recorded. `ProviderAuditEvent` is append-only.

| Provider | Role | Initial status | Proven capabilities |
| --- | --- | --- | --- |
| codex-cli | EXECUTION_AGENT | ACTIVE | CODE_EXECUTION, CANCELLATION, STATUS_POLLING, HEALTH_CHECK |
| openai | MODEL_API | DRAFT | MODEL_INFERENCE, USAGE_REPORTING, HEALTH_CHECK |
| claude | MODEL_API | DRAFT | MODEL_INFERENCE, USAGE_REPORTING, HEALTH_CHECK |
| github | REPOSITORY_SERVICE | DRAFT | REPOSITORY_READ, REPOSITORY_WRITE, BRANCH_MANAGEMENT, PULL_REQUEST_MANAGEMENT, HEALTH_CHECK |
| bigquery | DATA_SERVICE | DRAFT | DATA_QUERY_READ, DATA_QUERY_WRITE, HEALTH_CHECK |

Only Codex is active. Draft entries are not dispatchable and do not claim a remote proof.

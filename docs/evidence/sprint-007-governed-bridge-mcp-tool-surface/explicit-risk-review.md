# Explicit risk review

State-changing tools are classified separately from authentication, require a durable approval reference where required, are auditable, and use idempotency keys. Contract transitions still flow through the canonical lifecycle service. `execution.request_start` stores a request and never pretends to launch execution.

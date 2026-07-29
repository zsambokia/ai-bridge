# Orchestrator foundation

The orchestrator is a decision-support and lifecycle layer, not an executor. Providers implement a small `assess(context, correlation_id)` protocol. Every model call is composed outside the domain through the existing `ExecutionProvider` registry and provider-platform adapter. OpenAI is the first registered implementation, not a second SDK integration; provider choice is stored with each durable session.

Provider-specific request and response handling stays in `projects.providers`. The Orchestrator domain has no OpenAI SDK dependency, so a new provider implementation can be added without rewriting the domain.

The request context is normalized and bounded: project identity, repository name, summary, permitted recommendation vocabulary, and prohibitions. It excludes source checkout contents, logs, credentials, arbitrary tool output, and executable instructions.

Responses are accepted only when they use schema `1.0`, match the session token, cite evidence for every material fact and root-cause candidate, and identify a repository, component, cause, and bounded confidence. `evaluate_policy` then independently fails closed. `ALLOW` means only that later governed workflow may consider technical work; it never dispatches work.

## Issue #11 Sprint C: technical remediation loop

An execution blocked by an in-scope technical fault can create one durable,
scope-linked remediation Work Item without starting another provider run or
consuming another contract. The loop classifies blockers explicitly; only
`TECHNICAL_REMEDIATION` may proceed automatically. Business decisions,
security or governance conflicts, external dependencies, and non-recoverable
faults remain escalations. A bounded repair records its policy basis, evidence,
child scope, and audit events; it resumes the same parent only after the failed
gate is rerun successfully. Repeated requests are idempotent and a corrupted
published scope projection is restored from its unchanged canonical record.

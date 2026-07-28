# Sprint A — Authority Framework and Orchestrator Provider Foundation

Status: IMPLEMENTED — pending Product Owner review

## Objective

Establish the provider-neutral, LLM-assisted engineering-assessment boundary. An LLM response is untrusted input and never itself authorizes a mutation, execution dispatch, deployment, or approval.

## Scope and acceptance

- Persist idempotent orchestration sessions and validated decisions.
- Enforce schema `1.0`, evidence references, bounded root-cause candidates, enum validation, and correlation identifiers.
- Classify `ENGINEERING`, `BUSINESS`, `MIXED`, `UNSAFE`, and `UNKNOWN`; the deterministic policy is the sole authority decision.
- Provide an OpenAI-first adapter behind a neutral provider protocol and a test-only fake provider.
- Provide bounded MCP assessment/status/cancellation operations and read-only Django admin visibility.
- Do not implement incident ownership, remediation dispatch, validation continuation, or deployment. Those belong to Sprints B–E.

## Explicit non-goals and constraints

No model output can execute shell commands, access repository contents or secrets, approve scope, create a contract, or bypass the existing scope/contract lifecycle. Production, security, privacy, irreversible, and cross-project recommendations are denied by this foundation.

## Evidence plan

Run Django migration/check, project tests, Ruff, MyPy, and scope validation. Record final commands and results in the Sprint A evidence report.

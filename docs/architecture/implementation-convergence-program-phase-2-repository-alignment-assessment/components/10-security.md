# Security Assessment

## Target Architecture

Security is scope-aware. Secrets must not appear in Context Packages, Kernel Events, telemetry, or evidence; provider use and authorization are auditable and bounded by scope.

## Current Repository

Django CSRF middleware and authenticated UI routes are configured; `runtime_api.py` and Factory Chat use `login_required`. MCP token configuration is environment-driven. Execution and provider records retain audit information; execution event code contains explicit secret-conscious handling.

## Gap Analysis

**Partial:** baseline web authentication, CSRF, configuration secrecy, audit records, and some secret-safe conventions exist. **Missing:** organization/workspace authorization policy, formal scope checks at all service boundaries, constitutional classification/redaction contract, and integrated provider credential ownership.

## Migration Strategy

Introduce scope-aware authorization after component 07, with central policy checks and redaction/schema validation at Context/Event/Evidence boundaries. Preserve existing login/token mechanisms as authentication adapters.

## Risks and Dependencies

Security regressions can cause data disclosure or unauthorized execution. Depends on identity/scope model, provider binding, and event envelope.

## Readiness

**Partially Ready.** Baseline controls exist but cannot satisfy the target’s scope-aware model yet.

## Evidence

`bridge/settings/base.py`; `projects/runtime_api.py`; `projects/factory_chat.py`; `projects/execution.py`; `projects/models.py` (`ProviderAuditEvent`).

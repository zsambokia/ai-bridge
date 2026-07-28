# Orchestrator Context Isolation Audit

## Verdict

**PASS after remediation.** The Engineering Orchestrator now constructs and checks a complete, deterministic context tuple before every public orchestration-domain transition. A missing, inactive, unready, inconsistent, or unauthorised cross-project binding raises a stable context error before an operation can dispatch execution, validate, continue, deploy, or roll back.

This audit covers the AI Bridge control-plane boundary. A privileged operator directly changing production database rows is outside that boundary; it is not an Orchestrator execution path and must be controlled by database access governance.

## Canonical context tuple

| Level | Canonical identity | Resolution and fail-closed rule |
| --- | --- | --- |
| Platform | `ai-bridge.platform.v1` | A single constant owned by `projects.orchestration_context`; it identifies the governed AI Bridge platform policy and shared infrastructure. |
| Project | `project:<Project.project_id>` | `Project.project_id` and `repository_full_name` are unique. The registry entry must be `ACTIVE` and `READY`, otherwise `CONTEXT_PROJECT_UNRESOLVED` is raised. |
| Work | `orchestration:<session UUID>`, `incident:<incident UUID>`, or `remediation:<workflow UUID>` | UUID-backed durable model tokens prevent ambiguity and retries reuse their original work record. An empty work identity raises `CONTEXT_WORK_UNRESOLVED`. |

`projects.orchestration_context` is the sole binder for this domain. Its `bind`, `for_session`, `for_incident`, and `for_remediation` functions return the tuple or throw; callers do not fall back to a default project or infer one from repository names, issue text, branch names, or an LLM response.

## Findings and repairs

| Finding | Risk | Repair and regression proof |
| --- | --- | --- |
| The original bounded LLM request did not expose explicit platform/project/work identifiers. | An otherwise bounded prompt was harder to prove and audit as context-bound. | `build_context` now includes all three IDs. `test_bounded_context_excludes_secrets_and_repository_contents` asserts them as well as the existing secret/content exclusions. |
| `OrchestrationSession.idempotency_key` is globally unique, while a retry could previously return a session owned by a different project. | Cross-project session reuse. | `assess` verifies `session.project_id` on both normal and concurrent-create paths and raises `ORCHESTRATION_IDEMPOTENCY_CONFLICT`. Regression: `test_assessment_rejects_cross_project_idempotency_and_llm_repository`. |
| An incident could be supplied with a session from another project. | An incident work context could inherit a foreign correlation/session. | `record_incident` checks the context before persistence and rejects it with `CONTEXT_SESSION_PROJECT_MISMATCH`. Regression: `test_incident_rejects_a_session_from_another_project`. |
| The LLM root-cause candidate repository was schema-valid even if it named a different project. | A foreign repository could influence a remediation recommendation. | `validate_response` requires every candidate repository to equal the current project repository and records the session as failed before raising `ORCHESTRATOR_CONTEXT_PROJECT_MISMATCH`. Covered by the orchestrator regression above. |
| Remediation lifecycle operations did not share an explicit context guard or persist the tuple in dispatch audit data. | A corrupted or manually mis-bound workflow could reach a later lifecycle transition without an explicit context proof. | Every public remediation transition calls `for_remediation`; dispatch stores the tuple in `McpAuditEvent.details`. Regression: `test_rejects_an_unapproved_cross_project_remediation_context` and dispatch audit assertions. |

## Operation-by-operation isolation proof

### LLM assessment

`assess` binds its persisted `OrchestrationSession` before calling a provider. `build_context` supplies only the tuple, registered project ID and repository, a 500-character summary, schema/version metadata, engineering authority, allowed actions, and prohibited-content rules. It does not include repository contents, logs, secrets, or other projects. Provider adapters receive this single dictionary and cannot turn a recommendation into execution authority: `evaluate_policy` remains deterministic and dispatch is a separate governed path.

The response is schema checked and its root-cause repository must exactly match the bound project repository. Invalid or foreign context causes the session to be persisted as `FAILED`; a context mismatch is then re-raised to the caller.

### Incident, evidence, and ownership

`record_incident` binds the requested incident work identity before creating a row and rejects a foreign session. `add_evidence` and `assess_ownership` bind the durable incident before using evidence or candidate projects. Evidence is stored under one `FailureIncident`; the ownership assessment accepts only registered, evidence-backed candidates. The selected target is explicit rather than inferred from an LLM response.

### Remediation, validation, continuation, release, and rollback

`create_remediation` first binds the incident, then requires an `ALLOW` ownership assessment. Its target project is the assessment's selected project. A cross-project target is allowed only when the existing ownership policy explicitly selected that registered project; otherwise `CONTEXT_REMEDIATION_PROJECT_MISMATCH` stops the operation.

`link_contract`, `dispatch_remediation`, `enforce_timeout`, `cancel_remediation`, `validate_remediation`, `continue_workflow`, and `deploy_or_rollback` all bind the durable remediation first. Contracts, approvals, executable scopes, execution runs and deployment records are then checked against `workflow.project`. Dispatch records the tuple with the contract and approval in the durable audit event. Therefore a foreign contract, approval, deployment target, or rollback target cannot be reached through a normal Orchestrator path.

The existing contract/execution service adds the next boundary: its immutable issued payload binds project, repository, branch, baseline, scope, evidence root and provider selection immediately before execution. The Orchestrator never uses a GitHub Issue identifier as an authority or repository selector; there is no Orchestrator GitHub issue-mutation entry point to misdirect.

## Context-leak matrix

| Threat | Deterministic control |
| --- | --- |
| Cross-project repository access or LLM repository reference | Unique project repository registry, ready/active binder, exact candidate-repository validation, and contract repository validation. |
| Wrong issue or Sprint continuation | No issue text drives context. Work continuation uses the persisted remediation UUID, then scope/contract/project equality checks. |
| Foreign evidence or documentation | Evidence is incident-owned and ownership uses only that incident's evidence references. Contract evidence roots are bound by the existing contract validation; prompt construction excludes documents and repository content. |
| Wrong remediation target | Only an `ALLOW` ownership assessment can select a target; a cross-project workflow must agree with that exact selected project. |
| Wrong deployment or rollback target | The workflow context is checked before release; approval, validation result, and selected adapter are then checked by the release path. |
| Provider context leak | The provider-neutral interface receives one bounded dictionary created for the current session; no provider SDK or provider-specific context object is imported by the orchestration domain. |

## Release-gate regression coverage

The following test modules are mandatory regression evidence for this audit:

```text
projects/tests/test_orchestrator.py
projects/tests/test_incidents.py
projects/tests/test_remediation.py
```

They include negative tests for global-idempotency reuse, foreign session, foreign LLM repository, unapproved foreign remediation, and durable dispatch context audit data. Repository-wide lint, Django checks, migration consistency, type checking, and the complete test suite remain the release gate that prevents these guards from being silently removed or broken.

## Conclusion

Within the AI Bridge Orchestrator boundary, every decision and mutation has a resolved platform, project, and durable work identity before it proceeds. Uncertainty is an error, never a best-effort default. The only intentional cross-project flow is a recorded, policy-allowed ownership handoff, which changes to the explicitly selected target project and remains contract- and approval-bound thereafter.

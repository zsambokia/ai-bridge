# EPIC #9 full independent audit

Date: 2026-07-28

Classification: **PASS — EPIC COMPLETE AND PROVEN**

## Method and evidence boundary

This audit did not accept the earlier Sprint status labels as proof. It reviewed
the EPIC #9 source changes from `816c807` through `7e4c461`, the models and
migrations, provider and executor boundaries, deterministic policy functions,
all EPIC tests, and the final repository gate results. The working tree also
contained unrelated Product Owner work; it was inspected only as needed for
the repository-wide gate and was not changed or included in the EPIC commit.

The original 116-test result included the following EPIC test assets:

| Sprint | Test asset and coverage | Status |
| --- | --- | --- |
| A | `projects/tests/test_orchestrator.py`: deterministic policy, invalid response, durable assessment, bounded context, provider neutrality | PASS |
| A/B | `projects/tests/test_providers.py`: registered-model selection and structured response decoding through the existing provider platform | PASS |
| B | `projects/tests/test_incidents.py`: idempotent secret-safe incident evidence; single-owner assessment; ambiguous and cross-project fail-closed results | PASS |
| C/D/E | `projects/tests/test_remediation.py`: ownership/contract linkage, governed dispatch, timeout, validation, resume/retry, deployment, rollback | PASS after remediation listed below |

The exact pre-audit EPIC test functions in that 116-test run were
`test_policy_is_deterministic_and_fails_closed`,
`test_response_rejects_missing_evidence_and_unbounded_candidate`,
`test_assessment_is_durable_idempotent_and_never_dispatches`,
`test_invalid_provider_output_is_recorded_as_failed_session`,
`test_bounded_context_excludes_secrets_and_repository_contents`,
`test_domain_has_no_openai_specific_dependency`,
`test_configured_provider_uses_the_registered_model_platform`,
`test_model_selection_and_response_decoding_stay_in_provider_platform`, the
incident tests `test_incident_and_evidence_are_idempotent_and_secret_safe`,
`test_ownership_requires_registered_evidence_and_confident_single_owner`, and
`test_cross_project_and_ambiguous_ownership_fail_closed`, plus the remediation
tests `test_remediation_requires_allowed_ownership_and_consumed_contract`,
`test_independent_validation_resumes_or_requires_a_new_contract`,
`test_failed_validation_requires_new_contract_without_auto_dispatch`,
`test_timeout_is_durable_and_does_not_create_a_replacement_run`,
`test_dispatch_uses_canonical_executor_and_audit_linkage`, and
`test_deployment_and_rollback_require_separate_explicit_authority`.

The audit added six regression tests, increasing the suite from 116 to 122:
`test_provider_boundary_guard_covers_orchestration_and_remediation_domains`,
`test_retry_has_independent_validation_history_and_escalates_when_bounded`,
`test_validation_replay_is_immutable_and_does_not_duplicate_timeline`,
`test_cancellation_rechecks_scope_bound_execution_authority`,
`test_release_idempotency_and_provider_failure_are_durable`, and
`test_rollback_provider_failure_is_durable`.

## Sprint acceptance matrix

| Sprint | Scope proven against implementation | Result | Evidence |
| --- | --- | --- | --- |
| A — authority and provider foundation | `OrchestratorProvider` is a protocol; `evaluate_policy` deterministically denies high-risk technical actions, requires Product Owner for business/mixed/unsafe actions, and does not grant authority from an LLM response. Response validation, durable sessions, and bounded context are enforced. | PASS | `projects/orchestrator.py`, `projects/tests/test_orchestrator.py` |
| B — incidents and ownership | Incidents/evidence are durable and idempotent; evidence is bounded and secret-safe; ownership uses registered projects/dependencies and ambiguity/cross-project cases fail closed. | PASS | `projects/incidents.py`, migration `0018`, `projects/tests/test_incidents.py` |
| C — remediation and dispatch | A remediation requires an `ALLOW` ownership result, an existing published scope, a consumed schema-2 contract and matching execution approval. It dispatches only through `start_run`, records MCP audit linkage, and re-checks cancellation/timeout authority. | PASS | `projects/remediation.py`, migration `0019`, remediation tests |
| D — independent validation and continuation | Validator identity differs from executor identity; completed run and evidence are required. Validation results are immutable per run, retries preserve history and require a different consumed contract, and retries are bounded/escalated. | PASS | migration `0020`, remediation tests |
| E — release, rollback and integrated proof | Deployment and rollback use separate explicit authority, no implicit adapter exists, idempotency keys are bound to their request, and provider failure leaves a durable FAILED record. The tested path covers incident → ownership → remediation → contract → executor → validation → resume → deployment/rollback. | PASS | `projects/remediation.py`, remediation tests |

## Provider-neutral architecture review

The orchestration domain has no OpenAI SDK dependency or direct OpenAI import.
`projects/orchestrator.py` depends only on the local `OrchestratorProvider`
protocol. `projects/remediation.py` has no LLM-provider dependency at all.
`RegisteredModelOrchestratorProvider` in `projects/orchestrator_providers.py`
adapts the existing `ExecutionProvider` registry, `model_adapter_for`,
`select_model_provider`, and `structured_model_response` platform. OpenAI is
therefore a configured first implementation, not an orchestration-domain
integration. The AST guard added by this audit rejects `openai` imports from
both orchestration and remediation domains; `pyproject.toml` has no separate
OpenAI SDK dependency.

Execution authority is independently enforced at every mutation boundary:
policy assessment does not dispatch; remediation creation requires allowed
ownership; contract linking requires a consumed hash-bound contract and
published scope; dispatch, cancellation and timeout re-check scope-bound
execution approval; deployment and rollback require their own authority. An
LLM recommendation is only input to deterministic policy and never an
execution credential.

## Findings and repairs

Two material gaps were found during this independent audit and repaired before
closure.

1. A failed validation set `RETRY_REQUIRED`, but the one-to-one validation
   model and contract-link transition could not support a real second attempt.
   Migration `0020` makes validation per remediation *and execution token*,
   records retry counters, requires a different consumed contract, and
   deterministically escalates when the configured retry limit is exhausted.
   Replayed validation and continuation calls are now idempotent.
2. `deploy_or_rollback` invoked an external adapter inside an atomic database
   transaction. An adapter failure rolled back the FAILED audit record. The
   adapter invocation is now outside the record-creation transaction; both
   deployment and rollback provider failures persist a FAILED record. A
   unique idempotency key is race-safe and mismatched replay is rejected.

No unresolved critical technical debt remains for EPIC #9. Deliberate
operational limitations remain fail-closed: a registered release adapter is
required, a previously REQUESTED adapter call is never automatically replayed,
and a terminal retry exhaustion requires escalation rather than silent further
execution. These are governance safeguards, not unproven scope.

## Final verification

All commands were run from the final audited state:

```text
python -m pytest -q                                      PASS — 122 passed
python manage.py check --settings=bridge.settings.local  PASS
python -m scripts.release_gate                            PASS
python manage.py validate_scopes                          PASS
python manage.py makemigrations --check --dry-run         PASS — No changes detected
git diff --check                                          PASS
```

The release gate includes Django checks, the complete pytest suite, Ruff lint,
Ruff formatting verification, and mypy. The independent regression tests also
exercise malformed provider output, missing validation evidence, scope and
approval mismatch, cancellation, timeout, provider unavailability, duplicate
idempotency keys, and retry escalation.

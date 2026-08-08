# Canonical Runtime Architecture Compliance Review

Date: 2026-08-08
Scope: `bridge:ai-bridge:sprint:712aef15-2426-4f57-88b6-8b1389807b3e`
Proposal hash: `1e54604709d93af8c5be513779a7679a8503d6cc19fe6162564fc3b7827fbe6f`
Mode: Factory Development Mode (Product Owner-authorized bootstrap execution)
Branch: `feature/orki-runtime-foundation-integration`
Baseline: `262ec6700b5b5481fcf917c8eb86e9114998abd8`

## Decision

**PASS - READY FOR OPERATIONAL VALIDATION.**

The implemented Factory Chat path conforms to the canonical Runtime direction in
the reviewed source and targeted/component test evidence. The browser E2E and
complete-regression gates did not complete in this environment because its
interactive browser is unavailable and commands have a 64-second ceiling. The
Product Owner classifies these as environmental operational-validation gates, not
architecture blockers, and requires Manual Acceptance Validation in a capable
release environment. No merge, tag, branch deletion, or worktree cleanup is
authorized until that validation passes.

## Findings

| Requirement | Result | Evidence |
| --- | --- | --- |
| Factory Chat has one provider execution path | PASS | `factory_chat_message` creates a Runtime execution; `dispatch_factory_chat_execution` is the only Factory Chat provider boundary. The former `factory_orki.reply` direct-dispatch function was removed. |
| No Runtime/OESM bypass on the message path | PASS | Browser -> `/factory/chat/message` -> Runtime create -> Runtime dispatch -> provider -> verification -> reflection -> knowledge integration -> completed. |
| Goal -> Plan -> Execution is durable | PASS | `OrkiGoal`, `OrkiPlan`, and `OrkiExecution` are linked records; the execution projection exposes all three statuses. |
| Reflection precedes knowledge integration | PASS | Runtime enters `REFLECTING`, persists `OrkiReflection`, then enters `KNOWLEDGE_INTEGRATING`; acceptance evidence asserts event ordering. |
| Cognitive State is not duplicated | PASS | Runtime delegates observations to established Cognitive State owners through `record_runtime_cognitive_observation`; it stores only execution facts, lifecycle events, reflection, and knowledge-integration references. |
| Governance ownership is retained | PASS | Approval continues through the canonical `approve_plan` owner. Runtime observes and coordinates its lifecycle; it does not replace approval, `ExecutionRun`, queue, or evidence ownership. |
| Provider neutrality is retained | PASS | Provider selection and adapter invocation remain behind the existing provider registry. The Runtime owns the call boundary, not a provider-specific implementation. |
| Runtime presentation is server-owned | PASS | `runtime_presentation` deterministically projects OESM state to Hungarian human text. SSE/UI consume this projection and do not infer state. |

`projects/orchestrator_providers.py` still contains registered MCP/orchestrator
provider calls. Its callers are MCP/orchestration services, not the Factory Chat
message route; it is outside the Factory Chat provider path and was not changed.

## Runtime Presentation Contract

Every Runtime SSE `runtime`, `snapshot`, terminal, and event payload includes
the server-generated presentation fields:

```text
runtime_state
progress_percent
current_step
human_message
started_at
estimated_next_step
evidence_reference
```

The same projection also carries `goal_status`, `planning_status`,
`waiting_message`, `recovery_events`, `reflection_status`, and
`knowledge_integration_status`. The Live Runtime Monitor renders those fields
directly. Provider/configuration faults transition to `WAITING_EXTERNAL` with a
specific reason; the former generic `CHAT_UNAVAILABLE` response is absent.

This is a deterministic Runtime Presentation Layer only. It introduces neither
a Behaviour Engine nor a Persona Engine.

## Lifecycle and Exceptions

Normal Factory Chat execution follows:

```text
CREATED -> PLANNING -> DISPATCHING -> RUNNING -> VERIFYING
-> REFLECTING -> KNOWLEDGE_INTEGRATING -> COMPLETED
```

Provider and structured-context failures remain Runtime states with durable
events and evidence. Pause, user input, recovery, approval, and cancellation
use the existing OESM transitions. A natural-language plan approval message is
classified at Runtime ingress, runs through `WAITING_APPROVAL`, and delegates
the approval decision to the canonical Governance owner before completion.

The existing explicit plan-approval action remains a Governance UI operation,
not a Chat message or a provider execution route. It is not an alternate
Factory Chat provider path.

## Validation Performed

| Gate | Result |
| --- | --- |
| `python manage.py check` | PASS |
| `python manage.py makemigrations --check --dry-run` | PASS |
| `ruff check .` | PASS |
| Runtime/Factory targeted suite | PASS — 45 tests |
| Acceptance, Factory Chat integration, Mission E2E subset | PASS — 6 tests |
| Component regression groups | PASS — 9 + 41 + 18 + 31 tests |
| `projects.tests.test_factory_chat_browser_e2e` | OPERATIONAL VALIDATION REQUIRED - command environment timed out before result |
| Full `python manage.py test` | OPERATIONAL VALIDATION REQUIRED - command environment timed out before result |

## Required Next Action

Run the Product Owner-required Manual Acceptance Validation, browser E2E, and
complete suite in a release environment with an interactive browser and no
64-second command ceiling. Attach the resulting final-state evidence, rerun the
release-gate report, and only then request Product Owner merge approval.

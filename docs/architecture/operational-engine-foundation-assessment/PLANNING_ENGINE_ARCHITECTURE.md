---
status: TRANSITIONAL
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Planning Engine architecture

## Purpose

The Planning Engine owns the evidence-backed transition from an expressed mission to an approval package. It does not execute the plan and a provider does not decide that planning is complete.

## Planning Session Machine (PSM)

```text
CREATED -> MISSION_ANALYSIS -> LOAD_CONTEXT -> LOAD_KNOWLEDGE
-> LOAD_REPOSITORY -> UNDERSTANDING -> GAP_ANALYSIS
-> QUESTION_GENERATION -> WAITING_USER -> UNDERSTANDING_UPDATE
-> GAP_ANALYSIS

GAP_ANALYSIS -- no critical unknowns --> PLAN_SYNTHESIS
-> ALTERNATIVE_ANALYSIS -> PLAN_VALIDATION -> APPROVAL_PACKAGE -> COMPLETED
```

`WAITING_USER` is durable and consumes no worker. `CANCELLED` and `FAILED` are valid terminal/error states from non-terminal states. Recoverable provider or retrieval faults enter a bounded retry state with an evidence record.

## Hard planning gate

The only transition to `PLAN_SYNTHESIS` is:

```text
mission_confidence >= configured_threshold
AND open_questions == 0
AND critical_unknowns == 0
AND required context receipts are current
```

Otherwise the only permitted next action is `QUESTION_GENERATION` or a recoverable failure. The confidence threshold is policy, not provider output.

## Provider role

The provider may return structured candidate material:

```text
understanding, known_facts, unknown_facts, critical_unknowns,
questions, confidence, suggested_next_action
```

The Planning Engine validates this material against policy and durable context, then determines the PSM transition. A provider cannot emit a plan approval, create an execution contract, or bypass a question cycle.

## Planning evidence

Each PSM transition emits an immutable receipt containing session id, input versions, state before/after, contextual sources, validation outcome, and retry correlation id. The approval package contains assumptions, alternatives, risks, scope, estimate, unresolved non-critical items, and all receipts needed for Product Owner review.

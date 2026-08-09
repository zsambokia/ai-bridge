# Orki Workspace Runtime Flow

**Status:** implemented Factory Development Mode behaviour.

## Mission understanding and question gate

Factory Chat treats a user message as a mission-understanding request, not as
authority to prepare a plan. The Runtime owns the decision to enter Planning;
the model provider may supply observations, but cannot mark a mission ready.

```text
POST /factory/message/
-> UNDERSTANDING
-> SEMANTIC_SEARCH
-> provider observation
-> GAP_ANALYSIS
-> QUESTION_GENERATION -> WAITING_USER
   (when a critical unknown or open question remains)
-> UNDERSTANDING (next user answer)
```

This loop can repeat across as many user answers as are needed. The Runtime
persists the resulting mission understanding, confidence, critical unknowns,
open questions, and generated questions as canonical mission state and
append-only Runtime events.

Planning is permitted only when all of these conditions are true:

```text
mission confidence >= 0.90
AND open questions == 0
AND critical unknowns == 0
```

Only then does the Runtime transition to `PLANNING` and
`WAITING_APPROVAL`. Until then it is `WAITING_USER`; the Orki chat message
explains that Planning is blocked and displays the next questions. A provider
claim such as "the plan is ready" cannot bypass this gate.

The critical mission fields are objective, target users, primary workflow,
required inputs, required outputs, MVP boundary, and persistence requirements.
The questions are generated from the still-missing fields, so a response never
silently invents product decisions.

## Provider boundary

The provider response is treated as an observation with these permitted
semantic contributions:

- understanding;
- known and unknown facts;
- candidate questions;
- confidence;
- suggested next action.

The Runtime normalizes and evaluates that observation against canonical mission
state. It alone decides readiness, execution state, plan generation and
governance transition.

## Structured decision path

```text
validated ExecutionRequest -> start_structured_decision_execution
-> PLANNING -> READY -> execute_structured_decision
-> DISPATCHING -> RUNNING -> VERIFYING -> REFLECTING
-> KNOWLEDGE_CANDIDATE -> COMPLETED
```

Failure is explicit: `FAILED -> RECOVERY -> RETRYING`; user or governance waits
remain explicit states. Runtime events are append-only and
`execution_projection` is the UI/API/SSE read contract.

## Workspace presentation rule

The chat is the primary worklog and decision surface: understanding, search,
questions, plan and approval information appear there. The side rail is a
compact read-only projection of Runtime, Cognitive State, Context Package and
repository status. Lifecycle transitions remain server-owned; the browser does
not poll or own OESM state.

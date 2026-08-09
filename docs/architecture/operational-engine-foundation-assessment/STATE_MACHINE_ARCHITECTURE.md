# State-machine architecture audit

## State ownership

| Machine / record | Owner | May transition it | May observe it |
| --- | --- | --- | --- |
| OESM mission runtime | Runtime Foundation | Runtime governance service | all projections and engines |
| PSM planning session | Planning Engine | Planning Engine only | Runtime, Conversation |
| WSM workflow instance | Workflow Engine | Workflow Engine only | Runtime, execution projections |
| Task | Workflow Engine | Workflow Engine / authorized task adapter | ExecutionRun |
| ExecutionRun / ExecutionJob | Runtime execution service | governed execution service | Workflow, Provider Gateway |
| Approval | Runtime governance service | Product Owner action + Runtime | Planning, Workflow |
| Repository lifecycle | Repository Engine | Repository Engine | Planning, Workflow |
| Knowledge pipeline | Knowledge Engine | Knowledge Engine | Planning, Runtime |
| Reflection run | Reflection Engine | Reflection Engine | Runtime, Learning |

## Non-overlap rules

The OESM may decide that a mission is waiting for clarification or approval, but it cannot mutate the PSM's gap list. The PSM may request a question, but cannot approve or execute. The WSM may schedule a task, but cannot hold a provider lease. An ExecutionRun may finish an attempt, but cannot mark a Workflow complete without a Workflow Engine transition.

## Audit finding

The present Runtime state map contains planning and gap-analysis transitions, and the present Workflow Engine owns durable workflow/task state. This is a viable bootstrap split. The boundary becomes unsafe where a workflow adapter makes conversation and provider decisions, because it turns one WSM transition into an ungoverned cross-domain operation. The migration must introduce ports before extracting any state machine.

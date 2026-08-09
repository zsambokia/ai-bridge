# Runtime Audit

## Observed responsibility chain

| Responsibility | Current canonical seam | Audit result |
| --- | --- | --- |
| Intent/goal ingress | Factory Chat -> `start_factory_chat_execution` | present, durable and retry-aware. |
| Planning | Orki plan and `PLANNING` events | present. |
| Approval/governance | Factory plan observation and wait states | present; must remain explicit. |
| Provider selection | `dispatch_factory_chat_execution` / provider registry | present at a narrow boundary. |
| Execution/verification | runtime transition/event functions | present for structured and chat paths. |
| Reflection | reflection record/candidate validators | present. |
| Knowledge candidate | `RuntimeKnowledgeCandidate` then pipeline | present as hand-off, not direct mutation. |
| Context Package consumption | persisted package exists, runtime reference contract is not consistently exposed | integration gap. |

## Transition evidence

Executable test seams discovered:

- `projects/tests/test_orki_runtime.py`: shadow start, approval observation,
  pause/resume and external-wait recovery.
- `projects/tests/test_factory_chat.py`: durable chat result, provider failure,
  plan creation/approval, memory review and project isolation.
- `projects/tests/test_structured_decision_runtime.py` and
  `projects/tests/test_runtime_contract.py`: structured decision and no direct
  AKB mutation assertions.

The state map in `projects/orki_runtime.py` includes explicit approval,
governance, external/user waits, failure, recovery and retry transitions.
`projects/runtime_api.py` exposes read detail and SSE projections plus guarded
controls. This evidence supports a projection-first Workspace design.

## Gap

Intent detection and planner/reasoner are not a single verified Workspace
pipeline: Factory Chat uses a provider response path, while structured decision
execution requires an already validated request. A future implementation Sprint
must choose/declare the governed hand-off rather than conflate them in UI.

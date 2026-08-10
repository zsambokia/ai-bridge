---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Structured Decision Framework

## Canonical contract boundary

`projects.decision_contract` is a pure Python boundary. It imports only the
Semantic Context and the private Reasoning result to create an immutable,
serializable `StructuredDecision.v1`. It has no Django, Provider, OESM,
`ExecutionRun`, Runtime, queue, or execution import.

```text
Semantic Context (ranked candidates + evidence)
                    |
                    v
Reasoning internal StructuredDecision
                    |
                    v
StructuredDecisionBuilder
                    |
                    v
StructuredDecision.v1 -- DecisionValidator -- invalid -> repair feedback
                    |
                  valid
                    v
ExecutionRequest projection [no dispatch, STOP]
```

## Contract and evidence

The version is literal: `StructuredDecision.v1`. Each instance includes a
confidence model (`overall`, `semantic`, `reasoning`, `planning`, `critic`) and
typed evidence covering Knowledge entry IDs, embedding hits, activated
behaviour, plan identifiers, and Critic observations. `DecisionValidator`
checks mandatory values, confidence range/minimum, evidence-plan and
evidence-behaviour consistency, capability requirements, and risk consistency.

## Audit and API boundary

The Decision API computes the same pure pipeline from supplied semantic input.
A valid result is stored as an append-only `StructuredDecisionRecord` solely
for its `GET /reasoning/decision/{id}` audit retrieval. Invalid results return
repair feedback and are not recorded. This is decision evidence storage, not
AKB, Reflection, Knowledge Integration, execution state, or a command queue.

```text
POST /reasoning/decision
    -> SemanticContextV2 -> Reasoning -> StructuredDecision.v1 -> validate
    -> valid: audit record + JSON response
    -> invalid: 422 repair feedback

GET /reasoning/decision/{id} -> audit record only
GET /reasoning/schema        -> versioned contract schema only
```

The future Runtime may consume only a validated `ExecutionRequest`; Sprint 04
does not connect that projection to Runtime.

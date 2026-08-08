# Orki Runtime Orchestrator

The Runtime consumes an already validated `ExecutionRequest`; it neither calls
Semantic ranking nor Reasoning selection. The immutable, versioned plan stores
the decision reference and SHA-256 plan hash.

```text
Semantic Layer -> Reasoning Layer -> StructuredDecision
                                      |
                                      v
              Runtime: Planning -> Ready -> Running -> Verifying
                                      -> Reflecting -> KnowledgeCandidate -> Completed
```

Failure follows `Running -> Failed -> Recovery -> Retrying -> Running`.
Runtime events are append-only and the existing SSE endpoint projects the
current state, behaviour, provider gateway, events, evidence and progress.

`RuntimeReflectionCandidate` and `RuntimeKnowledgeCandidate` are immutable,
explicit Runtime contract artifacts. Their schema is defined in
`projects.runtime_contract`; it excludes embedding, vector, index, activation,
AKB, and KnowledgeEntry ownership. The historical `OrkiKnowledgeIntegration` is
isolated in the deprecated compatibility adapter for legacy Factory paths and is
not invoked by canonical executions.

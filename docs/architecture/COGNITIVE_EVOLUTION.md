# Cognitive & Behaviour Evolution

Sprint 07 adds a bounded learning layer without granting it Runtime, Reasoning,
Semantic, AKB, or governance authority.

```text
verified RuntimeReflectionCandidate
        |
        v
CognitiveExperience (immutable, project-scoped, evidence-bound)
        |
        v
BehaviourCandidate (immutable proposal, CANDIDATE)
        |
        +-- explicit GovernanceApproval --> APPROVED --> CognitiveGuidancePackage
        |
        +-- explicit GovernanceApproval --> REJECTED
```

`CognitiveExperience` can be created only from a verified, evidenced
`RuntimeReflectionCandidate`. Its one-to-one relation makes ingestion
idempotent, and its fingerprint binds the reflection contract, outcome and
evidence. A candidate records a proposed strategy and bounded guidance, but it
cannot execute work, alter a structured decision, or promote itself.

`govern_behaviour` accepts only a non-revoked `GovernanceApproval` for the
same project whose action is `cognitive_evolution.govern_behaviour`,
`ALL_GOVERNED_MUTATIONS`, or `ALL`. Approval or rejection is terminal and is
added to the candidate's audit trail.

`build_guidance` returns only approved patterns for the requesting project,
with approval and experience evidence and transparent metrics. It does not
rank or filter candidates by relevance: semantic retrieval remains the only
relevance-selection authority. The optional query is consumer provenance only.
No service in this layer imports or invokes Runtime, Reasoning, the Semantic
Layer, the Knowledge Pipeline, the AKB, embeddings, or the Vector Store.

The MVP publishes a durable guidance package; attaching it to a future
Reasoning input is a separately governed scope. Behavioural improvement is
therefore evidence-backed and reviewable without autonomous adaptation.

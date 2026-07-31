# Orki mandatory orchestration gate

Sprint 2 makes `OrchestrationSession` the durable, mandatory decision boundary
for a normal governed execution.  The public ChatGPT-facing MCP confirmation
path is:

```text
conversation.confirm
-> OrchestrationSession
-> OwnershipAssessment + OrchestrationDecision
-> ContextPackage
-> published Scope
-> ExecutionContract
-> ExecutionRun / ExecutionJob
-> Workspace / provider activity / evidence
```

## Sprint 3 durable context consumption

The context portion of this trace is now a first-class durable chain:

```text
active AKB entries
-> deterministic KnowledgeContextPackage
-> OrchestrationSession / OrchestrationDecision
-> ExecutionContract
-> ExecutionRun
```

The package records the retrieval intent and query, entry IDs, source versions,
stale and conflict warnings, and its SHA-256 hash. Orki records the package on
the session before assessment and binds the same package to the resulting
decision. Contract issuance and run queueing persist the subsequent bindings.
Dispatch continues to recompute and verify the expected package; it must reject
a context, project, decision, provider, or hash mismatch before work begins.

This is deliberately not hidden model memory. Session B can consume Session A's
approved project knowledge without re-asking for that decision, while a second
project cannot retrieve it. The read-only MCP and Admin projections expose the
same package identity and consumer bindings for operational audit.

The session stores an actor binding, selected project and repository, context
package hash, runtime-profile hash, provider identity, decision hash and final
outcome.  It stores concise policy rationale, never hidden reasoning.

`open_gate` is idempotent for a conversation flow.  It assesses registered
projects from the requested text, treats one foreign project as a cross-project
selection, and fails closed with `AMBIGUOUS_OWNERSHIP` when more than one project
is implicated.  A technical request remains an engineering decision; a
commercial or otherwise business-classified request requires Product Owner
authority.

The issued contract embeds the session, context and decision bindings and
persists them as first-class relations.  Queueing and worker dispatch re-check
the same bindings.  A project/repository, context, decision, authority,
provider, or hash mismatch rejects dispatch before workspace provisioning.

Direct public MCP contract-generation tools return
`ORCHESTRATION_GATE_REQUIRED`.  Older internal recovery paths retain their
separate, durable lifecycle records; they are not normal ChatGPT execution and
are not used as Sprint 2 acceptance evidence.

Django Admin exposes the session on conversation, assessment, contract, and run
records.  The MCP confirmation result includes the same concise trace used by
the API projection: session token, project/repository, assessment confidence,
authority and policy result, context/decision hashes, provider/runtime profile,
and final outcome.

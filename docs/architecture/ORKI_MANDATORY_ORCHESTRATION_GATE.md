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

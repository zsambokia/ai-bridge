---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# Orki Workspace Architecture — Discovery Audit

**Status:** proposed target architecture; no implementation authority
**Audit scope:** `Orki Workspace Discovery Audit` (Factory Development Mode)
**Observed baseline:** `bf6f886bb5a08187eafb9cccd02b662ff9856f66` on `main`

## Finding

The current canonical product surface is the authenticated Factory Chat. It is a
server-owned projection over Project, Cognitive State, Factory Plan, governed
memory and Orki Runtime; it is not yet a multi-area Orki Workspace. The target
must therefore compose existing owners rather than introduce a second runtime,
memory store, approval flow, or repository lifecycle.

## Canonical ownership

| Concern | Existing owner to retain | Workspace role |
| --- | --- | --- |
| Goal, plan, approval | `factory_planning`, `GovernanceApproval`, `ExecutableScope` | Explain and link; never approve by bypass. |
| Runtime state/events | `orki_runtime`, `OrkiExecution`, `OrkiExecutionEvent` | Read projection and lifecycle controls only. |
| Cognitive state | `factory_workspace`, `factory_missions` | Primary conversational working context. |
| Knowledge/AKB | `knowledge`, `knowledge_pipeline`, semantic layer | Show packages, provenance and review state. |
| Repository lifecycle | `repository_lifecycle`, provider port | Show bootstrap/sync receipts and readiness. |
| Provider | `providers` at the runtime gateway | Show selection/result metadata; no provider access from UI. |

## Required composition boundary

```text
Workspace UI -> read projections / governed action endpoints
                  -> canonical domain services
                  -> persisted models + append-only events
                  -> evidence and repository knowledge
```

The Workspace may request a Context Package through the canonical retrieval
boundary. Orki Runtime must consume the persisted package/reference, never
query `KnowledgeEntry`, `SemanticEmbedding`, or `KnowledgeContextPackage`
directly. This preserves the separation documented in
`KNOWLEDGE_PIPELINE.md` and `ORKI_RUNTIME_ORCHESTRATOR.md`.

## Explicit non-goals for implementation planning

- No new chat-memory database or client-owned state.
- No direct provider, AKB, Git, filesystem, or vector-store calls from UI.
- No automatic execution or approval inferred from a screen action.
- No replacement of the Factory Chat before equivalent projections and
  evidence are accepted.

## Evidence anchors

- Routes: `bridge/urls.py`, `projects/ui_urls.py`.
- Factory projection: `projects/factory_chat.py::_context` and
  `projects/templates/projects/factory_context_status.html`.
- Runtime boundary: `projects/orki_runtime.py`, `projects/runtime_api.py`.
- Knowledge boundary: `projects/knowledge_pipeline.py`,
  `projects/semantic/intelligence.py`.

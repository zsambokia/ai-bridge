# Operational Engine Foundation — assessment report

## Scope and method

This Architecture Discovery Sprint assessed the Runtime Foundation, planning/gap flow, conversation boundary, workflow foundation, state ownership, provider path, knowledge/repository seams, and evidence/governance integration. It is a documentation-only assessment: no application code, data model, migration, or runtime behaviour was changed.

Baseline recorded for assessment: `main` at `bf6f886bb5a08187eafb9cccd02b662ff9856f66`.

Reviewed implementation areas include `projects/orki_runtime.py`, `projects/workflow_engine.py`, `projects/models.py`, `projects/factory_chat.py`, the existing Workflow Engine architecture documents, and the Runtime integration surface.

## Findings

| Id | Finding | Severity | Target disposition |
| --- | --- | --- | --- |
| F-01 | Runtime is the correct canonical owner for mission lifecycle and governance, but contains emerging planning policy. | medium | retain authority; move planning mechanics behind a port/PSM |
| F-02 | Durable workflow/task records exist and establish a viable foundation. | positive | retain and evolve behind WSM ownership |
| F-03 | Workflow chat adapter constructs prompts and invokes providers directly. | high | route through Provider Gateway and governed ExecutionRun |
| F-04 | Planning needs a hard critical-unknown gate independent of provider confidence. | high | Planning Engine PSM controls transition to synthesis |
| F-05 | Conversation is presently close to the desired primary work-journal boundary. | medium | make side panels projections only; prevent direct state writes |
| F-06 | Semantic workflow search evidence is recorded, but template selection is not yet demonstrably based on its ranked result. | medium | make selection policy explicit and evidenced |
| F-07 | Cross-engine calls would create recovery and ownership ambiguity. | high | use durable work items, evidence and outbox events |

## Architecture decision

Adopt incremental Operational Engines: Planning, Workflow, Knowledge,
Repository, Reflection, Learning, Deployment and Documentation. Keep the
Runtime Foundation as the only mission/governance authority. Use a shared
durable Engine Work Item contract with polling and outbox events; retain
domain-specific state machines.

## Acceptance assessment

| Sprint acceptance question | Result |
| --- | --- |
| Can Runtime remain while engines are layered beside it? | PASS — its retained responsibilities are explicit. |
| Are Planning and Workflow independent bounded contexts? | PASS — PSM and WSM have separate owners and contracts. |
| Is early planning prevented architecturally? | PASS — hard gate specified; implementation proof remains a later phase. |
| Is a safe migration path provided? | PASS — seven phased, evidence-gated stages supplied. |
| Has implementation been avoided? | PASS — only this assessment documentation was added. |

## Deferred implementation evidence

The proposed PSM, queue, ports and migration phases are not implemented by this sprint. Their later implementation contracts must include the specified acceptance suites, especially three multi-turn question/answer E2E cases proving that unresolved critical unknowns prevent planning.

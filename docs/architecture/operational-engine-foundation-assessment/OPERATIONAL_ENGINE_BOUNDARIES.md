# Operational Engine boundaries and responsibility matrix

## Boundary rule

A business capability has one durable state owner. Other components may read its published projection but may not mutate it directly.

| Concern | Authoritative owner | Consumers | Explicit non-owners |
| --- | --- | --- | --- |
| Mission lifecycle, policy and approval | Runtime Foundation | Conversation, Planning, Workflow | all Operational Engines |
| Planning confidence, gaps and plan package | Planning Engine | Runtime, Conversation | provider, Workflow Engine |
| Workflow progression and task retries | Workflow Engine | Runtime, execution adapters | Planning Engine, Conversation |
| Execution authorization and worker lease | ExecutionRun / ExecutionJob runtime | Workflow, Provider Gateway | Conversation, Planning |
| Provider selection and invocation | Provider Gateway | governed execution adapter | Conversation, Workflow domain |
| Conversation transcript and user interaction | Conversation Layer | Runtime presentation | engines |
| Knowledge retrieval/index lifecycle | Knowledge Engine | Planning, Runtime | Workflow, provider |
| Repository bootstrap/index lifecycle | Repository Engine | Planning, Workflow | Conversation |
| Reflection and learning candidates | Reflection Engine | Runtime, Learning Engine | Planning, Workflow |
| Evidence publication | Evidence service / canonical store | every engine | no engine may overwrite another engine's evidence |

## Current coupling found

1. `OrkiRuntime.dispatch_factory_chat_execution` delegates to a Workflow adapter, but that adapter constructs Factory-chat prompts and invokes provider code. This crosses the target Workflow-to-Conversation and Workflow-to-Provider boundaries.
2. The Runtime presently contains planning/gap transitions. This is correct for the current foundation, but its planning policy must move behind a Planning Engine port before the state machine grows further.
3. Workflow selection records semantic-search evidence, while the observed selection path falls back to the first approved matching template. The semantic result therefore is not yet an authoritative selection decision.

## Prohibited dependencies

* An engine may not import another engine's service layer.
* A provider may not decide readiness for planning or advance a Runtime state.
* The Conversation Layer may not write planning, workflow, repository, or approval state directly.
* Planning may not start while its authoritative critical-unknown count is non-zero.

## Required ports

`MissionStatePort`, `EngineWorkQueue`, `ContextPackagePort`, `KnowledgeReceiptPort`, `RepositoryReceiptPort`, `EvidencePort`, `ProviderGatewayPort`, and `ExecutionAuthorizationPort` are the architectural ports. Their concrete implementation can initially be in-process and durable; their contracts must not assume that it remains so.

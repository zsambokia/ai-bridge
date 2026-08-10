# Implementation Readiness Matrix

| Component | Constitution target | Repository evidence | Gap | Readiness | First migration boundary |
| --- | --- | --- | --- | --- | --- |
| Mission Domain | Mission is unified intake; Conversation only human adapter | `FactoryMission`, `FactoryChatSession`, `factory_missions.py` | Non-human intake lacks a common Mission facade | Ready | Mission Intake Adapter |
| AI Kernel | Execution-owned Kernel managers/registries/objects | `OrkiExecution`, `ExecutionRun`, `orki_runtime.py` | Two lifecycle authorities and no Kernel boundary | Partially Ready | Kernel facade + execution mapping |
| Operational Foundation | authorized work-item delivery infrastructure | `ExecutionJob`, lease/heartbeat in `execution.py` | Existing dispatcher owns more than OF target | Partially Ready | OF work-item adapter |
| Provider | resolver → provider → executor, immutable binding | `ExecutionProvider`, `ProviderGateway`, `providers.py` | Gateway is primary and binding/profile semantics incomplete | Partially Ready | Provider Integration facade |
| AKB | uniform Knowledge Object graph/lifecycle/KLM | `KnowledgeEntry`, revisions, package, pipeline | entry-centric, no uniform object/reference/KLM subsystem | Partially Ready | KO identity/version projection |
| Event | Kernel Events, immutable and provider-neutral | `ExecutionProgressEvent`, `OrkiRuntimeEvent`, workflow events | fragmented event taxonomies and names | Partially Ready | event envelope/projection |
| Identity & Scope | organization/workspace/repository scope | `Project`, authenticated user, `ExecutableScope` | no organization/workspace ownership hierarchy | Not Ready | scope model ADR + read path |
| Multi-tenancy | tenant-ready, explicit owner and scope | project/platform scopes only | tenant data isolation model absent | Not Ready | identity-and-scope foundation |
| Localization | canonical English + localized assets | no locale configuration/catalogue evidence | no localization domain model | Not Ready | localization policy and content model |
| Security | scope-aware, secret-safe contexts/events/evidence | login, CSRF, MCP token, secret-conscious events | authorization is not scope policy | Partially Ready | scope-aware authorization |
| API & Integration | all non-human intakes converge to Mission | MCP and runtime endpoints | adapters bypass common Mission intake | Partially Ready | Mission intake API |
| UI Architecture | localized human Conversation adapter | Factory Chat and runtime UI routes | UI is coupled to Factory/Runtime terms | Ready | presentation projections |

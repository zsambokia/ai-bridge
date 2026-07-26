# AI Bridge Roadmap

**Status:** ACTIVE PROJECT ROADMAP  
**Scope:** AI Bridge project  
**Execution authority:** roadmap does not authorize implementation; only an approved Sprint may do so  
**Project definition:** `.bridge/project.yaml`

## 1. Product direction

AI Bridge is being built as a generic, governed AI software factory platform capable of onboarding, understanding, developing, testing, documenting, and proving complete software changes across both new and existing Projects.

The platform must remain Project-agnostic. Project-specific repository identity, paths, technology profile, Release Gates, and operational settings belong in Project configuration and Project Context, while the execution rules remain generic.

The near-term objective is to prove that the platform can take one registered Project through a complete, evidence-backed implementation cycle without relying on hidden chat context, manually assembled prompts, or Project-specific branches in the execution engine.

## 2. Roadmap principles

- The roadmap defines direction, sequencing, and dependencies.
- The roadmap does not authorize Codex execution.
- Every implementation must be defined by one explicitly approved Sprint.
- Platform capabilities must be generic unless they are explicitly Project configuration.
- New and existing Projects must use the same onboarding and execution machinery.
- Evidence, Release Gates, and Product Owner Review are mandatory completion conditions.
- Capability completion must be based on accepted evidence, not optimistic status labels.
- Bridge must automatically repair routine technical failures and rerun invalidated gates without Product Owner intervention.
- Product Owner involvement is reserved for business, product, legal, brand, material UX, destructive production-risk, credential, permission, and unresolved constitutional decisions.

## 3. Configuration and operational state boundary

AI Bridge must maintain a strict separation between relatively stable Project configuration and frequently changing operational state.

### 3.1 Static Project definition

Canonical repository-local location:

```text
.bridge/project.yaml
```

This file contains relatively stable Project-specific configuration, including:

- Project identity;
- repository identity;
- default and integration branches;
- governance and workflow paths;
- Sprint, architecture, roadmap, AKB, and evidence roots;
- technology profile;
- repository-wide Release Gates;
- repository policies and static supported-feature configuration.

It must not become a live status store.

### 3.2 Dynamic Project state

Frequently changing state belongs in the operational database and Project Context, including:

- selected Project;
- observed branch and commit;
- active Sprint and pull request;
- validation status;
- refresh timestamps;
- context snapshots;
- state events;
- accepted capability state;
- next safe action.

A separate repository-local status file may be introduced only if a later approved Sprint proves a concrete need for a durable, reviewable status projection. It must be generated from structured state, never edited as a competing source of truth.

Sprint 003 establishes this boundary for Project lifecycle, onboarding, and Context state. A later operational-capability Sprint may add a structured capability-state model; it must remain separate from the static definition.

## 4. Milestone sequence

## Milestone 1 — Project Bootstrap and Onboarding

**Implemented foundation awaiting Product Owner review:** `docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md`

**Goal:** make both new and existing repositories registerable as governed Projects.

Required outcomes:

- Project Registry;
- canonical Project Definition schema;
- `.bridge/project.yaml` creation and validation;
- repository identity resolution;
- new-Project bootstrap path;
- existing-repository assessment and onboarding path;
- governance and document-path discovery;
- onboarding readiness status;
- deterministic evidence that the Project is ready for governed execution.

This milestone must establish the prerequisites consumed by all later capabilities.

## Milestone 2 — Project Context and AKB State Management

**Superseded, not executed specification:** `docs/sprints/SPRINT_002_PROJECT_CONTEXT.md`

**Implemented foundation awaiting Product Owner review:** `docs/sprints/SPRINT_003_PROJECT_REGISTRY_AND_CONTEXT_FOUNDATION.md`

**Goal:** allow the platform to determine and prove where a registered Project currently stands.

Required outcomes:

- active Project selection;
- generic Project Context services;
- repository observation through a replaceable provider boundary;
- configured AKB / current-state reading;
- validation and drift detection;
- explicit conflict reporting;
- immutable context snapshots;
- explicit, gate-protected main-only AKB publication;
- multi-Project isolation.

Sprint 003 establishes only the minimum Registry and first validated Project Context prerequisite. It does not claim completion of the wider AKB state management outcomes above. This milestone must preserve the static configuration / dynamic state boundary described in this roadmap.

## Milestone 3 — Operational Capability State

**Goal:** make capability readiness and implementation status structured, evidence-backed, and independent from static Project configuration.

Required outcomes:

- authoritative capability-state model in the operational database;
- lifecycle states for planned, in-progress, implemented, proven, accepted, deprecated, and unavailable capabilities;
- evidence and final-commit binding;
- generated AKB / current-state projection;
- drift detection between accepted evidence and projected status;
- Project-level capability queries usable by later planning and handoff services.

This milestone is the explicit roadmap home for the `project.yaml` / dynamic status separation.

## Milestone 4 — Generic Handoff Generator

**Goal:** generate a complete immutable Execution Contract without manually assembling repository, Sprint, workflow, Release Gate, or evidence inputs.

Required outcomes:

- Project Registry and Project Context resolution;
- exact approved Sprint binding;
- Project-definition and document hashing;
- deterministic Release Gate and evidence resolution;
- machine-readable and human-readable contracts;
- lifecycle and single-consumption protection;
- supersession and revocation;
- proof that the same implementation handles differently configured Projects without Project-specific branches.

Sprint 005 establishes tiered policy resolution and the full durable contract lifecycle. Subsequent work consumes the smallest sufficient contract level; Epic-level planning must be decomposed into child implementation contracts.

Sprint 006 adds the first deliberately narrow remote MCP proof: a public, authenticated Streamable HTTP server that exposes only a read-only factory status tool while retaining governed Bridge services behind the canonical internal boundary. It also corrects repository-stored issued-contract baseline validation so issuance does not invalidate its own artifact.

Sprint 007 expands the remote MCP surface into a governed, versioned public registry covering project resolution, bounded accepted knowledge, execution preparation, contract lifecycle, audit, idempotency, approval, and execution-start request boundaries.

Canonical specification:

```text
docs/contracts/HANDOFF_EXECUTION_CONTRACT.md
```

## Milestone 5 — Bridge Conversation Orchestrator

**Goal:** turn the individual governed MCP capabilities into one coherent conversational planning and continuation engine.

Required outcomes:

- intent classification for feature, bugfix, refactor, documentation, deployment, research, and recovery work;
- deterministic tool-planning and prerequisite ordering;
- explicit missing-information detection;
- continuation handling across ambiguous project and execution states;
- generation of one bounded Execution Package containing project, goal, accepted knowledge, constraints, policy, gates, evidence obligations, and handoff;
- durable conversation-to-execution state independent of hidden model memory;
- natural-language journeys such as “Folytassuk a Mesél az Erdőt” without requiring the Product Owner to know tool names;
- no lifecycle mutation without canonical approvals and contract rules.

This is the next orchestration milestone after the governed tool surface. It must reuse the Sprint 007 public and canonical services rather than creating a parallel planning stack.

## Milestone 6 — Autonomous Execution and Repair Loop

**Planned Sprint:** `docs/sprints/SPRINT_009_AUTONOMOUS_EXECUTION_AND_REPAIR_LOOP.md`

**Goal:** prove that Bridge can dispatch one governed execution to Codex, observe progress, repair ordinary technical failures, rerun all invalidated gates, collect evidence, and return one truthful final state without routine Product Owner intervention.

Required flow:

```text
Approved execution package
→ issued and consumed tiered Execution Contract
→ Codex execution start
→ repository mutation
→ targeted validation
→ automatic diagnose-and-repair loop
→ dependent gate reruns
→ documentation and AKB synchronization
→ final evidence binding
→ Product Owner Review
```

Required outcomes:

- canonical Codex dispatcher or durable execution-run adapter;
- execution-run lifecycle and progress events;
- exact repository, branch, baseline, contract, and workspace binding;
- automatic repair of test, lint, type, build, migration, browser, dependency, configuration, evidence, and documentation failures when no reserved Product Owner decision is required;
- root-cause analysis after repeated failure;
- retry and rerun limits that prevent silent infinite loops;
- honest blocking only for Constitution-reserved Product Owner decisions or unavailable external input;
- proof that technical failure does not become a Product Owner support request;
- immutable final execution evidence and exact final commit binding.

## Milestone 7 — Complete Governed Execution Loop Proof

**Goal:** prove an end-to-end implementation cycle through the platform on a bounded real application change.

Required flow:

```text
Project selection
→ validated Project Context
→ approved Sprint
→ issued Execution Contract
→ isolated Codex implementation
→ automated tests
→ acceptance suite
→ documentation and AKB update
→ Release Gates
→ final evidence
→ Product Owner Review
```

Proof must include both backend and frontend work when the selected proving Sprint requires them.

## Milestone 8 — Existing Project Safety Proof

**Goal:** demonstrate that an existing repository can be onboarded and modified without uncontrolled restructuring or unrelated regressions.

Required outcomes:

- assessment before mutation;
- canonical-component reuse;
- preservation of unrelated work;
- explicit architecture and AKB conflict handling;
- repository-native tests and Release Gates;
- reversible main-only workflow using new revert or repair commits;
- evidence-backed Product Owner handoff.

A production-critical repository must not be selected as the first safety proof.

## Milestone 9 — New Project Autonomous Delivery Proof

**Goal:** demonstrate that AI Bridge can bootstrap and deliver a complete new application through multiple governed Sprints.

Required outcomes:

- template or technology-profile selection;
- repository creation or initialization;
- Project onboarding;
- architecture baseline;
- frontend and backend implementation;
- automated acceptance testing;
- documentation and deployment preparation;
- full evidence chain across Sprints.

## Milestone 10 — Multi-Project Platform Operations

**Goal:** operate AI Bridge as one platform serving multiple Projects with strict isolation.

Required outcomes:

- Project switching;
- isolated context and execution records;
- Project-specific configuration with generic services;
- repository-provider abstraction;
- operational status overview;
- safe concurrency and execution ownership;
- no Project-specific code paths in platform engines.

## 5. Deferred capabilities

The following are intentionally deferred until the governed development loop is proven:

- organization, department, role, and employee simulation;
- marketing and sales departments;
- customer support operations;
- training and onboarding content platforms;
- autonomous goal decomposition beyond approved Sprint boundaries;
- generalized workflow marketplace;
- advanced analytics dashboards;
- additional broad MCP tool expansion without a proven execution need;
- self-modification without the same Contract, Release Gate, and evidence requirements.

These may remain part of the long-term product vision, but they must not distract from proving autonomous, evidence-backed software delivery.

## 6. Immediate next actions

1. complete the Sprint 007 staging migration recovery and authenticated live MCP tool-call proof;
2. refresh and rescan the Bridge app in ChatGPT Business;
3. implement the Bridge Conversation Orchestrator as the next approved orchestration Sprint;
4. review the completed Sprint 009 autonomous execution and repair-loop evidence;
5. select a bounded proving application Sprint for the first complete frontend-and-backend execution loop;
6. keep `.bridge/project.yaml` as the static Project definition;
7. use the smallest sufficient tiered Execution Contract for every implementation, repair, migration, and recovery task.

## 7. Roadmap success criterion

The roadmap's first major success is reached when AI Bridge can demonstrate, with reproducible evidence, that it can:

- onboard a Project;
- determine its real current state;
- receive one approved Sprint;
- generate an immutable execution handoff;
- dispatch Codex through a governed execution boundary;
- implement and test the change;
- diagnose and repair ordinary technical failures without Product Owner intervention;
- rerun every invalidated Release Gate;
- update documentation and AKB;
- pass all Release Gates;
- present exact final evidence for Product Owner Review;
- do so without Project-specific execution logic, hidden manual context, or routine technical escalation to the Product Owner.

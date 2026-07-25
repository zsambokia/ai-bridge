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

Sprint 003 establishes this boundary for Project lifecycle, onboarding, and
Context state. A later operational-capability Sprint may add a structured
capability-state model; it must remain separate from the static definition.

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

Sprint 003 establishes only the minimum Registry and first validated Project
Context prerequisite. It does not claim completion of the wider AKB state
management outcomes above. This milestone must preserve the static
configuration / dynamic state boundary described in this roadmap.

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

Canonical specification:

```text
docs/contracts/HANDOFF_EXECUTION_CONTRACT.md
```

## Milestone 5 — Complete Governed Execution Loop

**Goal:** prove an end-to-end implementation cycle through the platform.

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

## Milestone 6 — Existing Project Safety Proof

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

## Milestone 7 — New Project Autonomous Delivery Proof

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

## Milestone 8 — Multi-Project Platform Operations

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
- broad MCP tool expansion;
- self-modification without the same Contract, Release Gate, and evidence requirements.

These may remain part of the long-term product vision, but they must not distract from proving autonomous, evidence-backed software delivery.

## 6. Immediate next actions

1. execute Sprint 003 to create and validate the Project Registry, onboarding readiness, and first Project Context foundation;
2. keep `.bridge/project.yaml` as the static Project definition;
3. use `STANDARD` Execution Contracts only after Sprint 003 has produced a valid Project Context;
4. prepare the dedicated Operational Capability State Sprint;
5. implement the generic Handoff Generator only after Project Registry and Project Context are accepted;
6. select a bounded proving application Sprint for the first complete frontend-and-backend execution loop.

## 7. Roadmap success criterion

The roadmap's first major success is reached when AI Bridge can demonstrate, with reproducible evidence, that it can:

- onboard a Project;
- determine its real current state;
- receive one approved Sprint;
- generate an immutable execution handoff;
- implement and test the change;
- update documentation and AKB;
- pass all Release Gates;
- present exact final evidence for Product Owner Review;
- do so without Project-specific execution logic or hidden manual context.

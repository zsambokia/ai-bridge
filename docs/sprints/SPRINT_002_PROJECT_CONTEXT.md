# Sprint 002 — Project Context and AKB State Management

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** resolved from `.bridge/project.yaml` and Project Registry  
**Repository:** resolved from Project definition  
**Target branch:** resolved by the Execution Contract  
**Integration target:** resolved by the Execution Contract  
**Task type:** FEATURE  
**Execution workflow:** resolved from Project definition  
**Evidence path:** resolved from Project definition and Sprint identifier

## 1. Purpose

Implement the smallest reliable Project Context and AKB state-management capability for a Project that has already completed Bootstrap / Onboarding.

Sprint 001 is assumed to have established:

- a registered Project;
- a canonical Project definition;
- repository identity and integration settings;
- governance and workflow document paths;
- a valid onboarding state;
- the minimum repository structure required for governed execution.

Sprint 002 must build on that foundation. It must not recreate onboarding, bootstrap, repository registration, or Project-definition discovery.

The outcome is a generic platform capability that can manage the current operational state of any registered Project without project-specific branches in the implementation.

## 2. Business outcome

After this Sprint, the platform must be able to answer reliably:

> What Project is selected, where does it currently stand, which repository facts support that answer, does the AKB agree with those facts, and what is the next safe action?

For any registered Project, the system must be able to:

- resolve the selected Project from the Project Registry;
- load its canonical Project definition;
- load stored operational context;
- refresh repository facts through a replaceable repository boundary;
- read canonical current-state / AKB documents declared by the Project definition;
- validate whether database state, repository state, and accepted AKB state agree;
- identify stale, incomplete, conflicted, or unavailable context;
- create immutable evidence snapshots;
- explicitly publish accepted durable state back to the repository through a branch / pull-request boundary;
- return a structured next-action recommendation derived from explicit rules.

## 3. Binding context

Read the mandatory context defined by `AGENTS.md` and the issued Execution Contract.

At minimum, the Contract must resolve:

- Project definition path;
- Constitution path;
- execution workflow path;
- approved Sprint path;
- roadmap path when present;
- AKB / current-state paths;
- architecture context paths;
- repository-wide and Sprint-specific Release Gates;
- evidence output paths.

For this first Project Context creation only, the issued Contract may use
`BOOTSTRAP` mode as defined by
`docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`. That mode must be bound to this
Sprint, may be used only when no valid Project Context exists, and does not
authorize Bootstrap, onboarding, or Project Registry creation.

The Sprint must not hard-code a Project name, repository name, branch, technology stack, Release Gate command, or AKB path.

## 4. Dependencies and preconditions

Sprint 002 may begin only when all are true:

- the Project exists in the Project Registry;
- the Project definition is valid;
- the Project onboarding status is `READY` or equivalent;
- repository identity is unambiguous;
- the Project definition declares the canonical AKB / current-state location;
- the Project definition declares repository-wide Release Gates;
- the issued Execution Contract passes integrity validation in either:
  - `BOOTSTRAP` mode, only for this first Project Context creation and only
    when its first-context eligibility rules pass; or
  - `STANDARD` mode, with Project Context status `VALID`.

If any precondition is missing, Sprint 002 must stop with the appropriate governed blocking state. It must not silently perform Bootstrap / Onboarding work.

## 5. Architectural decision

Use a hybrid persistence model.

### 5.1 Operational database responsibility

The database is the operational source of truth for live, structured, frequently changing state, including:

- Project Registry identity reference;
- selected or active Project;
- repository observations;
- current branch and commit observations;
- current Sprint and pull-request observations;
- validation status;
- refresh timestamps;
- immutable context snapshots;
- append-only state events;
- execution-facing structured context.

### 5.2 Repository responsibility

The repository is the durable, human-readable, reviewable source of truth for accepted Project knowledge, including:

- Constitution and governance documents;
- approved Sprint specifications;
- architecture and ADRs;
- Project roadmap;
- accepted current-state / AKB documents;
- closure evidence;
- material Product Owner decisions.

### 5.3 Prohibited duplication

Do not build a Git-like version-control system in the database.

Do not create a repository commit for every operational refresh.

Do not store a second independently edited Project definition in Project Context.

Publishing accepted durable context must be explicit.

## 6. Project Registry and Project Definition integration

Project Context must be generic and Project Registry driven.

It must resolve Project-specific values from the Project definition, including:

- canonical repository identity;
- default and integration branches;
- AKB / current-state paths;
- roadmap path;
- architecture roots;
- Sprint root;
- evidence root;
- repository-wide Release Gate commands;
- repository provider capabilities.

The implementation must not contain code paths such as:

```python
if project.slug == "some-project":
    ...
```

Behaviour differences must come from declared configuration and repository capabilities.

## 7. Approved domain model

Implement the smallest coherent model set required by this Sprint. Existing Bootstrap / Onboarding models must be reused rather than duplicated.

### 7.1 Project reference

Use the canonical Project Registry model created by Sprint 001.

Sprint 002 must not create a parallel `Project` identity model.

### 7.2 ActiveProjectSelection

Stores the selected Project for the current platform execution scope.

Required responsibilities:

- reference one registered Project;
- preserve selection timestamp;
- record selecting actor or execution identity when available;
- reject Projects that are archived, disabled, or not onboarding-ready.

Use the simplest repository-consistent scope. Do not introduce users, teams, organizations, or tenancy.

### 7.3 ProjectContext

Stores the current operational context for one registered Project.

Required data or equivalent structured representation:

- Project reference;
- Project-definition version or content hash;
- observed repository identity;
- observed branch;
- observed HEAD commit SHA;
- observed open pull-request identifier when applicable;
- current Sprint identifier or path when known;
- last completed Sprint or accepted milestone when known;
- canonical AKB source paths used;
- validation status;
- last refresh timestamp;
- last validation timestamp;
- source metadata sufficient to identify where each material value came from.

Allowed validation states must include:

```text
VALID
STALE
INCOMPLETE
CONFLICTED
UNAVAILABLE
```

### 7.4 ProjectContextSnapshot

Immutable evidence-oriented snapshot of resolved context.

Required data:

- Project reference;
- capture timestamp;
- Project-definition version;
- repository identity;
- branch;
- commit SHA;
- Sprint and pull-request observations;
- AKB observations;
- validation status;
- normalized context payload;
- source hashes or equivalent source identifiers where practical.

Snapshots must not change after creation.

### 7.5 ProjectStateEvent

Append-only audit event for material context operations.

Required event types must include at least:

```text
ACTIVE_PROJECT_SELECTED
CONTEXT_REFRESHED
CONTEXT_VALIDATED
CONTEXT_SNAPSHOT_CREATED
CONTEXT_PUBLISHED
```

Reuse existing onboarding / registry event infrastructure when available.

## 8. Required application operations

Implement these operations as explicit application services. Public names may follow repository conventions, but responsibilities must remain distinct and testable.

### 8.1 Active Project operations

- `select_active_project`
- `get_active_project`

Required behaviour:

- selection resolves through Project Registry;
- archived, disabled, or onboarding-incomplete Projects are rejected;
- selecting a Project records `ACTIVE_PROJECT_SELECTED`;
- loading context without a resolvable active Project returns a clear domain error;
- switching Projects must never leak context from the previous Project.

### 8.2 Context operations

- `load_project_context`
- `refresh_project_context`
- `validate_project_context`
- `create_context_snapshot`
- `compare_context_snapshot`
- `publish_project_context`

Internal supporting operations may include:

- Project-definition loading and validation;
- repository-context import;
- AKB parsing;
- drift detection;
- event recording;
- source normalization;
- next-action resolution.

## 9. Repository integration boundary

Implement a replaceable repository-context interface.

The domain and application layers must not depend directly on one provider's HTTP client throughout the codebase.

The boundary must be capable of resolving at least:

- repository availability;
- canonical repository identity;
- default branch;
- selected branch HEAD SHA;
- open pull requests relevant to the Project;
- canonical AKB / current-state documents declared by Project configuration;
- approved Sprint documents when required for validation;
- latest accepted merge or milestone indicators required by this Sprint.

GitHub may be the first provider implementation, but the Project Context domain must remain provider-neutral.

Tests must use deterministic fakes or mocks at the integration boundary. Local tests and Release Gates must not require live credentials.

Do not implement OAuth, webhook ingestion, polling, background synchronization, GitHub App installation, MCP tools, or generic connector orchestration.

## 10. AKB and current-state contract

The Project definition must declare one or more canonical AKB / current-state paths.

Sprint 002 must support at least one primary current-state document.

The AKB reader must extract, when present:

- Project identity;
- current lifecycle phase;
- current or next Sprint;
- last accepted Sprint or milestone;
- active branch or pull request when documented;
- known blockers;
- next approved action;
- last accepted state timestamp or commit reference.

The parser must tolerate absent optional fields and classify the result honestly as `INCOMPLETE` rather than inventing values.

AKB content must never be treated as automatically superior to repository facts or operational state. Conflicts must be reported explicitly.

## 11. Context loading contract

`load_project_context` must return a structured result containing at least:

```text
Project identity
Project-definition version
repository identity
active or observed branch
observed commit SHA
current Sprint when known
last completed Sprint or accepted milestone when known
open pull request when applicable
AKB source summary
validation status
last refresh time
source summary
recommended next action or reason it cannot be derived
```

The next action must come from explicit rules, not free-form speculation.

Minimum rules:

- onboarding is not ready → onboarding required;
- no active Sprint and no open pull request after an accepted milestone → ready for Sprint planning;
- active Sprint branch and open pull request → implementation or review in progress;
- stale context → refresh required;
- conflicted context → explicit resolution required;
- repository unavailable → required external input unavailable;
- AKB missing required accepted-state fields → AKB update required.

## 12. Refresh contract

`refresh_project_context` must:

1. resolve the registered Project;
2. load and validate its Project definition;
3. resolve the primary repository;
4. retrieve repository facts through the canonical integration boundary;
5. read configured AKB / current-state documents;
6. normalize observed state;
7. update `ProjectContext` atomically;
8. record source metadata and refresh time;
9. record `CONTEXT_REFRESHED`;
10. return the refreshed structured context.

A refresh must not:

- create a repository commit;
- publish AKB documentation;
- silently resolve material conflicts;
- create a snapshot unless explicitly requested;
- modify Project Registry configuration;
- modify another Project.

## 13. Validation and drift contract

`validate_project_context` must compare:

- Project Registry identity;
- Project-definition values;
- stored operational context;
- currently observed repository facts;
- canonical AKB / current-state documents.

At minimum, detect:

- stored commit differs from repository branch HEAD → `STALE`;
- Project definition missing required AKB path → `INCOMPLETE`;
- required repository or primary repository missing → `INCOMPLETE`;
- repository cannot be accessed → `UNAVAILABLE`;
- Project-definition repository identity conflicts with Registry identity → `CONFLICTED`;
- database current Sprint materially disagrees with AKB → `CONFLICTED`;
- AKB branch or PR materially disagrees with repository facts → `CONFLICTED`;
- all required observations agree → `VALID`.

Conflict precedence must be explicit:

- no source is silently discarded;
- conflicting fields, values, and sources are returned;
- last known state is preserved;
- resolution requires explicit refresh, publish, configuration correction, or Product Owner decision.

Record `CONTEXT_VALIDATED` for every completed validation.

## 14. Snapshot contract

`create_context_snapshot` must:

- require a resolvable ProjectContext;
- capture the exact current normalized context;
- include Project-definition version and AKB source identifiers;
- store an immutable snapshot;
- record `CONTEXT_SNAPSHOT_CREATED`;
- return the snapshot identifier and material captured values.

`compare_context_snapshot` must identify material differences including:

- Project-definition version;
- repository identity;
- branch;
- commit;
- open pull request;
- current Sprint;
- last accepted milestone;
- AKB state;
- validation status.

Do not build a generic visual diff system.

## 15. Publish contract

`publish_project_context` represents an explicit request to publish accepted durable state to the configured AKB / current-state path.

Publishing must:

1. require context status `VALID` unless an explicit internal override is documented and tested;
2. render the configured current-state document from structured context;
3. target the canonical AKB path declared by the Project definition;
4. use a dedicated branch and pull-request-oriented repository operation;
5. never write directly to the integration target;
6. return branch, commit, changed path, and pull-request metadata;
7. record `CONTEXT_PUBLISHED` only after the repository boundary reports success.

Rendering and orchestration must be fully tested.

Live repository writes are not required by local Release Gates, but the publishing contract must be concrete and replaceable.

## 16. Explicit exclusions

Do not implement:

- Project Bootstrap / Onboarding;
- Project Registry creation or repository registration;
- creation of `.bridge/project.yaml`;
- frontend or dashboard;
- public REST or GraphQL API unless required by established repository conventions;
- MCP server or MCP tools;
- ChatGPT conversation memory;
- authentication, authorization, teams, organizations, or tenancy;
- workflow engine;
- task, issue, backlog, goal, or roadmap-management domain;
- background jobs, schedulers, or polling;
- webhook processing;
- repository-provider OAuth or App setup;
- deployment infrastructure;
- semantic search, embeddings, or vector database;
- automatic merge or direct writes to an integration branch;
- database-level Git emulation;
- speculative provider implementations beyond the replaceable boundary;
- Handoff Generator implementation.

## 17. Required automated tests

Codex must create comprehensive tests covering at least:

```text
test_select_active_registered_project
test_onboarding_incomplete_project_cannot_be_selected
test_get_active_project_without_selection_fails_clearly
test_project_context_isolated_between_projects
test_project_definition_is_loaded_from_registry_configuration
test_refresh_context_from_repository_boundary
test_refresh_reads_configured_akb_path
test_refresh_does_not_publish_or_snapshot
test_validate_valid_context
test_detect_stale_commit
test_detect_incomplete_project_definition
test_detect_unavailable_repository
test_detect_registry_definition_repository_conflict
test_detect_database_akb_sprint_conflict
test_detect_repository_akb_branch_conflict
test_conflict_is_not_silently_resolved
test_create_immutable_context_snapshot
test_compare_snapshot_with_current_context
test_publish_requires_valid_context
test_publish_renders_configured_current_state
test_publish_uses_branch_and_pull_request_boundary
test_project_state_events_are_recorded
test_same_services_support_multiple_project_definitions
```

Test names may differ, but every behaviour must be proven.

## 18. Mandatory acceptance scenarios

Codex must implement a repository-native executable acceptance suite or management command that runs these scenarios through canonical services.

### Scenario A — Select an onboarded Project

Given a registered Project with onboarding status ready and a valid Project definition:

Expected:

- the Project can be selected;
- selection is recorded;
- the Project definition is resolved;
- no Project-specific code path is used.

### Scenario B — Reject incomplete onboarding

Given a registered Project whose onboarding is incomplete:

Expected:

- active selection or context refresh is rejected;
- the error identifies onboarding as the missing prerequisite;
- Sprint 002 does not create missing onboarding artifacts.

### Scenario C — Load refreshed context

Use deterministic repository observations representing:

```text
repository available: true
branch: integration branch
open pull request: none
last accepted Sprint: previous Sprint
current Sprint: none
AKB agrees with repository facts
```

Expected:

- refresh persists observations;
- validation is `VALID`;
- load returns structured state;
- next action indicates Sprint planning or equivalent explicit rule.

### Scenario D — Detect stale commit and repair

Persist an older commit SHA, then return a newer repository HEAD.

Expected:

- validation becomes `STALE`;
- mismatch includes stored and observed SHAs;
- refresh updates stored state;
- revalidation becomes `VALID`.

### Scenario E — Detect Registry / Project-definition conflict

Represent different repository identities in Registry and Project definition.

Expected:

- validation becomes `CONFLICTED`;
- both identities and sources are returned;
- neither source is silently overwritten.

### Scenario F — Detect database / AKB Sprint conflict

Represent one current Sprint in operational state and a different Sprint in AKB.

Expected:

- validation becomes `CONFLICTED`;
- both values and sources are returned;
- a clear resolution-required result is produced.

### Scenario G — Detect repository / AKB branch conflict

Represent one branch and pull-request state in repository facts and another in AKB.

Expected:

- validation becomes `CONFLICTED`;
- actual repository observations remain available;
- AKB is not silently rewritten.

### Scenario H — Snapshot and compare

Create a snapshot with no active Sprint or pull request. Then refresh to a Sprint branch with an open pull request.

Expected comparison includes:

```text
branch: previous -> current
open PR: none -> present
current Sprint: none -> active Sprint
```

The original snapshot remains unchanged.

### Scenario I — Publish accepted AKB state

Use a `VALID` context and a deterministic fake repository publisher.

Expected:

- rendered content reflects structured context;
- target path comes from Project definition;
- a dedicated branch is requested;
- pull-request-oriented metadata is returned;
- `CONTEXT_PUBLISHED` is recorded only after success.

### Scenario J — Multi-Project isolation

Create two registered Projects with different Project definitions, repositories, AKB paths, and context.

Expected:

- the same generic services handle both;
- each load returns only the selected Project's data;
- no state or configuration leaks between Projects;
- no Project-specific conditional implementation exists.

## 19. Acceptance evidence

The acceptance suite must generate machine-readable evidence under the Sprint-specific evidence root resolved from the Project definition.

The report must include for every scenario:

- scenario identifier;
- run identifier;
- relevant inputs;
- expected outcome summary;
- actual outcome summary;
- PASS or FAIL;
- relevant created record identifiers or normalized values.

Do not store credentials, tokens, secrets, or environment-specific absolute paths.

## 20. Sprint-specific Release Gate additions

In addition to repository-wide Release Gates, Sprint 002 must prove:

```text
Project Registry integration tests                  PASS
Active Project selection tests                      PASS
Project-definition loading and drift tests          PASS
Repository boundary tests                           PASS
AKB parsing and normalization tests                  PASS
Context refresh and load tests                      PASS
Validation and conflict tests                        PASS
Snapshot immutability and comparison tests           PASS
Publish orchestration and rendering tests            PASS
Multi-Project isolation tests                        PASS
Executable acceptance scenarios A-J                  PASS
Machine-readable acceptance evidence generated       PASS
Closure report generated                             PASS
Evidence paths and final state consistent             PASS
```

Codex must repair and rerun until the complete Release Gate passes.

## 21. Required documentation

Create or update as required by the implementation:

- repository README with commands for tests, acceptance suite, and complete Release Gate;
- Project Context architecture documentation;
- AKB / current-state schema and publishing rules;
- canonical current-state document declared by the Project definition;
- Sprint closure report;
- machine-readable acceptance evidence;
- any existing Release Gate documentation affected by the change.

Documentation must not describe Bootstrap / Onboarding, Handoff Generator, MCP, frontend, live repository publishing, or other excluded capabilities as implemented.

## 22. Required closure report content

The closure report must include:

- final model and migration summary;
- reused Sprint 001 / onboarding components;
- public operation inventory;
- Project Registry and Project-definition integration description;
- repository boundary description;
- AKB parsing, validation, and publishing rules;
- context-state and precedence rules;
- output for every acceptance scenario;
- exact complete Release Gate command and result;
- proof that two differently configured Projects use the same services;
- proof that refresh did not publish automatically;
- proof that conflicts were not silently resolved;
- final branch and commit SHA.

## 23. Acceptance criteria

Sprint 002 is technically ready only when all are true:

- Sprint 001 onboarding components are reused;
- no parallel Project Registry or Project identity model is introduced;
- all Project-specific values are resolved from configuration and Execution Contract;
- Project selection works without introducing users or tenancy;
- multiple Projects remain isolated;
- context can be refreshed through a replaceable repository boundary;
- configured AKB paths are read and normalized;
- structured context can be loaded;
- `VALID`, `STALE`, `INCOMPLETE`, `CONFLICTED`, and `UNAVAILABLE` are correctly produced;
- stale state can be repaired through refresh;
- Registry, Project definition, repository facts, and AKB conflicts are explicit;
- conflicts are never silently resolved;
- immutable snapshots can be created and compared;
- explicit publishing renders accepted current state to the configured AKB path;
- operational refresh never writes to the repository;
- all required state events are recorded;
- the same implementation handles at least two differently configured Projects;
- all automated tests pass;
- all acceptance scenarios pass;
- evidence is repository-versioned at the resolved path;
- the complete Release Gate passes on the exact final state;
- documentation and AKB match the implementation;
- no excluded feature or speculative abstraction was added;
- final evidence is bound to the final branch and commit.

## 24. Allowed terminal states

Use only the terminal states declared by `AGENTS.md` and the execution workflow.

Ordinary technical failures are repair work and are not valid blockers.

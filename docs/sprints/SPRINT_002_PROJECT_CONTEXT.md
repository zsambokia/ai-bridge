# Sprint 002 — Project Context

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Target branch:** `sprint/002-project-context`  
**Integration target:** `main`  
**Task type:** FEATURE  
**Constitution mode:** FOUNDATION  
**Execution workflow:** `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`  
**Evidence path:** `docs/evidence/sprint-002-project-context/CLOSURE_REPORT.md`

## 1. Purpose

Implement the smallest reliable Project Context capability that allows AI Bridge to know which Project is selected, load its current operational state, refresh that state from GitHub, detect stale or conflicting context, create evidence snapshots, and publish accepted durable context back to the repository.

This sprint establishes Project Context as Bridge's working memory for one selected Project. It is not a project-management platform, workflow engine, dashboard, organization model, or generic knowledge system.

The sprint is complete only when Codex implements the capability, executes all mandatory acceptance scenarios, records real outputs, and passes the complete evidence-driven Release Gate.

## 2. Binding context

Read the mandatory context defined by `AGENTS.md` and the execution workflow.

In addition, inspect and use:

- `docs/architecture/DJANGO_FOUNDATION.md`;
- `docs/akb/CURRENT_STATE.md`;
- the existing Django project, models, settings, commands, tests, and Release Gate implementation;
- repository conventions established by Sprint 001.

If any listed file does not exist, assess the repository and use the canonical equivalent without inventing a parallel structure. Record the resolution in the closure report.

## 3. Business outcome

After this sprint, Bridge must be able to support this interaction reliably:

```text
User: Continue the AI Bridge project. Where are we?

Bridge:
- resolves the selected Project;
- loads its stored operational context;
- refreshes relevant repository facts from GitHub;
- validates whether stored and repository context agree;
- returns the current branch, repository state, sprint state, open PR state,
  last accepted milestone, and next actionable step;
- records evidence of the resolved state.
```

The capability must be usable by application services and future MCP or API layers, but this sprint must not implement MCP, external chat orchestration, or a frontend.

## 4. Architectural decision

Use a hybrid persistence model.

### 4.1 Database responsibility

The database is the operational source of truth for live, structured, frequently changing state, including:

- Project identity and status;
- repository association;
- selected or active Project;
- current branch and commit observations;
- current sprint and pull request observations;
- validation status;
- refresh timestamps;
- snapshots and state events.

### 4.2 GitHub responsibility

The repository is the durable, human-readable, reviewable source of truth for accepted knowledge, including:

- Constitution;
- approved sprint specifications;
- architecture and ADRs;
- accepted current state;
- closure evidence;
- material Product Owner decisions.

### 4.3 Prohibited duplication

Do not build a Git-like version-control system in the database.

Do not create a GitHub commit for every operational context refresh.

Publishing to GitHub occurs only through an explicit publish operation for accepted durable context.

## 5. Approved domain model

Implement the smallest coherent model set that satisfies the required behaviour. Expected responsibilities are listed below; exact class names may vary only when repository conventions require it.

### 5.1 Project

Required data:

- stable primary key;
- unique `slug`;
- human-readable `name`;
- optional description;
- status with at least active and archived states;
- created and updated timestamps.

Rules:

- project slug is unique;
- archived Projects remain queryable;
- normal deletion is not part of the public application contract;
- create and upsert operations must not create duplicates.

### 5.2 ProjectRepository

Required data:

- owning Project;
- repository provider, initially GitHub;
- repository owner and name, or a canonical full-name representation;
- default branch;
- primary-repository marker;
- created and updated timestamps.

Rules:

- one Project may support multiple repositories in the future;
- this sprint requires exactly one canonical primary repository per Project;
- the same GitHub repository must not be attached as the primary repository of multiple active Projects without an explicit documented reason;
- repository identity must be normalized before comparison.

### 5.3 ProjectContext

Stores the current operational context for a Project.

Required data or equivalent structured representation:

- Project reference;
- observed current or default branch;
- observed HEAD commit SHA;
- observed open pull request identifier when applicable;
- current sprint identifier or path when known;
- last completed sprint or accepted milestone when known;
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

### 5.4 ProjectContextSnapshot

Immutable evidence-oriented snapshot of resolved context.

Required data:

- Project reference;
- capture timestamp;
- repository identity;
- branch;
- commit SHA;
- sprint and PR observations;
- validation status;
- normalized context payload;
- source hashes or equivalent source identifiers where practical.

Snapshots must not change after creation.

### 5.5 ProjectStateEvent

Append-only audit event for material context operations.

Required event types must include at least:

```text
PROJECT_CREATED
PROJECT_UPDATED
PROJECT_ARCHIVED
REPOSITORY_ATTACHED
ACTIVE_PROJECT_SELECTED
CONTEXT_REFRESHED
CONTEXT_VALIDATED
CONTEXT_SNAPSHOT_CREATED
CONTEXT_PUBLISHED
```

Events must record timestamp, Project, event type, and structured metadata sufficient to understand the change.

## 6. Active Project scope

Bridge must support selecting one active Project for a caller or execution context.

Use the simplest repository-consistent persistence mechanism. In this sprint, an active Project may be stored globally or through a small singleton/application setting model if no authenticated user/session model exists yet.

Do not introduce authentication, multi-user ownership, tenancy, teams, organizations, or permission systems.

The implementation must isolate Projects. Selecting or loading one Project must never merge context from another Project.

## 7. Required application operations

Implement these operations as explicit application services. Public names may follow repository conventions, but responsibilities must remain distinct and testable.

### 7.1 Project operations

- `create_project`
- `get_project`
- `list_projects`
- `update_project`
- `upsert_project`
- `archive_project`

Required behaviour:

- create rejects conflicting unique identity;
- upsert resolves by canonical slug or repository identity and never duplicates the same Project;
- update modifies only declared fields;
- archive preserves history and removes the Project from default active listings;
- list supports at least active and archived filtering.

### 7.2 Active Project operations

- `select_active_project`
- `get_active_project`

Required behaviour:

- selecting an archived Project is rejected unless explicitly allowed by an internal administrative option;
- selecting a Project records `ACTIVE_PROJECT_SELECTED`;
- loading context without a resolvable active Project returns a clear domain error rather than silently choosing one.

### 7.3 Context operations

- `load_project_context`
- `refresh_project_context`
- `validate_project_context`
- `create_context_snapshot`
- `publish_project_context`

Internal supporting operations may include:

- repository context import;
- drift detection;
- event recording;
- source parsing and normalization.

Do not expose internal persistence helpers as public application operations unless necessary.

## 8. GitHub integration boundary

This sprint must define and implement a replaceable GitHub repository-context interface.

The domain/application layer must not depend directly on a concrete HTTP client throughout the codebase.

The integration must be capable of resolving at least:

- repository availability;
- default branch;
- branch HEAD SHA;
- open pull requests relevant to the Project;
- canonical context files when present;
- latest relevant merge or accepted state indicators needed by this sprint.

Tests must use deterministic fakes or mocks at the integration boundary. Acceptance scenarios must exercise the real application logic through the same canonical service path.

Real network access is not required for automated tests. The implementation must not require GitHub credentials to run the local Release Gate.

Do not implement OAuth, webhook ingestion, background synchronization, polling infrastructure, GitHub App installation flows, or MCP tools.

## 9. Repository context sources

When present, context refresh and validation must inspect the canonical repository documents relevant to current state, including:

- `docs/constitution/BRIDGE_CONSTITUTION.md`;
- `docs/akb/CURRENT_STATE.md`;
- the active sprint path when known;
- repository branch, commit, and PR metadata.

The parser must tolerate absent optional files and classify the context honestly as `INCOMPLETE` rather than fabricating values.

The implementation must not use hidden model memory as a source.

## 10. Context loading contract

`load_project_context` must return a structured result that includes at least:

```text
project identity
repository identity
active or observed branch
observed commit SHA
current sprint when known
last completed sprint or accepted milestone when known
open pull request when applicable
validation status
last refresh time
source summary
recommended next action or reason it cannot be derived
```

The recommended next action must be derived from explicit state rules, not free-form speculation.

Examples:

- no active sprint and no open PR after an accepted sprint → ready for sprint planning;
- active sprint branch and open PR → sprint implementation or review in progress;
- stale or conflicted context → refresh or Product Owner resolution required;
- repository unavailable → external input unavailable.

Keep the rule set small and documented.

## 11. Refresh contract

`refresh_project_context` must:

1. resolve the Project and primary repository;
2. retrieve repository facts through the canonical integration boundary;
3. parse available canonical context documents;
4. normalize the observed state;
5. update the current `ProjectContext` atomically;
6. record source metadata and refresh time;
7. record `CONTEXT_REFRESHED`;
8. return the refreshed structured context.

A refresh must not:

- create a GitHub commit;
- publish documentation;
- silently resolve material conflicts;
- create a snapshot unless explicitly requested;
- modify another Project.

## 12. Validation and drift contract

`validate_project_context` must compare stored operational state with currently observed repository state and canonical documents.

At minimum, detect:

- stored commit differs from repository branch HEAD → `STALE`;
- required repository or primary repository missing → `INCOMPLETE`;
- repository cannot be accessed → `UNAVAILABLE`;
- database current sprint materially disagrees with `CURRENT_STATE.md` → `CONFLICTED`;
- all required observations agree → `VALID`.

Conflict precedence must be explicit:

- do not silently overwrite one authoritative source with another;
- return the conflicting fields and values;
- preserve the last known data;
- require explicit refresh, publish, or Product Owner decision as appropriate.

Record `CONTEXT_VALIDATED` for every completed validation.

## 13. Snapshot contract

`create_context_snapshot` must:

- require a resolvable ProjectContext;
- capture the exact current normalized context;
- store an immutable snapshot;
- record `CONTEXT_SNAPSHOT_CREATED`;
- return the snapshot identifier and material captured values.

Provide an application-level comparison helper or equivalent tested behaviour that can identify material differences between a snapshot and current context, including branch, commit, PR, sprint, and validation status changes.

Do not build a generic visual diff system.

## 14. Publish contract

`publish_project_context` represents an explicit request to publish accepted durable state to GitHub.

For this sprint, implement the publishing boundary and deterministic behaviour without requiring live GitHub credentials in tests.

Publishing must:

1. require context status `VALID` unless an explicit internal override is documented and tested;
2. render an approved current-state document from structured context;
3. target the canonical current-state path, normally `docs/akb/CURRENT_STATE.md`;
4. use a dedicated branch and pull-request-oriented repository operation rather than writing directly to `main`;
5. return the planned or completed branch, commit, changed path, and pull request metadata;
6. record `CONTEXT_PUBLISHED` only after the publishing boundary reports success.

The rendering logic and application orchestration must be fully tested.

A real GitHub write is not required by the local Release Gate, but the integration contract must be concrete enough for the next GitHub service sprint to implement without changing Project Context domain behaviour.

## 15. Explicit exclusions

Do not implement:

- frontend or dashboard;
- REST API or GraphQL API unless a minimal internal endpoint already exists and is necessary for repository conventions;
- MCP server or MCP tools;
- ChatGPT conversation memory;
- authentication, authorization, users, teams, organizations, or tenancy;
- workflow engine;
- task, issue, backlog, roadmap, goal, or sprint-management domain;
- background jobs, Celery, schedulers, or polling;
- webhook processing;
- GitHub OAuth or GitHub App setup;
- generic connector framework;
- deployment infrastructure;
- semantic search, embeddings, or vector database;
- automatic merge or direct writes to `main`;
- database-level Git emulation;
- deletion of Projects with history;
- speculative multi-provider support beyond a small provider field and replaceable interface.

## 16. Required automated tests

Codex must create comprehensive tests covering at least:

```text
test_create_project
test_project_slug_is_unique
test_upsert_project_creates_when_missing
test_upsert_project_updates_without_duplicate
test_archive_project_preserves_history
test_select_active_project
test_archived_project_cannot_be_selected
test_get_active_project_without_selection_fails_clearly
test_project_context_isolated_between_projects
test_refresh_context_from_github_boundary
test_refresh_does_not_publish_or_snapshot
test_validate_valid_context
test_detect_stale_commit
test_detect_incomplete_context
test_detect_unavailable_repository
test_detect_database_github_sprint_conflict
test_conflict_is_not_silently_resolved
test_create_immutable_context_snapshot
test_compare_snapshot_with_current_context
test_publish_requires_valid_context
test_publish_renders_current_state
test_publish_uses_branch_and_pull_request_boundary
test_project_state_events_are_recorded
```

Test names may differ, but every behaviour must be proven.

Tests must verify persisted state, returned contracts, event records, and absence of prohibited side effects.

## 17. Mandatory acceptance scenarios

Codex must implement a repository-native executable acceptance suite or management command that runs the following scenarios through canonical application services.

The suite must create isolated test data, execute each scenario, print or persist structured actual outputs, and fail with a non-zero exit code when any scenario fails.

### Scenario A — Create Project and attach repository

Input:

```text
name: AI Bridge
slug: ai-bridge
repository: zsambokia/ai-bridge
default branch: main
```

Expected:

- one active Project exists;
- one primary repository is attached;
- expected creation and attachment events exist;
- returned identity is canonical.

### Scenario B — Repeated upsert does not duplicate

Execute the same repository upsert twice.

Expected:

- still exactly one Project;
- still exactly one primary repository;
- declared mutable fields are updated;
- no duplicate identity exists.

### Scenario C — Select and resolve active Project

Select AI Bridge and retrieve the active Project without passing its identifier again.

Expected:

- active Project is AI Bridge;
- selection event exists;
- no unrelated Project is selected.

### Scenario D — Load refreshed context

Use deterministic GitHub observations representing:

```text
repository: zsambokia/ai-bridge
branch: main
open PR: none
last completed sprint: Sprint 001
current sprint: none
repository available: true
```

Expected:

- context refresh persists the observations;
- validation is `VALID`;
- load returns the expected structured state;
- recommended next action is ready for Sprint 002 planning or equivalent documented rule.

### Scenario E — Detect stale context and repair by refresh

Persist an older commit SHA, then return a newer GitHub branch HEAD.

Expected:

- validation becomes `STALE`;
- mismatch includes stored and observed SHAs;
- refresh updates the stored SHA;
- revalidation becomes `VALID`.

### Scenario F — Detect DB and repository conflict

Represent database current sprint as Sprint 002 and `CURRENT_STATE.md` as Sprint 003.

Expected:

- validation becomes `CONFLICTED`;
- both values and sources are returned;
- neither value is silently discarded or overwritten;
- a clear resolution-required result is produced.

### Scenario G — Snapshot and compare

Create a snapshot on `main` with no open PR. Then refresh current context to a sprint branch with an open PR.

Expected comparison includes:

```text
branch: main -> sprint/002-project-context
open PR: none -> present
current sprint: none -> Sprint 002
```

The original snapshot remains unchanged.

### Scenario H — Publish accepted context

Use a `VALID` context and execute publish through a deterministic fake repository publisher.

Expected:

- rendered `CURRENT_STATE.md` content reflects structured context;
- target path is canonical;
- a dedicated branch is requested;
- pull-request-oriented metadata is returned;
- `CONTEXT_PUBLISHED` is recorded only after reported success.

### Scenario I — Project isolation

Create AI Bridge and SuperBI with different repositories and context.

Switch active Project between them.

Expected:

- each load returns only the selected Project's repository, branch, sprint, PR, and snapshot data;
- no state leaks between Projects.

### Scenario J — Archive behaviour

Archive SuperBI.

Expected:

- it remains queryable through archived filtering;
- it disappears from the default active list;
- it cannot be selected as active;
- its events and snapshots remain intact.

## 18. Acceptance evidence format

The acceptance suite must generate a machine-readable report under:

```text
docs/evidence/sprint-002-project-context/acceptance-results.json
```

or generate it into a temporary build directory and copy the final deterministic report to that path during sprint closure.

The report must include for every scenario:

- scenario identifier;
- execution timestamp or deterministic run identifier;
- relevant inputs;
- expected outcome summary;
- actual outcome summary;
- PASS or FAIL;
- relevant created record identifiers or normalized values.

Do not store credentials, tokens, secrets, or volatile environment-specific absolute paths.

## 19. Sprint-specific Release Gate additions

In addition to the repository-wide Release Gate and the minimum contract in `EVIDENCE_DRIVEN_SPRINT.md`, Sprint 002 must prove:

```text
Project domain migrations                           PASS
Project operation tests                             PASS
Active Project tests                                PASS
GitHub boundary tests                               PASS
Context refresh and load tests                      PASS
Validation and drift tests                          PASS
Snapshot immutability and comparison tests          PASS
Publish orchestration and rendering tests           PASS
Project isolation tests                             PASS
Executable acceptance scenarios A-J                 PASS
Acceptance results JSON generated                   PASS
Closure report generated                            PASS
Evidence paths and final state consistent            PASS
```

The canonical complete backend Release Gate command must execute the full test suite and the Sprint 002 acceptance suite in one reproducible invocation, directly or through a composed repository-native command.

Codex must repair and rerun until the complete command passes.

## 20. Required documentation

Create or update as required by the implementation:

- `README.md` — commands for migrations, tests, acceptance suite, and complete Release Gate;
- `docs/architecture/PROJECT_CONTEXT.md` — hybrid persistence decision, domain responsibilities, service boundaries, validation states, and explicit exclusions;
- `docs/akb/CURRENT_STATE.md` — exact state after Sprint 002 implementation;
- `docs/evidence/sprint-002-project-context/CLOSURE_REPORT.md`;
- acceptance evidence at the required path;
- any existing Release Gate documentation affected by the change.

Documentation must not describe MCP, frontend, live GitHub publishing, or other excluded capabilities as implemented.

## 21. Required closure report content

The closure report required by the execution workflow must additionally include:

- final model and migration summary;
- public application operation inventory;
- GitHub integration boundary description;
- context state and precedence rules;
- output for every acceptance scenario A-J;
- path and integrity summary for `acceptance-results.json`;
- exact complete Release Gate command and result;
- proof that Project isolation passed;
- proof that refresh did not publish automatically;
- proof that conflicts were not silently resolved;
- final branch and commit SHA.

## 22. Acceptance criteria

Sprint 002 is technically ready only when all are true:

- the approved domain models and migrations exist and are minimal;
- all required application operations work through one canonical path;
- active Project selection works without introducing users or tenancy;
- Project data and context are isolated;
- context can be refreshed through a replaceable GitHub boundary;
- context can be loaded as a structured result;
- `VALID`, `STALE`, `INCOMPLETE`, `CONFLICTED`, and `UNAVAILABLE` are correctly produced;
- stale state can be repaired through refresh;
- material conflicts are reported and never silently resolved;
- immutable snapshots can be created and compared;
- explicit publishing renders accepted current state and uses a branch/PR boundary;
- operational refresh never writes to GitHub;
- all required state events are recorded;
- all automated tests pass;
- acceptance scenarios A-J execute and pass;
- acceptance evidence is repository-versioned;
- the complete backend Release Gate passes on the exact final state;
- architecture, README, AKB, and evidence match the implementation;
- no excluded feature or speculative abstraction was added;
- final evidence is bound to the final branch and commit.

## 23. Allowed terminal states

Use only the terminal states declared by `AGENTS.md` and `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`.

Ordinary technical failures are repair work and are not valid blockers.

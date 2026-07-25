# Sprint 003 — Project Registry and Project Context Foundation

Status: APPROVED FOR CODEX EXECUTION

**Project:** AI Bridge
**Repository:** `zsambokia/ai-bridge`
**Required branch:** `main`
**Required baseline or descendant:** `395e5df305efd7130a6aa4f94d5a77022790b74b`
**Constitution:** `docs/constitution/BRIDGE_CONSTITUTION.md` (v1.1)
**Execution workflow:** `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`
**Execution Contract:** `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`
**Evidence path:** `docs/evidence/sprint-003-project-registry-and-context-foundation/`

## 1. Objective

A Bridge első kanonikus projekt-nyilvántartási és projektkörnyezet-alapjának
létrehozása úgy, hogy a repository statikus Project Definitionje
összekapcsolódjon a runtime Project Registryvel, majd ebből determinisztikusan
létrejöhessen az első validált Project Context.

The first real project registered by this capability is AI Bridge itself. The
Sprint must prove that Bridge can self-bootstrap from its own canonical
`.bridge/project.yaml`, create or update its own Registry record, derive
`READY` onboarding state, and create its first `VALID` Project Context without
hard-coded project-specific platform logic.

This Sprint replaces the unexecuted Sprint 002 Project Context specification.
It establishes the minimum prerequisite that Sprint 002 incorrectly assumed to
already exist; it does not revive or claim completion of that scope.

## 2. Binding architectural rules

- All Project-specific data must be resolved from the canonical
  `.bridge/project.yaml` Project Definition and its matching Registry record.
- Platform logic remains project-independent. Project-name, slug, repository,
  or technology-specific branches in platform code are forbidden.
- AI Bridge is the first bootstrap subject and acceptance proof, not a
  hard-coded special case. The same canonical operation must later be usable
  for another valid Project Definition.
- Reuse and extend existing Django Foundation components where they are
  canonical. Create a new responsibility only when the assessment proves it is
  absent.
- There is one canonical runtime Project Registry model and one canonical
  Project Context domain. Parallel `Project`, `RepositoryProject`,
  `RegisteredProject`, onboarding, or Context implementations are forbidden.
- The Project Definition is static configuration. Runtime state belongs in the
  Registry or Project Context and must not be written back to YAML.
- This first execution uses the constrained `BOOTSTRAP` Execution Contract.
  Later executions must use `STANDARD` only after a valid Project Context
  exists.

## 3. Scope

### A. Canonical runtime Project Registry

Create exactly one canonical runtime Project model with, at minimum:

- a stable project identifier;
- display name;
- repository full name;
- Project Definition path;
- lifecycle state;
- onboarding state;
- creation timestamp; and
- update timestamp.

The implementation must not introduce a parallel Project, RepositoryProject,
or RegisteredProject model. Any supporting service, command, or validation
code must operate on this canonical Registry record.

### B. Minimum onboarding readiness

Implement onboarding without a UI or multi-phase workflow. Its only statuses
are:

```text
PENDING
READY
INVALID
```

`READY` is permitted only when all of the following are true:

1. the Project Definition is available;
2. its schema is valid;
3. repository identity is unambiguous;
4. required governance documents are available; and
5. configured Release Gate commands are resolvable.

Any failed or missing prerequisite must produce `INVALID` or retain `PENDING`
only when validation cannot yet be completed. The result must identify the
specific condition.

### C. Canonical Project Definition loader and validator

Implement one canonical loader and validator for `.bridge/project.yaml`.
It must be the source for the Registry and onboarding inputs used by this
Sprint. Validation failures must be explicit and understandable.

The YAML remains static configuration and must not contain current Sprint,
branch state, Project Context status, active execution, or live capability
state. Those values are runtime state and belong in the appropriate runtime
model.

### D. Idempotent Registry bootstrap operation

Provide one canonical management command or application-service operation that:

1. loads the Project Definition;
2. validates it;
3. upserts the canonical Registry record;
4. derives onboarding readiness; and
5. returns an understandable, structured result for success and failure.

The command or service must support an explicit definition path, equivalent in
intent to:

```text
python manage.py bootstrap_project --definition .bridge/project.yaml
```

The exact command name and option syntax may follow repository conventions,
but the operation must be explicit, repeatable, testable, and usable without
manual database editing.

For this Sprint's end-to-end proof, running the operation against the
repository's own `.bridge/project.yaml` must register `zsambokia/ai-bridge` as
the first canonical project. This is a data-driven self-bootstrap, not a
fixture or hard-coded AI Bridge seed.

Repeated execution with the same valid definition must be idempotent: it may
update the same Registry record but must not create duplicates. Conflicting or
ambiguous repository identity must be rejected rather than silently creating a
second Project record.

### E. First canonical Project Context

Create the first canonical runtime Project Context domain, derived
deterministically from a `READY` canonical Registry record. At minimum it must
contain references or values for:

- Project identity;
- repository;
- Constitution;
- Roadmap;
- current Sprint document;
- AKB/current-state document;
- Release Gate configuration;
- validation status;
- source commit SHA; and
- creation time.

It is not necessary to copy full stable documents when a stable reference and
the relevant SHA provide the required deterministic provenance. Project Context
is runtime data, not static YAML configuration.

The Sprint's first Context must belong to the AI Bridge Registry record created
from the repository's own Project Definition. Its source commit SHA and source
references must be observable in implementation evidence.

### F. Project Context validation and freshness

Project Context validation statuses are exactly:

```text
VALID
INVALID
STALE
```

`VALID` requires every required source to be available and valid for the
derived Context. An invalid or unavailable source produces `INVALID`. A
Context is `STALE` when its recorded base/source commit differs from the
current canonical repository state. Validation must make the reason observable.

### G. BOOTSTRAP execution boundary

This Sprint is the first use of `BOOTSTRAP`. No prior Project Context exists.
The operation is permitted only after the Registry exists, the Definition is
valid, onboarding is `READY`, repository and execution branch are unambiguous,
and this approved Sprint is available. By Sprint completion there must be a
`READY` Registry record for AI Bridge and a `VALID` first Project Context for
that same project. The next execution must use `STANDARD`; `BOOTSTRAP` is not a
reusable bypass.

## 4. Explicit exclusions

This Sprint must not implement:

- UI, dashboard, or onboarding wizard;
- GitHub API integration;
- Codex launch or execution orchestration;
- Handoff Generator implementation;
- Goal system, workflow engine, or capability engine;
- multi-project authorization, organization, or tenant capabilities;
- automatic AKB publication;
- production deployment; or
- parallel branch management.

Do not create a separate bootstrap Sprint, a new Project Registry implementation
beside the canonical one, or a parallel onboarding model.

## 5. Required acceptance scenarios

The implementation must provide executable evidence for each scenario:

1. A valid Project Definition loads and validates.
2. An invalid Project Definition is rejected with an understandable result.
3. Running the canonical bootstrap against the repository's own
   `.bridge/project.yaml` creates the AI Bridge Registry record and its first
   Project Context.
4. The created AI Bridge Registry record has repository identity
   `zsambokia/ai-bridge` and reaches onboarding state `READY` only after every
   required validation passes.
5. The first AI Bridge Project Context is `VALID`, records the source commit
   SHA, and exposes the required source references.
6. Repeating the bootstrap operation is idempotent and updates or reuses the
   same AI Bridge Registry record rather than creating a duplicate.
7. Duplicate or ambiguous repository identity cannot create duplicate Registry
   records.
8. A Project Context can be created only for a `READY` Project.
9. The Context contains every required source reference/value listed in this
   specification.
10. A Context with all valid available sources is `VALID`.
11. A differing current canonical commit makes the Context `STALE`.
12. An invalid or unavailable required source makes the Context `INVALID`.
13. The bootstrap implementation contains no hard-coded AI Bridge-only branch;
    a second valid test Project Definition can pass through the same canonical
    loader and bootstrap service.

## 6. Required implementation evidence

The closure report must prove, with commands and results bound to the final
`main` commit:

- the data model and migration;
- the bootstrap command or canonical application service;
- Project Definition validation;
- the exact self-bootstrap command used for `.bridge/project.yaml`;
- the created AI Bridge Registry record, including stable identifier,
  repository identity, and `READY` onboarding state;
- the created first AI Bridge Project Context, including `VALID` status, source
  commit SHA, and required source references;
- proof that a repeated bootstrap did not create a duplicate Registry record;
- all required tests and acceptance scenarios; and
- the complete repository Release Gate.

Update `docs/akb/CURRENT_STATE.md` and every affected contract, architecture,
or roadmap document to describe only the implemented final state. Do not mark
future capability work as complete.

## 7. Execution and publication rules

Apply the Evidence-Driven Sprint Workflow in full. Work directly on `main`:

- do not create or require a sprint branch;
- do not require a pull request;
- do not rewrite shared history;
- commit and push only after all required Release Gates pass; and
- correct any problem with a new repair or revert commit.

Before implementation, perform the required assessment and record what was
reused, extended, or newly created. The final evidence must bind the exact
final `main` commit SHA.

## 8. Completion criteria

Sprint 003 is ready for Product Owner review only when the canonical Registry,
onboarding readiness, Project Definition integration, and first validated
Project Context are implemented and proven according to every acceptance
scenario and Release Gate above. The proof must show that AI Bridge was
successfully self-bootstrapped from its own `.bridge/project.yaml`. No excluded
capability may be represented as implemented.

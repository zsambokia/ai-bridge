# Architecture Review — Sprint 002: Project Context

**Status:** BLOCKED — BUSINESS DECISION REQUIRED

**Reviewed branch:** `sprint/002-project-context`

**Reviewed baseline:** `c4e7525bcc74ee37e85f07ab29e29e587e012451`

## Review scope

This review replaces the earlier, untracked review made on the Sprint 001
checkout. Its conclusions are based only on the canonical Sprint 002 branch.

The following sources were reviewed together:

- `AGENTS.md`
- `docs/constitution/BRIDGE_CONSTITUTION.md`
- `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`
- `.bridge/project.yaml`
- `docs/roadmap/ROADMAP.md`
- `docs/sprints/SPRINT_002_PROJECT_CONTEXT.md`
- `docs/akb/CURRENT_STATE.md`
- `docs/workflow/EVIDENCE_DRIVEN_SPRINT.md`

## Baseline integration record

**Product Owner decision:** Sprint 002 must reuse the accepted Sprint 001
baseline and must not create a parallel Project Registry or onboarding model.

**Source commit selected for integration:**
`413487b5e7bf4cc4fee0cd2472a00855ead30992`
(`sprint/001-django-foundation`, `feat: establish Django foundation`).

**Target before integration:**
`c4e7525bcc74ee37e85f07ab29e29e587e012451`
(`sprint/002-project-context`).

The review file was intentionally kept untracked during the integration so that
no existing work was overwritten.

**Integration result:** merge commit
`159e938b522875a84c415fb300d63e887d9de6d7` incorporates the source baseline
into the Sprint 002 branch. The only merge conflict was in `AGENTS.md`; its
newer contract-first, Project-definition-driven rules were retained because
they are required by the Sprint 002 governance documents.

**Product Owner decision on Contract bootstrap:** introduce the explicit
`BOOTSTRAP` and `STANDARD` contract modes. `BOOTSTRAP` is limited to the
first-Project-Context execution and does not permit Registry or onboarding
creation in Sprint 002.

## Consistent findings

- The approved Constitution, handoff contract, Project Definition, roadmap,
  and Sprint 002 specification are present on this branch.
- The Project Definition is the declared source of project-specific identity,
  repository, path, evidence, and release-gate configuration.
- Sprint 002 requires a project-independent implementation and prohibits
  project-name or slug based platform branching.
- The Sprint 002 specification correctly limits its scope to Project Context;
  it explicitly excludes Project Bootstrap, onboarding, Project Registry
  creation, and repository registration.

## Material blockers

### 1. Required Project Registry and onboarding baseline is absent

Sprint 002 requires a registered project with ready onboarding before work can
begin. It also requires reuse of the canonical Project Registry model allegedly
created by Sprint 001, while explicitly prohibiting creation of a parallel
Project model, Project Registry, or onboarding flow.

The current repository baseline does not contain that reusable implementation:

- `docs/akb/CURRENT_STATE.md` records the accepted state as Django Foundation
  only, with no domain models, workflows, or external integrations.
- `pyproject.toml` and the tracked Django packages contain the foundation
  application only; there is no Project Registry model or migration.
- No tracked application code or migration implements repository registration
  or onboarding.

This conflicts with `.bridge/project.yaml`, which declares
`database_record_required: true`, `onboarding_status: ready`, and
`capabilities.project_registry: true`, because the required canonical runtime
implementation and evidence are not present in this baseline. Sprint 002 is
not authorized to create the missing prerequisite itself.

### 2. Resolved: the first Project Context had a circular Execution Contract prerequisite

Originally, `AGENTS.md`, `.bridge/project.yaml`, the handoff contract, and
Sprint 002 required an issued, validated Execution Contract before a governed
run started, while the contract required Project Context status `VALID`.

Sprint 002 creates the first minimal Project Context, so those prior rules were
circular. The Product Owner decision is now implemented consistently in the
handoff contract and Sprint 002 specification: a `BOOTSTRAP` Contract may be
issued only for this one first-context purpose after Registry, definition,
onboarding, repository, branch, and Sprint eligibility have been proved. It
records `NOT_CREATED` rather than requiring a prior valid Context. `STANDARD`
remains mandatory once a valid Context exists.

An actual issued `BOOTSTRAP` Contract still cannot be produced until blocker 1
is resolved; its Registry and onboarding prerequisites remain mandatory.

## Non-blocking observation

`docs/akb/CURRENT_STATE.md` describes the previously accepted Sprint 001
branch. It is stale relative to this checkout, but that is an expected
`INCOMPLETE` AKB input for Sprint 002 to assess and later publish; it is not a
reason to alter it during this preflight.

## Remaining required decision

The merged accepted Sprint 001 commit does not contain the Registry/onboarding
implementation that the Product Owner decision expects it to provide. The only
scope-compliant resolution is to provide the actual accepted source commit or
branch containing the Project Bootstrap/onboarding/Project Registry
implementation, its migrations, tests, and evidence, so it can be merged into
this baseline. If no such accepted source exists, the Product Owner must
explicitly revise the current constraints before implementation can continue;
Sprint 002 cannot create this missing foundation.

After the required accepted baseline is available, issue a validated
`BOOTSTRAP` Execution Contract for it and rerun this review. Until then,
implementing a registry or an ad-hoc onboarding model inside Sprint 002 would
violate the approved Sprint scope and the Constitution's contract-first rules.

## Decision

Sprint 002 implementation has not started. The baseline merge and contract
policy documentation are complete, but the review remains blocked because the
required reusable Registry/onboarding implementation is still absent. No Sprint
002 Django application code, models, migrations, dependencies, Node.js prototype
files, or future-roadmap features were changed.

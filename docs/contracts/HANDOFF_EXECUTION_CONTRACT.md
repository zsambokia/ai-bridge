# Handoff Generator / Execution Contract

**Status:** CANONICAL PLATFORM SPECIFICATION  
**Applies to:** every governed Codex implementation, repair, migration, recovery, release, and self-development execution  
**Project configuration source:** `.bridge/project.yaml` or an equivalent Project Registry record  
**Execution workflow:** resolved from the selected Project definition

## 1. Purpose

The Handoff Generator produces the complete, deterministic Execution Contract required to start a governed Codex run safely and consistently.

The generated handoff connects four separate concerns:

- Project Registry: what the Project is and how it is configured;
- Project Context: where the Project currently stands;
- approved Sprint: what must be implemented;
- execution workflow: how implementation, testing, evidence, and closure must be performed.

The contract binds the exact inputs for one execution. It does not define project-specific business scope and it does not replace the Sprint.

## 2. Platform rule

The Handoff Generator and Execution Contract are platform-level capabilities.

They must not contain hard-coded Project names, repository names, branch names, technology stacks, sprint numbers, document paths, Release Gate commands, or evidence paths.

Every project-specific value must be resolved from:

1. the selected Project Registry record;
2. its canonical project definition;
3. for `STANDARD`, a validated Project Context snapshot; or, for `BOOTSTRAP`,
   the approved first-Project-Context execution eligibility;
4. the explicitly approved Sprint.

No valid Project definition or approved Sprint means no implementation start. The
Project Context requirement is mode-specific as defined in section 3.1.

## 3. Core execution rule

Codex must never infer the active Project, repository, Sprint, execution baseline, target branch, roadmap milestone, or Release Gate from branch names, filenames, issues, pull requests, comments, chat history, or model memory.

Every governed run must begin from one validated and issued Execution Contract.

### 3.2 Main-only development execution

While the Product Owner-approved main-only development policy is active, the
contract must resolve both `target_branch` and `integration_target` to `main`.
The executor may commit and push directly only after all required Release Gates
pass. A pull request is optional; the final evidence must record the resulting
`main` commit SHA. A failed or superseded change is corrected by a new revert or
repair commit, not shared-history rewriting.

### 3.1 Contract modes

Every contract has exactly one mode:

```text
BOOTSTRAP
STANDARD
```

`STANDARD` is required for ordinary and all subsequent governed executions. It
requires Project Context status `VALID` and an immutable snapshot belonging to
the selected Project.

`BOOTSTRAP` is a narrow, one-time mode for the approved execution whose sole
purpose is creation of that Project's first Project Context. It may be issued
only when all of the following are true:

- the Project Registry record exists;
- the Project definition is valid and consistent with that record;
- onboarding status is ready;
- repository identity and execution branch are unambiguous;
- the approved Sprint specification is available and explicitly targets the
  first Project Context;
- no valid Project Context exists for the selected Project; and
- the execution intent is limited to creating that first Project Context.

`BOOTSTRAP` does not require a pre-existing `VALID` Project Context or context
snapshot. It must not be used to bypass prerequisites for a later Sprint,
repair an invalid Context, or perform ordinary execution. Once a valid Project
Context exists, only `STANDARD` may be issued for that Project.

## 4. Responsibilities

The Handoff Generator must:

1. resolve the active Project from the Project Registry;
2. load and validate the Project definition;
3. for `STANDARD`, load and validate Project Context;
4. for `STANDARD`, create or resolve an immutable Project Context snapshot;
   for `BOOTSTRAP`, prove and record first-Project-Context eligibility;
5. resolve the exact target repository and integration branch;
6. resolve the exact approved Sprint path;
7. resolve the Constitution and execution workflow declared by the Project;
8. resolve required architecture, AKB, roadmap, and additional context paths;
9. resolve the baseline commit or descendant requirement;
10. resolve repository-wide and Sprint-specific Release Gates;
11. resolve deterministic evidence output paths;
12. validate cross-document consistency;
13. generate a unique handoff identifier;
14. generate a reproducible contract hash;
15. emit machine-readable and human-readable representations;
16. refuse issuance when a material ambiguity or conflict remains.

## 5. Non-responsibilities

The Handoff Generator must not:

- implement a Sprint;
- modify application code;
- create or approve a Sprint;
- select a Sprint based on guesswork or roadmap order alone;
- create missing Project policy without authorization;
- silently repair Project Registry, Project Context, AKB, Sprint, or repository conflicts;
- execute Release Gates;
- merge pull requests;
- create Product Owner decisions;
- replace Project Context;
- replace the execution workflow;
- become a project-specific prompt template.

## 6. Project Registry and Project Definition

The Project Registry identifies Projects available to the platform.

A Project definition provides repository-specific configuration without creating a separate workflow implementation.

The canonical repository-local definition should normally be:

```text
.bridge/project.yaml
```

The Project Registry may store the same configuration in a database. When both database and repository definitions exist, the platform must define precedence and detect drift. It must not silently merge contradictory values.

The Project definition may declare:

- Project identity;
- repository provider and canonical repository identity;
- default and integration branches;
- governance and workflow document paths;
- Sprint, architecture, roadmap, AKB, and evidence roots;
- technology profile;
- repository-wide Release Gate commands;
- static supported-feature configuration and policies.

Lifecycle, onboarding, Project Context validation, and accepted capability state
are runtime values. They belong in the canonical Registry, Project Context, or
a future operational-state domain; they must not be written into the static
Project Definition.

## 7. Required request input

The generator requires at least:

```text
PROJECT_IDENTIFIER
EXECUTION_INTENT
REQUESTED_TASK_TYPE
REQUESTED_SPRINT_IDENTIFIER_OR_PATH
REQUESTED_TARGET_BRANCH
REQUESTED_INTEGRATION_TARGET
REQUESTED_BY
```

Some values may be resolved from a validated Project Registry record and Project Context, but the approved Sprint must always resolve to one exact repository path.

## 8. Supported task types

At minimum:

```text
FEATURE
BUGFIX
MIGRATION
RECOVERY
DOCUMENTATION
RELEASE
SELF_DEVELOPMENT
ONBOARDING
```

Task type may select additional gates or constraints, but it must never weaken governance or evidence requirements.

## 9. Canonical machine-readable schema

The generated contract must contain at least:

```yaml
contract_version: "1.0"
handoff_identifier: "bridge:<project-slug>:<sprint-id>:<unique-run-id>"
contract_mode: "BOOTSTRAP | STANDARD"
generated_at: "ISO-8601 timestamp"
generated_by: "canonical handoff generator"
requested_by: "product owner or authorized caller"

project:
  id: "stable registry identifier"
  slug: "project slug"
  name: "project name"
  definition_source: ".bridge/project.yaml or registry source"
  definition_version: "content hash or registry version"
  onboarding_status: "PENDING | READY | INVALID"
  context_status: "VALID | INVALID | STALE | NOT_CREATED"
  context_snapshot_id: "immutable snapshot identifier or null only for BOOTSTRAP"

execution:
  task_type: "resolved task type"
  intent: "approved execution intent"
  target_repository: "provider-specific canonical identity"
  target_branch: "resolved branch"
  integration_target: "resolved integration branch"
  baseline_commit: "full commit SHA"
  baseline_rule: "EXACT | DESCENDANT_OF"
  worktree_policy: "MAIN_ONLY"

binding_documents:
  agents_path: "resolved path"
  constitution_path: "resolved path"
  constitution_version: "content hash"
  workflow_path: "resolved path"
  workflow_version: "content hash"
  approved_sprint_path: "resolved exact Sprint path"
  sprint_version: "content hash"
  roadmap_path: "resolved optional Project roadmap path"
  akb_paths:
    - "resolved AKB or current-state paths"
  additional_context_paths:
    - "resolved architecture or Sprint-required context paths"

release_gates:
  repository_wide:
    - id: "stable gate id"
      command: "resolved repository-native command"
  sprint_specific:
    - id: "Sprint-specific gate id"
      command: "resolved command or acceptance suite"
  complete_gate_command: "resolved composed command when available"

evidence:
  root_path: "resolved Project evidence root"
  closure_report_path: "deterministic Sprint-specific path"
  machine_results_paths:
    - "deterministic machine-readable evidence path"
  required_final_commit_binding: true

allowed_terminal_states:
  - "PASS — READY FOR PRODUCT OWNER REVIEW"
  - "BLOCKED — BUSINESS DECISION REQUIRED"
  - "BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE"

constraints:
  preserve_unrelated_work: true
  direct_write_to_integration_target: true
  infer_active_project: false
  infer_active_sprint: false
  roadmap_authorizes_execution: false
  scope_expansion: false
  ordinary_technical_failure_is_blocker: false

integrity:
  source_project_context_snapshot: "snapshot identifier"
  repository_head_at_generation: "full commit SHA"
  project_definition_hash: "deterministic digest"
  contract_hash: "deterministic digest over normalized contract"
```

Exact field names may follow implementation conventions, but all responsibilities and invariants must remain represented and testable.

## 10. Contract invariants

A contract is valid only when all common invariants are true:

- the selected Project is unambiguous;
- the Project is registered;
- the Project definition is valid;
- the Project definition and Registry record do not materially conflict;
- repository identity matches the Project definition;
- target branch and integration target are explicit;
- the baseline commit exists in the target repository;
- the approved Sprint document exists;
- Sprint status permits Codex execution;
- the Sprint belongs to the selected Project;
- Constitution and workflow documents are readable;
- mandatory additional context paths exist or have an explicitly approved equivalent;
- required Release Gates can be resolved;
- evidence paths are deterministic and collision-free;
- allowed terminal states exactly match platform governance;
- roadmap direction does not contradict the approved Sprint;
- no material contradiction exists between Project definition, Project Context, AKB, Sprint, and repository state;
- the normalized contract hash can be reproduced.

In addition, mode-specific invariants apply:

- `STANDARD` requires Project Context status `VALID` and a context snapshot
  belonging to the selected Project, and repository identity matching that
  Project Context;
- `BOOTSTRAP` requires every condition in section 3.1, records
  `context_status: NOT_CREATED`, has no context snapshot, and binds only the
  approved first-Project-Context execution; its repository identity must match
  the selected Project Registry record and Project definition.

## 11. Roadmap rule

The roadmap is project-specific and may describe goals, milestones, sequencing, dependencies, and planned capabilities.

The roadmap does not authorize implementation.

Only an explicitly approved Sprint may authorize a Codex execution. The Handoff Generator may validate that the Sprint is consistent with the roadmap, but it must not infer or approve a Sprint from roadmap order.

## 12. Contract lifecycle

Allowed lifecycle states:

```text
DRAFT
VALIDATED
ISSUED
CONSUMED
COMPLETED
SUPERSEDED
REVOKED
```

Rules:

- `DRAFT` cannot start execution;
- `VALIDATED` has passed all pre-issuance checks;
- `ISSUED` is immutable and may start one governed execution;
- `CONSUMED` means the execution acknowledged the contract and started preflight;
- `COMPLETED` links to final evidence and closure state;
- `SUPERSEDED` points to a replacement contract generated after binding inputs changed;
- `REVOKED` cannot be consumed.

After issuance, binding fields are immutable. Any change requires a new handoff identifier and contract hash.

## 13. Contract invalidation

An issued contract becomes stale or invalid when a binding input changes materially before execution begins, including:

- Project definition changes;
- Registry identity changes;
- approved Sprint content changes;
- Constitution or workflow changes;
- target repository HEAD violates the baseline rule;
- active Project changes;
- Project Context is no longer `VALID` (for example, it is `STALE` or `INVALID`);
- target branch or integration target changes;
- required Release Gates change;
- evidence paths collide;
- the contract is revoked or superseded.

Codex must stop before mutation when integrity validation fails.

## 14. Generator validation flow

```text
RESOLVE REQUEST
→ RESOLVE PROJECT REGISTRY RECORD
→ LOAD PROJECT DEFINITION
→ VALIDATE REGISTRY / DEFINITION CONSISTENCY
→ RESOLVE CONTRACT MODE
→ [STANDARD: LOAD / REQUIRE VALID CONTEXT / CREATE OR RESOLVE SNAPSHOT]
→ [BOOTSTRAP: VERIFY FIRST-CONTEXT ELIGIBILITY / RECORD NOT_CREATED]
→ RESOLVE REPOSITORY AND BASELINE
→ RESOLVE APPROVED SPRINT
→ RESOLVE GOVERNANCE DOCUMENTS
→ RESOLVE ROADMAP, AKB, AND ADDITIONAL CONTEXT
→ RESOLVE RELEASE GATES
→ RESOLVE EVIDENCE PATHS
→ CHECK CROSS-DOCUMENT CONSISTENCY
→ NORMALIZE CONTRACT
→ CALCULATE CONTRACT HASH
→ VALIDATE INVARIANTS
→ ISSUE CONTRACT
```

No step may silently downgrade a conflict into a warning.

## 15. Human-readable handoff

The generator must render a concise handoff derived entirely from the machine-readable contract:

```text
CODEX EXECUTION CONTRACT

HANDOFF_IDENTIFIER: <resolved identifier>
PROJECT: <resolved Project name and slug>
TASK_TYPE: <resolved task type>
CONTRACT_MODE: <BOOTSTRAP | STANDARD>
TARGET_REPOSITORY: <resolved repository identity>
TARGET_BRANCH: <resolved target branch>
INTEGRATION_TARGET: <resolved integration branch>
BASELINE_COMMIT: <full SHA>
BASELINE_RULE: <resolved rule>

PROJECT_DEFINITION: <resolved definition source>
CONSTITUTION_PATH: <resolved path>
WORKFLOW_PATH: <resolved path>
APPROVED_SPRINT_PATH: <resolved exact path>
ROADMAP_PATH: <resolved optional path>
AKB_PATHS:
- <resolved AKB path>
ADDITIONAL_CONTEXT_PATHS:
- <resolved path>

REQUIRED_RELEASE_GATES:
- <resolved gate>

EVIDENCE_PATH:
<resolved closure report path>

ALLOWED_TERMINAL_STATES:
- PASS — READY FOR PRODUCT OWNER REVIEW
- BLOCKED — BUSINESS DECISION REQUIRED
- BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE

CONTRACT_HASH: <digest>
```

The human-readable form must not be independently editable.

## 16. Storage and audit

Issued contracts must be stored as immutable execution records in the operational database or equivalent durable store.

A sanitized repository copy may be published when evidence policy requires it, using a deterministic evidence path resolved from the Project definition.

The execution record must retain:

- Project Registry identity;
- Project definition version;
- source Project Context snapshot;
- normalized contract payload;
- contract hash;
- lifecycle transitions;
- issuing actor;
- consuming execution identity;
- final evidence links;
- final closure state.

Secrets and credentials must never be embedded in a contract.

## 17. Required application operations

Implement or reserve these canonical platform operations:

- `generate_execution_contract`
- `validate_execution_contract`
- `issue_execution_contract`
- `get_execution_contract`
- `render_execution_handoff`
- `consume_execution_contract`
- `complete_execution_contract`
- `supersede_execution_contract`
- `revoke_execution_contract`

Project-specific branches must never exist inside these operations. Behaviour differences must come from Project configuration and approved Sprint inputs.

## 18. Domain errors

At minimum:

```text
PROJECT_NOT_REGISTERED
PROJECT_DEFINITION_MISSING
PROJECT_DEFINITION_INVALID
PROJECT_REGISTRY_DEFINITION_CONFLICT
NO_ACTIVE_PROJECT
PROJECT_CONTEXT_NOT_VALID
REPOSITORY_MISMATCH
BASELINE_NOT_RESOLVED
SPRINT_NOT_FOUND
SPRINT_NOT_APPROVED
SPRINT_PROJECT_MISMATCH
BINDING_DOCUMENT_MISSING
BINDING_DOCUMENT_CONFLICT
RELEASE_GATE_NOT_RESOLVED
EVIDENCE_PATH_COLLISION
CONTRACT_INTEGRITY_FAILURE
CONTRACT_ALREADY_CONSUMED
CONTRACT_REVOKED
CONTRACT_SUPERSEDED
```

Errors must be structured and identify the smallest safe resolution action.

## 19. Security and safety requirements

- never include tokens, passwords, private keys, or secret environment values;
- preserve unrelated working-tree changes;
- require explicit authorization for destructive or production-risk operations;
- bind execution to exact Project, repository, and baseline identities;
- prevent contract reuse across Projects or repositories;
- require contract hash verification before Codex mutation;
- log lifecycle events without logging secrets;
- do not allow arbitrary caller input to weaken terminal-state or Release Gate requirements.

## 20. Relationship between platform components

```text
PROJECT REGISTRY + PROJECT DEFINITION
                 ↓
          PROJECT CONTEXT
                 ↓
     IMMUTABLE CONTEXT SNAPSHOT
                 ↓
       EXECUTION CONTRACT
                 ↓
AGENTS + CONSTITUTION + WORKFLOW + SPRINT
                 ↓
          CODEX EXECUTION
                 ↓
       RELEASE GATES + EVIDENCE
                 ↓
        PRODUCT OWNER REVIEW
```

Project Registry answers:

> What is this Project and how is it configured?

Project Context answers:

> Where does this Project currently stand?

The approved Sprint answers:

> What exact Project-specific capability must be delivered now?

The Execution Contract answers:

> What exact immutable package may Codex use for this governed run?

## 21. Minimum implementation acceptance scenarios

A future implementation Sprint must prove at least:

- valid contract generation for a registered Project;
- failure for an unregistered Project;
- failure for missing or invalid Project definition;
- detection of Registry and repository definition drift;
- failure for absent active Project;
- `STANDARD` failure for every non-`VALID` Project Context state;
- `BOOTSTRAP` issuance only for an onboarded registered Project with no valid
  Context and an approved first-Project-Context Sprint;
- `BOOTSTRAP` rejection when a valid Context already exists or the requested
  execution is not the first-Project-Context creation;
- failure for missing or unapproved Sprint without Sprint inference;
- exact repository baseline binding;
- document and Project-definition hash binding;
- immutable issuance and supersession;
- Project isolation;
- single-consumption protection;
- exact machine-to-human rendering;
- final evidence and commit binding;
- secret exclusion;
- proof that the same generator handles at least two differently configured Projects without project-specific code paths.

## 22. Definition of ready for implementation

The Handoff Generator is ready for implementation when:

- a Project Registry and canonical Project definition schema are accepted;
- Project onboarding/bootstrap can create a valid registry entry and definition;
- Project Context is available and proven;
- the repository's Sprint approval marker is defined;
- repository-wide Release Gates can be resolved from Project configuration;
- persistence and lifecycle event conventions are available;
- the Product Owner approves a dedicated implementation Sprint.

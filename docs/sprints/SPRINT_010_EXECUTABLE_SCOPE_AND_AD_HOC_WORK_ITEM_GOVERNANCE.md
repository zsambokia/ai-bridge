# Sprint 010 — Executable Scope, Work Item Governance, and AI Bridge Contract Authority

**Status:** APPROVED FOR IMPLEMENTATION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Primary outcome:** Replace the mandatory-Sprint execution assumption with a governed executable-scope model and make AI Bridge the authoritative issuer and lifecycle owner of Execution Contracts. Execution providers such as Codex must consume an already issued contract rather than authorizing themselves.

## 1. Problem statement

The current governed execution flow requires every contract to resolve one exact approved Sprint. This causes two related problems.

First, small or ad hoc Product Owner requests can be attached to an unrelated or already closed Sprint. The first ChatGPT external acceptance attempt demonstrated this failure mode: a standalone README documentation task was classified as a `TASK`, but its execution context and evidence root were still derived from the already closed Sprint 009.

Second, the responsibility boundary between governance and execution is incomplete. Codex currently expects an approved Sprint and an issued contract before mutation, but the operating flow can still implicitly expect the executor to prepare or issue the contract that authorizes its own work. This creates a bootstrap ambiguity and weakens separation of duties.

The target architecture must therefore solve both issues:

- ad hoc work must receive its own approved Work Item scope;
- closed Sprint history and evidence must remain immutable;
- AI Bridge must classify, validate, approve, generate, validate, issue, and retain the authoritative Execution Contract;
- Codex and other execution providers must only validate, consume, execute, report evidence, and complete the issued contract;
- the executor must never issue its own authorization.

## 2. Product Owner decisions

### 2.1 Canonical planning and execution hierarchy

```text
PROJECT
│
├── INITIATIVE / MILESTONE        optional planning container
│   └── EPIC                      optional multi-sprint outcome
│       └── SPRINT                optional coherent implementation increment
│           └── WORK ITEM         executable unit
│               └── SUBTASK       optional internal decomposition
│
└── AD HOC WORK ITEM              executable project-level unit
    └── SUBTASK                    optional internal decomposition
```

Every repository mutation requires exactly one approved executable scope, but not every mutation requires a Sprint.

Allowed executable scope kinds:

```text
SPRINT
WORK_ITEM
```

Planning-only scope kinds:

```text
INITIATIVE
MILESTONE
EPIC
```

A Subtask is not independently governed by default and does not receive a separate Execution Contract unless repository boundary, authorization, risk, or independent approval requires it.

### 2.2 Canonical authority boundary

AI Bridge is the **Contract Authority**.

An execution provider such as Codex is an **Execution Provider**.

```text
Product Owner
    │
    ▼
AI Bridge
    ├── request interpretation
    ├── scope classification proposal
    ├── deterministic policy resolution
    ├── Sprint or Work Item approval binding
    ├── Execution Context generation
    ├── contract generation
    ├── contract validation
    ├── contract issuance
    └── authoritative audit and lifecycle state
    │
    ▼
Execution Provider
    ├── fetch issued contract
    ├── independently validate integrity and eligibility
    ├── consume contract
    ├── execute bounded work
    ├── run required gates
    ├── produce evidence
    └── submit completion result
    │
    ▼
AI Bridge
    ├── validate completion evidence
    ├── bind final commit and results
    └── complete or reject the contract
```

The execution provider must not:

- approve its own scope;
- issue its own Execution Contract;
- broaden the approved outcome;
- replace the authoritative contract with an executor-local draft;
- mutate the repository before successful contract consumption.

## 3. Responsibility model

### 3.1 Product Owner

The Product Owner:

- defines or approves the intended business outcome;
- approves material scope, risk, and business ambiguity;
- may authorize a bounded ad hoc Work Item through an authenticated natural-language request;
- does not need to prescribe routine technical implementation details.

### 3.2 AI Bridge Contract Authority

AI Bridge must be the authoritative system for:

- Project and scope resolution;
- semantic classification orchestration;
- deterministic governance policy;
- approval reference creation and validation;
- immutable scope version and hash binding;
- Execution Context generation;
- contract generation and schema validation;
- contract issuance;
- contract lifecycle state transitions;
- audit events;
- evidence-root allocation;
- completion verification.

### 3.3 Execution Provider

Codex, Claude Code, another coding agent, or a governed human executor may act as an Execution Provider.

The provider must:

- receive an AI Bridge-issued immutable contract identifier or payload;
- verify contract signature or hash, status, baseline, target repository, and scope;
- atomically consume the contract before mutation;
- execute only the bounded authorized work;
- generate required evidence and gate results;
- report the final commit and completion data to AI Bridge.

Execution Provider identity must be auditable and provider-independent.

## 4. Classification model

Classification is hybrid.

### 4.1 Semantic proposal

The LLM or request-classification layer may:

- interpret the Product Owner's natural-language request;
- propose `scope_kind`;
- propose parent scope and origin;
- propose `work_type`;
- propose an execution profile;
- identify risk modifiers;
- provide a concise audit-safe rationale;
- detect material missing information.

The LLM is advisory and must not be the final governance authority.

### 4.2 Deterministic policy resolution

The deterministic policy engine must:

- validate, strengthen, reject, or request clarification for the semantic proposal;
- prevent attachment of new work to a closed, revoked, superseded, or otherwise inactive Sprint;
- prevent Epic-level direct repository mutation;
- require a child executable scope for Epic execution;
- strengthen governance when risk requires it;
- never silently weaken a proposed governance profile;
- determine required gates, evidence, review, and documentation obligations;
- allocate deterministic collision-free evidence roots;
- determine whether Product Owner clarification or explicit approval is required;
- refuse contract issuance when required authority or input is unavailable.

Allowed deterministic outcomes:

```text
ACCEPTED
STRENGTHENED
REJECTED
CLARIFICATION_REQUIRED
```

The final classification is the deterministic policy result, not the raw LLM proposal.

## 5. Scope, work type, urgency, and execution profile

These concepts must be represented independently.

### 5.1 Scope

```yaml
scope:
  kind: "SPRINT | WORK_ITEM"
  identifier: "stable scope identifier"
  path: "repository path or immutable registry reference"
  version: "content hash"
  parent_kind: "PROJECT | INITIATIVE | MILESTONE | EPIC | SPRINT | null"
  parent_identifier: "stable parent identifier or null"
  origin: "ROADMAP | SPRINT_DECOMPOSITION | PRODUCT_OWNER_AD_HOC | INCIDENT | RECOVERY | OTHER_APPROVED_ORIGIN"
```

### 5.2 Work type

At minimum preserve:

```text
FEATURE
BUGFIX
MIGRATION
RECOVERY
DOCUMENTATION
RELEASE
SELF_DEVELOPMENT
ONBOARDING
SECURITY
CONFIGURATION
```

### 5.3 Execution profile

```text
COMPACT
STANDARD
EXTENDED
```

### 5.4 Urgency

`HOTFIX` is an urgency or risk modifier for a bounded Work Item, not a mandatory hierarchy parent.

Compatibility fields may be preserved during migration, but the canonical model must not treat `TASK`, `BUGFIX`, `SPRINT`, `EPIC`, and `HOTFIX` as a single hierarchy dimension.

## 6. Work Item domain

Implement a governed Work Item domain sufficient for ad hoc and Sprint-decomposed work.

A Work Item must contain at least:

```yaml
id: "stable identifier"
title: "human-readable title"
project_id: "registered project"
status: "DRAFT | PROPOSED | APPROVED | ACTIVE | COMPLETED | CANCELLED | SUPERSEDED"
scope_kind: "WORK_ITEM"
parent_kind: "PROJECT | EPIC | SPRINT"
parent_identifier: "nullable stable identifier"
origin: "PRODUCT_OWNER_AD_HOC | SPRINT_DECOMPOSITION | INCIDENT | RECOVERY | OTHER_APPROVED_ORIGIN"
work_type: "supported work type"
execution_profile: "COMPACT | STANDARD | EXTENDED"
urgency: "NORMAL | HOTFIX"
risk_modifiers: []
requested_outcome: []
in_scope: []
out_of_scope: []
acceptance_checks: []
requested_by: "auditable requester"
approval_reference: "durable Product Owner approval reference"
approved_at: "timestamp"
evidence_root: "deterministic path"
created_at: "timestamp"
updated_at: "timestamp"
```

A Work Item may be created from a natural-language Product Owner request only after semantic classification and deterministic validation. Approval must be durable and auditable before contract issuance.

## 7. Executable scope invariants

1. Every governed repository mutation binds exactly one executable scope.
2. An executable scope is either one approved Sprint or one approved Work Item.
3. A closed Sprint cannot accept new child Work Items, contracts, executions, or evidence.
4. A Work Item may exist directly under a Project as an ad hoc request.
5. A Work Item may belong to an active Sprint when it is part of that Sprint's approved scope.
6. A Work Item may reference an Epic for planning traceability, but Epic is not direct mutation authority.
7. Epic-only scope cannot authorize repository mutation.
8. Subtasks do not receive separate contracts by default.
9. Each execution receives a unique evidence root derived from executable scope and execution identifier.
10. Existing closed Sprint evidence is immutable except through an explicitly governed correction or recovery procedure.
11. The system must never infer the latest Sprint as parent of an ad hoc request.
12. Roadmap order does not authorize execution.
13. Only AI Bridge may issue an authoritative Execution Contract.
14. An Execution Provider may not consume a contract that it issued itself.
15. Repository mutation is forbidden before successful atomic contract consumption.
16. Contract completion is authoritative only after AI Bridge validates submitted evidence and final commit binding.

## 8. Approved executable scope model

Generalize the current mandatory `approved_sprint_path` binding.

Canonical form:

```yaml
approved_scope:
  scope_kind: "SPRINT | WORK_ITEM"
  identifier: "stable identifier"
  path: "exact repository path or immutable registry reference"
  version: "content hash"
  status: "APPROVED"
  approval_reference: "durable approval identifier"
```

Temporary backward-compatible fields may be emitted during migration, but:

- new contracts must use `approved_scope`;
- `approved_sprint_path` must not be required for Work Item contracts;
- Sprint contracts must bind an exact Sprint path and version;
- Work Item contracts must bind an exact Work Item path or immutable registry snapshot;
- all scope hashes must be computed and validated by AI Bridge before issuance.

## 9. Contract Authority model

### 9.1 Contract identity

Every contract must have:

```yaml
contract_id: "globally unique immutable identifier"
contract_version: "schema version"
issuer:
  system: "AI_BRIDGE"
  authority_instance: "stable instance identifier"
  issued_by: "auditable service or actor"
issued_at: "timestamp"
status: "DRAFT | VALIDATED | ISSUED | CONSUMED | RUNNING | COMPLETED | FAILED | CANCELLED | EXPIRED | REVOKED"
project: "registered project identity"
approved_scope: {}
approval_reference: "durable approval identifier"
execution_provider_policy: {}
baseline: {}
required_gates: []
evidence_requirements: []
evidence_root: "unique deterministic root"
contract_hash: "canonical payload hash"
```

Where supported, the contract should also carry a cryptographic signature or verifiable authority proof. A canonical content hash remains mandatory.

### 9.2 Contract lifecycle ownership

AI Bridge owns these transitions:

```text
DRAFT → VALIDATED → ISSUED
ISSUED → CONSUMED
CONSUMED → RUNNING
RUNNING → COMPLETED | FAILED
ISSUED → CANCELLED | EXPIRED | REVOKED
CONSUMED | RUNNING → REVOKED only through an explicit governed emergency path
```

The Execution Provider may request or trigger a permitted transition, but AI Bridge records and authorizes the authoritative state change.

### 9.3 Issuance prerequisites

AI Bridge must not issue a contract unless all required conditions pass:

- registered Project resolved;
- exact approved executable scope resolved;
- scope status permits execution;
- immutable scope version and hash verified;
- durable Product Owner approval reference verified;
- policy resolution is accepted or strengthened;
- target repository and branch policy resolved;
- baseline commit or baseline rule resolved;
- required gates and evidence obligations resolved;
- evidence root reserved;
- no conflicting active execution violates policy;
- contract schema and canonical hash validation pass.

### 9.4 Atomic consumption

Consumption must be atomic and auditable.

The Execution Provider submits:

- contract identifier;
- expected contract hash;
- provider identity;
- observed repository baseline;
- supported contract schema version.

AI Bridge returns either:

```text
CONSUMED
```

with a durable consumption record, or a deterministic rejection such as:

```text
CONTRACT_NOT_ISSUED
CONTRACT_HASH_MISMATCH
CONTRACT_ALREADY_CONSUMED
CONTRACT_EXPIRED
CONTRACT_REVOKED
BASELINE_MISMATCH
PROVIDER_NOT_ALLOWED
SCHEMA_NOT_SUPPORTED
```

No repository mutation may occur when consumption fails.

### 9.5 Completion

The Execution Provider submits:

- final commit SHA;
- gate results;
- evidence manifest;
- changed-file summary;
- execution result;
- failure classification where applicable.

AI Bridge validates these against the contract before recording `COMPLETED` or `FAILED`.

## 10. Contract handoff protocol

The canonical handoff must not rely only on a Markdown path.

AI Bridge must provide the Execution Provider with at least:

```yaml
handoff:
  contract_id: "immutable contract identifier"
  contract_hash: "expected canonical hash"
  contract_status: "ISSUED"
  project_id: "registered project"
  repository: "owner/name or canonical repository identifier"
  target_ref: "branch or governed ref"
  approved_scope_id: "Sprint or Work Item identifier"
  approved_scope_version: "scope content hash"
  retrieval_reference: "MCP resource, governed API reference, or immutable local artifact"
```

The provider may receive a cached contract artifact, but must validate it against AI Bridge's authoritative record before mutation.

The system must support provider-neutral handoff so Codex can later be replaced or supplemented without changing governance semantics.

## 11. Product Owner approval binding

A natural-language Product Owner instruction may authorize a bounded ad hoc Work Item only when:

- requester identity is authenticated and auditable;
- the request clearly authorizes execution rather than discussion or proposal only;
- the bounded outcome is determinable;
- no unresolved business decision remains;
- normalized request, timestamp, requester, policy result, generated scope identifier, and approval reference are stored;
- the approval reference exists before contract issuance.

The system must distinguish:

```text
DISCUSS_OR_ASSESS
PREPARE_PROPOSAL
AUTHORIZE_EXECUTION
```

Only `AUTHORIZE_EXECUTION` may produce an approved executable scope and an issued contract without an additional Product Owner approval step.

## 12. MCP and service surface

Update or add governed operations sufficient to support the full lifecycle. Exact names may follow repository conventions.

### 12.1 Request and scope capabilities

- classify a natural-language request;
- validate classification deterministically;
- create a proposed Work Item;
- approve a Work Item with durable approval reference;
- retrieve Work Item details and status;
- list relevant active and closed scopes;
- resolve an approved Sprint;
- generate Execution Context from Sprint or Work Item.

### 12.2 Contract Authority capabilities

- generate contract draft from approved scope;
- validate contract draft;
- issue contract;
- retrieve authoritative contract by identifier;
- verify contract hash and status;
- atomically consume contract for an Execution Provider;
- mark execution running;
- submit execution evidence and result;
- complete or fail contract after validation;
- cancel, expire, or revoke under policy;
- list contract audit events.

Mutation operations must remain governed and auditable. No unaudited direct mutation shortcut may be introduced.

## 13. Contract and runtime migration

Update every layer that assumes Sprint-only execution or executor-owned contract preparation, including as applicable:

- domain models and migrations;
- Work Item services;
- classification proposal boundary;
- deterministic policy resolver;
- approval reference storage;
- Execution Context generation;
- contract schemas and serializers;
- canonical hashing and signature support;
- issuance service;
- contract lifecycle state machine;
- atomic consumption service;
- provider identity and eligibility checks;
- MCP request and response schemas;
- execution identifiers;
- evidence path allocation;
- audit events;
- ExecutionRun linkage;
- completion verification;
- tests and fixtures;
- documentation examples.

Existing immutable issued contracts and historical Sprint 005–009 evidence must remain valid and readable. Do not rewrite historical artifacts.

## 14. Sprint 010 bootstrap and transition rule

Sprint 010 introduces the completed Contract Authority model, so its own first contract requires an explicit transition path.

This is not permission to bypass governance.

Before Sprint 010 repository implementation begins:

1. the approved Sprint 010 file must exist on the execution workspace's checked-out `main` and its content hash must match the approved repository version;
2. the current pre-Sprint-010 AI Bridge contract service must generate and validate the Sprint 010 contract using the existing Sprint-based contract schema;
3. AI Bridge must issue that contract and store a durable authoritative record before Codex mutation;
4. Codex must fetch, validate, and consume that issued contract;
5. the issued Sprint 010 contract and its hash must be preserved as bootstrap evidence;
6. after Sprint 010 migration, the new Contract Authority must import or recognize that historical bootstrap contract without rewriting it.

If the existing AI Bridge service cannot issue the Sprint 010 bootstrap contract, implementation must stop with:

```text
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

The blocker report must identify the missing authority operation precisely. Codex must not issue the contract to itself.

The approved Sprint document alone is not an issued contract.

## 15. Evidence layout

Use separate roots for Sprint and Work Item evidence.

Recommended canonical paths:

```text
docs/evidence/sprints/<sprint-slug>/<execution-id>/
docs/evidence/work-items/<work-item-id>-<slug>/<execution-id>/
```

Equivalent deterministic layouts are acceptable if collision-free and documented.

Required behavior:

- no ad hoc execution may write under a closed Sprint evidence root;
- repeated executions must not overwrite earlier evidence;
- final evidence must bind the final repository commit and authoritative contract;
- evidence indexes may show planning traceability without nesting unrelated evidence into closed scope directories;
- AI Bridge reserves the evidence root at issuance;
- the provider submits evidence, but AI Bridge validates completion binding.

## 16. Constitution and canonical documentation

This model is a platform governance rule and must be reflected in the Constitution.

Update the Constitution so it states at minimum:

- every repository mutation requires one approved executable scope;
- executable scope may be Sprint or Work Item;
- ad hoc Product Owner requests become standalone approved Work Items;
- closed Sprint scope and evidence are immutable historical records;
- Epic is planning/orchestration scope and requires a child executable scope;
- LLM classification is advisory and deterministic policy is authoritative;
- policy may strengthen but not silently weaken governance;
- AI Bridge is the sole authoritative Execution Contract issuer;
- execution providers cannot approve or issue their own authorization;
- mutation requires successful contract consumption;
- routine technical decisions remain autonomous inside approved scope;
- Product Owner intervention is reserved for genuine business ambiguity, material risk authorization, or required external authority;
- historical contracts and evidence are immutable and remain readable across schema migration.

Also update:

- `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`;
- `AGENTS.md` where permanent agent behavior changes;
- architecture documentation;
- MCP tool reference;
- AKB current state;
- roadmap;
- README where user-visible platform behavior is described.

## 17. Required proving executions

Sprint 010 is not complete without end-to-end proof.

### 17.1 Bootstrap proof — Sprint 010 contract handoff

Prove the transition sequence:

1. approved Sprint 010 exists on `main` and in the executor workspace;
2. the current AI Bridge service resolves its exact path and hash;
3. AI Bridge generates and validates the bootstrap contract;
4. AI Bridge issues it with an authoritative identifier and hash;
5. Codex retrieves and validates the contract;
6. Codex atomically consumes it before repository mutation;
7. audit events prove separation between issuer and executor.

### 17.2 Positive proof — ad hoc Work Item

Use a harmless predetermined README sentence change.

Prove:

1. an authenticated Product Owner submits a bounded execution request to AI Bridge;
2. semantic classification proposes `WORK_ITEM`;
3. deterministic policy accepts or strengthens it;
4. AI Bridge creates a standalone approved Work Item under the Project;
5. a durable approval reference is created;
6. AI Bridge generates Execution Context;
7. AI Bridge generates, validates, and issues the contract;
8. Codex or a test Execution Provider retrieves and consumes the issued contract;
9. the predetermined mutation occurs only after consumption;
10. required gates run;
11. evidence is submitted under the reserved Work Item root;
12. AI Bridge validates the result and records completion with final commit binding.

The Work Item must not be attached to Sprint 009 or another closed Sprint.

### 17.3 Negative proof — closed Sprint rejection

Attempt to attach a new Work Item or evidence-producing execution to closed Sprint 009.

Expected result:

```text
REJECTED — CLOSED_SCOPE_IMMUTABLE
```

No mutation, contract issuance, or evidence write may occur under the closed Sprint root.

### 17.4 Negative proof — Epic direct mutation rejection

Attempt direct repository mutation with Epic-only scope.

Expected result:

```text
REJECTED — CHILD_EXECUTABLE_SCOPE_REQUIRED
```

### 17.5 Negative proof — executor self-issuance

Attempt to let an Execution Provider issue the contract that authorizes its own mutation.

Expected result:

```text
REJECTED — CONTRACT_AUTHORITY_REQUIRED
```

### 17.6 Negative proof — mutation before consumption

Attempt repository mutation with a valid but merely `ISSUED` contract that has not been consumed.

Expected result:

```text
REJECTED — CONTRACT_NOT_CONSUMED
```

### 17.7 Negative proof — hash or baseline mismatch

Attempt consumption with a wrong contract hash or invalid repository baseline.

Expected result:

```text
CONTRACT_HASH_MISMATCH
```

or

```text
BASELINE_MISMATCH
```

No mutation may occur.

### 17.8 Strengthening proof

Provide a semantic proposal that is too weak for an explicit risk modifier.

Expected result:

```text
STRENGTHENED
```

The issued contract must contain the stronger gates and evidence requirements.

### 17.9 Provider-neutral proof

Use at least one deterministic fake Execution Provider in tests and ensure the contract handoff interface does not contain Codex-specific authorization semantics.

## 18. Release Gates

At minimum run and record:

```text
python manage.py makemigrations --check
pytest
ruff check .
ruff format --check .
mypy .
git diff --check
```

Also run Sprint-specific acceptance tests covering:

- Work Item lifecycle;
- classification proposal schema;
- deterministic policy validation;
- closed Sprint rejection;
- Epic mutation rejection;
- strengthening-only behavior;
- approved-scope contract generation for Sprint and Work Item;
- AI Bridge-only issuance authorization;
- contract canonical hashing;
- atomic contract consumption;
- duplicate-consumption rejection;
- provider eligibility;
- mutation-before-consumption rejection;
- hash and baseline mismatch rejection;
- deterministic evidence roots;
- completion evidence verification;
- immutable historical contract compatibility;
- MCP authorization and audit ordering;
- provider-neutral handoff;
- end-to-end Work Item execution;
- Sprint 010 bootstrap contract recognition.

## 19. Evidence requirements

Create Sprint evidence under:

```text
docs/evidence/sprint-010-executable-scope-and-ad-hoc-work-item-governance/
```

At minimum include:

```text
ASSESSMENT.md
CLASSIFICATION_MODEL.md
CONTRACT_AUTHORITY_ARCHITECTURE.md
BOOTSTRAP_HANDOFF.md
MIGRATION_NOTES.md
PROVING_EXECUTION.md
NEGATIVE_PROOFS.md
RELEASE_GATES.md
CLOSURE_REPORT.md
acceptance-results.json
BOOTSTRAP_ISSUED_EXECUTION_CONTRACT.json
```

The positive ad hoc Work Item must have a separate Work Item evidence root.

Evidence must distinguish:

- authoritative AI Bridge contract records;
- provider-local validation records;
- execution evidence;
- completion validation and final commit binding.

## 20. Out of scope

This Sprint does not require:

- a full Jira clone;
- boards, drag-and-drop planning UI, estimation, story points, or velocity;
- mandatory Epic creation for every Work Item;
- mandatory Sprint creation for every mutation;
- independent contracts for ordinary Subtasks;
- a complete multi-agent planner;
- the complete future Conversation Orchestrator UI;
- automatic dispatch to every possible coding provider;
- replacing historical contracts with the new schema;
- a general-purpose public PKI, provided contract authority and integrity are still verifiable inside the governed platform.

## 21. Definition of done

Sprint 010 is complete only when:

- Sprint-only assumptions are removed from the canonical execution path;
- Sprint and Work Item executable scopes are supported;
- ad hoc requests create standalone governed Work Items;
- closed Sprint attachment is deterministically rejected;
- Epic direct mutation is deterministically rejected;
- LLM proposals are validated by deterministic policy;
- policy strengthening is proven;
- AI Bridge is the authoritative contract issuer and lifecycle owner;
- Execution Providers cannot self-issue authorization;
- contract handoff is provider-neutral;
- atomic consumption is required before mutation;
- completion is validated by AI Bridge against contract and evidence;
- Work Item evidence is deterministic and collision-free;
- historical contracts remain readable and immutable;
- the Sprint 010 bootstrap contract is issued by the pre-migration AI Bridge authority and preserved as evidence;
- Constitution and all canonical documentation are synchronized;
- positive and negative proving executions pass;
- all required gates pass;
- final evidence binds the exact `main` commit;
- `HEAD == origin/main` and the worktree is clean.

Allowed terminal states:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

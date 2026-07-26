# Sprint 010 — Executable Scope, Work Item Governance, and AI Bridge Contract Authority

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`  
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

or a deterministic rejection, including at minimum:

```text
CONTRACT_NOT_ISSUED
CONTRACT_ALREADY_CONSUMED
CONTRACT_HASH_MISMATCH
REPOSITORY_MISMATCH
BRANCH_MISMATCH
BASELINE_MISMATCH
PROVIDER_NOT_ALLOWED
CONTRACT_EXPIRED
CONTRACT_REVOKED
```

No repository mutation may begin before `CONSUMED` is durably recorded.

## 10. Provider-neutral handoff

The canonical handoff must not depend on Codex-specific prompt text.

AI Bridge must provide an immutable machine-readable handoff containing at least:

```yaml
handoff:
  contract_id: "..."
  contract_hash: "..."
  contract_status: "ISSUED"
  authority_endpoint: "..."
  project_id: "..."
  repository: "..."
  branch: "..."
  baseline: "..."
  approved_scope: {}
  provider_policy: {}
  required_gates: []
  evidence_requirements: []
```

Execution-provider-specific adapters may render this into:

- a Codex task prompt;
- a Claude Code command package;
- a remote runner request;
- a governed human runbook.

Those adapters must not alter scope, approval, policy, hash, baseline, gates, or evidence requirements.

## 11. Sprint 010 bootstrap and transition rule

Sprint 010 implements the generalized Contract Authority model, but it must itself start through the strongest currently available governed path.

Before any Sprint 010 implementation mutation:

1. AI Bridge resolves the exact approved Sprint 010 document.
2. AI Bridge computes and binds the exact Sprint content hash.
3. AI Bridge resolves the registered Project, target repository, target branch, and baseline.
4. AI Bridge generates the current-version Execution Contract.
5. AI Bridge validates that contract.
6. A durable Product Owner approval reference authorizes issuance.
7. AI Bridge changes the contract to `ISSUED`.
8. The issued contract identifier or immutable handoff is passed to Codex.
9. Codex validates and consumes it before mutation.

The approved Sprint Markdown document is not itself an Execution Contract.

The existing AI Bridge contract lifecycle must be used to issue the bootstrap contract. Sprint 010 may then migrate and generalize that mechanism without rewriting the immutable bootstrap contract.

If the currently deployed AI Bridge cannot perform one of the required bootstrap operations, the run must stop with:

```text
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

The blocker report must identify the exact missing Contract Authority operation. Codex must not issue an authorization to itself as a workaround.

## 12. Evidence layout

Sprint evidence and Work Item evidence must use separate deterministic roots.

Recommended paths:

```text
docs/evidence/sprints/<sprint-slug>/<execution-id>/
docs/evidence/work-items/<work-item-id>-<slug>/<execution-id>/
```

Equivalent layouts are acceptable only when collision-free, deterministic, and documented.

Required behavior:

- no ad hoc execution may write under a closed Sprint evidence root;
- repeated executions must not overwrite earlier evidence;
- final evidence must bind the issued contract, contract hash, scope hash, baseline, final commit, and gate results;
- planning traceability may reference an Epic or Sprint without physically nesting unrelated evidence inside a closed scope directory.

## 13. Classification policy

Implement a provider-independent classifier boundary with two stages.

### Stage A — semantic proposal

Input:

- authenticated Product Owner request;
- selected Project;
- current Project Context;
- active and closed scope metadata;
- roadmap and AKB where relevant.

Output:

```yaml
proposal:
  scope_kind: "SPRINT | WORK_ITEM"
  parent_kind: "PROJECT | EPIC | SPRINT | null"
  parent_identifier: "nullable"
  origin: "..."
  work_type: "..."
  requested_profile: "COMPACT | STANDARD | EXTENDED"
  urgency: "NORMAL | HOTFIX"
  risk_modifiers: []
  rationale: []
  clarification_required: false
  clarification_questions: []
```

The semantic implementation may use an LLM provider or deterministic test double, but must be auditable and replaceable.

### Stage B — deterministic resolution

The resolver returns:

```text
ACCEPTED
STRENGTHENED
REJECTED
CLARIFICATION_REQUIRED
```

At minimum enforce:

- one small independently reviewable result may become a Work Item;
- multiple coordinated outcomes or material architectural change require Sprint-level scope;
- Epic-only repository mutation is rejected;
- closed Sprint parent or evidence binding is rejected;
- production, security, schema, authentication, public API, cross-repository, external integration, or irreversible risk strengthens obligations;
- governance may be strengthened but not silently weakened;
- missing business intent triggers clarification;
- routine technical implementation choices do not require Product Owner intervention.

## 14. Product Owner approval binding

A natural-language Product Owner request may authorize creation and approval of an ad hoc Work Item only when:

- requester identity is authenticated and auditable;
- the request clearly authorizes a bounded result;
- unresolved business ambiguity is absent;
- the normalized request, requester, timestamp, classification, and Work Item identifier are stored;
- a durable approval reference exists before contract issuance.

The system must distinguish:

```text
discussion or assessment request
proposal preparation request
bounded execution authorization
```

Only bounded execution authorization may proceed automatically to an approved executable Work Item and contract issuance.

Contract issuance remains a distinct authoritative lifecycle transition even when the Product Owner instruction supplies the underlying approval.

## 15. MCP and service surface

Update or add governed operations sufficient to support the complete separation of duties.

### 15.1 Classification and scope

Capabilities must include:

- classify a natural-language request;
- validate or strengthen classification deterministically;
- create a proposed Work Item;
- approve a Work Item with durable approval reference;
- retrieve Work Item details and status;
- list active and closed executable scopes;
- resolve one exact approved Sprint or Work Item.

### 15.2 Contract Authority

Capabilities must include:

- generate a DRAFT contract from approved scope;
- validate a DRAFT contract;
- issue a VALIDATED contract using a durable Product Owner approval reference;
- retrieve immutable contract status and payload;
- render provider-neutral handoff;
- consume an issued contract atomically;
- start and track an execution run;
- accept evidence and final commit submission;
- complete, reject, cancel, expire, revoke, or supersede contracts according to policy.

### 15.3 Authorization boundary

At minimum:

- read-only contract retrieval may be broadly available to authenticated allowed actors;
- contract generation is governed preparation;
- contract validation is deterministic preparation;
- contract issuance requires Product Owner authority or an approved delegated authority policy;
- contract consumption requires an allowed Execution Provider identity;
- completion requires evidence validation;
- self-issuance by the Execution Provider must be rejected and audited.

No unaudited mutation shortcut may bypass scope approval, contract issuance, consumption, evidence, or completion validation.

## 16. Contract and runtime migration

Update every Sprint-only or executor-authority assumption, including as applicable:

- domain models and migrations;
- Work Item services;
- semantic-classifier interface;
- deterministic policy resolver;
- Project and scope resolution;
- Execution Context generation;
- contract schemas and serializers;
- contract hashing and integrity validation;
- issuer identity and authority proof;
- contract lifecycle transitions;
- approval-reference validation;
- provider eligibility;
- atomic consumption;
- evidence allocation;
- execution identifiers;
- ExecutionRun linkage;
- audit events and ordering;
- MCP input and response schemas;
- tests, fixtures, and documentation examples.

Historical immutable contracts and Sprint 005–009 evidence must remain valid and readable. Do not rewrite historical issued contracts to match the new schema.

Compatibility adapters may expose old fields, but the canonical path must use the approved executable scope and AI Bridge-issued contract.

## 17. Constitution and canonical documentation

This is a platform governance rule and must be added to the Constitution.

The Constitution must state at minimum:

- every repository mutation requires one approved executable scope;
- executable scope may be Sprint or Work Item;
- ad hoc Product Owner requests become standalone approved Work Items rather than being attached to closed Sprints;
- closed Sprint scope and evidence are immutable historical records;
- Epic is planning and orchestration scope and requires child executable authority;
- LLM classification is advisory and deterministic policy is authoritative;
- policy may strengthen but never silently weaken governance;
- AI Bridge is the Contract Authority;
- Execution Providers cannot approve or issue their own authorization;
- only an issued and atomically consumed contract permits mutation;
- routine technical decisions remain autonomous within approved scope;
- Product Owner intervention is reserved for genuine business ambiguity, risk authorization, or required external authority.

Also update and synchronize:

- `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`;
- `AGENTS.md` where permanent executor behavior changes;
- architecture documentation;
- MCP tool reference;
- `docs/akb/CURRENT_STATE.md`;
- `docs/roadmap/ROADMAP.md`;
- README where user-visible behavior is described.

## 18. Required proving executions

Sprint 010 is not complete without end-to-end proof.

### 18.1 Bootstrap proof — Sprint 010 contract handoff

Prove the transition path used to start Sprint 010:

```text
approved Sprint 010
→ AI Bridge Execution Context
→ contract DRAFT
→ VALIDATED
→ Product Owner approval binding
→ ISSUED
→ Codex retrieval
→ independent validation
→ atomic CONSUMED
→ execution start
```

Record the immutable bootstrap contract separately from any new-schema proving contract produced later in the Sprint.

### 18.2 Positive proof — ad hoc Work Item

Use a harmless predetermined README sentence change.

Prove:

1. ChatGPT or equivalent authenticated caller submits a bounded execution request.
2. Semantic classification proposes `WORK_ITEM`.
3. Deterministic policy accepts or strengthens it.
4. A standalone approved Work Item is created under the Project.
5. It is not attached to Sprint 009 or another closed Sprint.
6. A durable approval reference is created.
7. AI Bridge generates and validates the contract.
8. AI Bridge issues the contract.
9. An allowed Execution Provider retrieves and atomically consumes it.
10. The predetermined repository mutation occurs only after consumption.
11. Required Release Gates run.
12. Evidence is written under the Work Item evidence root.
13. AI Bridge validates evidence and completes the contract with final commit binding.

### 18.3 Negative proof — executor self-issuance

Attempt to issue a contract using the same authority identity as the intended Execution Provider without Product Owner or delegated authority.

Expected result:

```text
REJECTED — EXECUTOR_SELF_ISSUANCE_FORBIDDEN
```

### 18.4 Negative proof — mutation before consumption

Attempt to start execution or record repository mutation while the contract is only `VALIDATED` or `ISSUED`.

Expected result:

```text
REJECTED — CONTRACT_NOT_CONSUMED
```

### 18.5 Negative proof — closed Sprint

Attempt to attach a new Work Item, contract, execution, or evidence to closed Sprint 009.

Expected result:

```text
REJECTED — CLOSED_SCOPE_IMMUTABLE
```

No repository mutation or evidence write may occur under Sprint 009.

### 18.6 Negative proof — Epic direct mutation

Attempt repository mutation using Epic-only scope.

Expected result:

```text
REJECTED — CHILD_EXECUTABLE_SCOPE_REQUIRED
```

### 18.7 Integrity proofs

Prove deterministic rejection for:

- altered contract payload after issuance;
- wrong contract hash;
- wrong target repository;
- wrong target branch;
- wrong baseline;
- unauthorized provider;
- duplicate consumption;
- expired or revoked contract.

### 18.8 Strengthening proof

Provide a deliberately too-weak semantic proposal with an explicit high-risk modifier.

Expected result:

```text
STRENGTHENED
```

The issued contract must contain the stronger gates, evidence, and review obligations.

### 18.9 Provider-neutrality proof

Demonstrate that the same issued contract or canonical handoff can be rendered for at least two provider adapter types without changing the authoritative contract payload.

A deterministic test adapter is sufficient for the second provider; a live second coding provider is not required.

## 19. Release Gates

At minimum run and record:

```text
python manage.py makemigrations --check
pytest
ruff check .
ruff format --check .
mypy .
git diff --check
```

Also run Sprint-specific tests covering:

- Work Item lifecycle;
- semantic proposal schema;
- deterministic classification;
- closed Sprint rejection;
- Epic direct mutation rejection;
- strengthening-only behavior;
- Sprint and Work Item approved-scope contract generation;
- AI Bridge-only issuance authority;
- Product Owner approval binding;
- executor self-issuance rejection;
- contract hash integrity;
- atomic consumption and duplicate-consumption rejection;
- repository, branch, and baseline validation;
- deterministic evidence roots;
- historical contract compatibility;
- provider-neutral handoff;
- MCP authorization;
- audit ordering and lifecycle events;
- end-to-end ad hoc Work Item execution;
- completion evidence validation.

## 20. Evidence requirements

Create Sprint evidence under:

```text
docs/evidence/sprint-010-executable-scope-and-ad-hoc-work-item-governance/
```

At minimum include:

```text
ASSESSMENT.md
CLASSIFICATION_MODEL.md
CONTRACT_AUTHORITY_MODEL.md
BOOTSTRAP_CONTRACT_HANDOFF.md
MIGRATION_NOTES.md
PROVING_EXECUTION.md
NEGATIVE_PROOFS.md
RELEASE_GATES.md
CLOSURE_REPORT.md
acceptance-results.json
ISSUED_EXECUTION_CONTRACT.json
```

The ad hoc proving Work Item must have a separate Work Item evidence root.

Evidence must identify:

- AI Bridge authority instance;
- Product Owner approval reference;
- immutable contract identifier and hash;
- approved scope identifier and hash;
- Execution Provider identity;
- consumption event;
- execution run;
- required gates and results;
- final commit;
- AI Bridge completion decision.

## 21. Out of scope

This Sprint does not require:

- a Jira clone;
- planning boards, estimation, story points, or velocity;
- mandatory Epic creation for every Work Item;
- mandatory Sprint creation for every mutation;
- independent contracts for ordinary Subtasks;
- a complete Conversation Orchestrator interface;
- a live integration with every possible coding provider;
- a public-key infrastructure beyond the repository's reasonable current maturity, provided canonical hashing and issuer identity are proven.

## 22. Definition of done

Sprint 010 is complete only when:

- the Sprint-only canonical execution assumption is removed;
- Sprint and Work Item executable scopes are supported;
- ad hoc Product Owner requests create standalone governed Work Items;
- closed Sprint attachment is deterministically rejected;
- Epic direct mutation is deterministically rejected;
- LLM classification remains advisory and deterministic policy is authoritative;
- governance strengthening is proven;
- AI Bridge is the authoritative Contract Authority;
- an Execution Provider cannot issue its own contract;
- the Sprint 010 bootstrap contract was issued by AI Bridge and consumed before mutation;
- repository mutation before consumption is rejected;
- Work Item evidence roots are deterministic and collision-free;
- historical contracts remain readable and valid;
- provider-neutral handoff is proven;
- Constitution and canonical documentation match implementation;
- positive and negative proving executions pass;
- all required Release Gates pass;
- final evidence binds the exact `main` commit;
- `HEAD == origin/main` and the worktree is clean.

Allowed terminal states:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

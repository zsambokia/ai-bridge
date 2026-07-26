# Sprint 010 — Executable Scope and Ad Hoc Work Item Governance

**Status:** APPROVED FOR IMPLEMENTATION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Primary outcome:** Replace the mandatory-Sprint execution assumption with a governed executable-scope model that supports both approved Sprints and standalone ad hoc Work Items without attaching new work to closed Sprints.

## 1. Problem statement

The current governed execution flow requires every contract to resolve one exact approved Sprint. This causes small or ad hoc Product Owner requests to be attached to an unrelated or already closed Sprint. The first ChatGPT external acceptance attempt demonstrated this failure mode: a standalone README documentation task was classified as a `TASK`, but its execution context and evidence root were still derived from the already closed Sprint 009.

This is misleading because:

- a closed Sprint is immutable historical scope and evidence;
- later ad hoc work is not part of that Sprint;
- new evidence must not be written into a closed Sprint evidence area;
- `TASK`, `BUGFIX`, and `HOTFIX` are executable work classifications, not mandatory children of a Sprint;
- an Epic is a planning and orchestration container, not direct permission for unbounded repository mutation.

## 2. Product Owner decision

The canonical work hierarchy is:

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

A Subtask is not independently governed by default and does not receive a separate execution contract unless risk, repository boundary, authorization, or independent approval requires one.

## 3. Classification model

Classification is hybrid.

### 3.1 LLM responsibilities

The conversation or request-classification layer may:

- interpret the Product Owner's natural-language request;
- propose `scope_kind`;
- propose parent scope and origin;
- propose `work_type`;
- propose risk modifiers;
- provide a concise audit-safe classification rationale;
- detect missing information and request clarification only when materially necessary.

The LLM must not be the final authority for governance validity.

### 3.2 Deterministic policy responsibilities

The deterministic policy engine must:

- validate or reject the LLM proposal;
- prevent attachment of new work to a closed, revoked, superseded, or otherwise non-active Sprint;
- prevent Epic-level direct code mutation;
- require a child executable scope for Epic execution;
- strengthen governance when risk requires it;
- never silently weaken a proposed governance profile;
- determine required gates, evidence, review, and documentation obligations;
- produce deterministic, collision-free evidence paths;
- determine whether Product Owner clarification or approval is required.

The final classification is the deterministic policy result, not the raw LLM proposal.

## 4. Scope, work type, and execution profile must be separate

The current execution-level model mixes three concerns. Sprint 010 must represent them independently.

### 4.1 Scope

```yaml
scope:
  kind: "SPRINT | WORK_ITEM"
  identifier: "stable scope identifier"
  path: "repository path to approved scope document"
  version: "content hash"
  parent_kind: "PROJECT | INITIATIVE | MILESTONE | EPIC | SPRINT | null"
  parent_identifier: "stable parent identifier or null"
  origin: "ROADMAP | SPRINT_DECOMPOSITION | PRODUCT_OWNER_AD_HOC | INCIDENT | RECOVERY | OTHER_APPROVED_ORIGIN"
```

### 4.2 Work type

At minimum preserve the supported types:

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

### 4.3 Execution profile

Governance depth must be represented separately from scope kind and work type.

At minimum:

```text
COMPACT
STANDARD
EXTENDED
```

`HOTFIX` should be treated as an urgency or execution profile modifier for a bounded Work Item, not as a mandatory hierarchy parent.

Compatibility with existing contract fields may be preserved through an explicit schema migration, but the canonical model must not continue to treat `TASK`, `BUGFIX`, `SPRINT`, and `EPIC` as one hierarchy dimension.

## 5. Work Item domain

Implement a governed Work Item domain sufficient for ad hoc execution.

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
work_type: "supported task type"
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

A Work Item may be created from a natural-language Product Owner request only after classification and deterministic validation. Approval must be durable and auditable.

## 6. Executable scope rules

Implement the following invariants:

1. Every governed repository mutation binds exactly one executable scope.
2. An executable scope is either one approved Sprint or one approved Work Item.
3. A closed Sprint cannot accept new child Work Items or new execution evidence.
4. A Work Item may exist directly under a Project as an ad hoc request.
5. A Work Item may belong to an active Sprint when it is part of that Sprint's approved scope.
6. A Work Item may reference an Epic for planning traceability, but the Work Item itself remains the executable scope unless an approved Sprint is the executable scope.
7. Epic scope cannot directly authorize repository mutation; child contracts are mandatory.
8. Subtasks do not receive separate contracts by default.
9. Each execution receives a unique evidence root derived from its executable scope and execution identifier.
10. Existing closed Sprint evidence remains immutable except for explicitly governed correction or recovery procedures.
11. The system must never infer the most recent Sprint as the parent of an ad hoc request.
12. Roadmap order does not authorize scope creation or execution.

## 7. Approved scope document model

Generalize the current mandatory `approved_sprint_path` binding to an approved executable scope binding.

Canonical form:

```yaml
approved_scope:
  scope_kind: "SPRINT | WORK_ITEM"
  identifier: "stable identifier"
  path: "exact repository path"
  version: "content hash"
  status: "APPROVED"
```

Temporary backward-compatible fields may be emitted during migration, but:

- new contracts must use the canonical approved-scope representation;
- `approved_sprint_path` must not be required for a Work Item contract;
- Sprint contracts must still bind an exact Sprint path and version;
- Work Item contracts must bind an exact Work Item path or canonical immutable registry snapshot.

## 8. Evidence layout

Use separate roots for Sprint and Work Item evidence.

Recommended canonical paths:

```text
docs/evidence/sprints/<sprint-slug>/<execution-id>/
docs/evidence/work-items/<work-item-id>-<slug>/<execution-id>/
```

Equivalent deterministic layouts are acceptable if collision-free and documented.

Required behavior:

- no new ad hoc execution may write under a closed Sprint evidence root;
- repeated executions of the same Work Item must not overwrite earlier evidence;
- final evidence must bind the final repository commit and execution contract;
- evidence indexes should make parent Epic or Sprint traceability visible without physically nesting unrelated evidence into closed scope directories.

## 9. Classification policy

Implement a canonical classifier boundary with two stages.

### Stage A — semantic proposal

Input:

- Product Owner request;
- selected Project;
- current Project Context;
- active and closed scope metadata;
- roadmap and current state where relevant.

Output:

```yaml
proposal:
  scope_kind: "SPRINT | WORK_ITEM"
  parent_kind: "PROJECT | EPIC | SPRINT | null"
  parent_identifier: "nullable"
  origin: "..."
  work_type: "..."
  requested_profile: "COMPACT | STANDARD | EXTENDED"
  risk_modifiers: []
  rationale: []
  clarification_required: false
  clarification_questions: []
```

The implementation may use an LLM provider, a deterministic test double, or both, but the interface must be provider-independent and auditable.

### Stage B — deterministic policy resolution

The resolver must return one of:

```text
ACCEPTED
STRENGTHENED
REJECTED
CLARIFICATION_REQUIRED
```

At minimum enforce:

- one small independently reviewable result may be a Work Item;
- multiple coordinated outcomes or material architecture change require Sprint-level scope;
- repository mutation under Epic-only scope is rejected;
- closed Sprint parent is rejected;
- production, security, schema, authentication, public API, cross-repository, external integration, or irreversible risk strengthens obligations;
- the resolver may strengthen but must not silently weaken governance;
- missing business intent triggers clarification, while routine technical implementation detail does not.

## 10. Product Owner approval binding

A natural-language Product Owner instruction may serve as authorization to create an ad hoc Work Item only when:

- the requester identity is authenticated and auditable;
- the request clearly authorizes the bounded outcome;
- classification does not require unresolved business decisions;
- the exact normalized request, timestamp, requester, classification result, and generated Work Item identifier are stored;
- a durable approval reference is created before contract issuance.

The system must distinguish:

```text
request to discuss or assess
request to prepare a proposal
request to execute an approved bounded change
```

Only the third category may automatically create an approved executable Work Item.

## 11. MCP and service surface

Update or add governed operations sufficient to support the lifecycle. Exact names may follow repository conventions, but capabilities must include:

- classify a natural-language request;
- validate a classification deterministically;
- create a proposed Work Item;
- approve a Work Item with durable approval reference;
- retrieve Work Item details and status;
- list relevant active and closed scopes;
- generate execution context from either Sprint or Work Item scope;
- generate, validate, issue, consume, execute, and complete contracts for either scope kind.

Mutation operations must remain governed and auditable.

## 12. Contract and runtime migration

Update all implementation layers that assume Sprint-only execution, including as applicable:

- execution context generation;
- contract schemas and serializers;
- contract validation and hashing;
- contract policy resolution;
- MCP request and response schemas;
- execution identifiers;
- evidence path resolution;
- audit events;
- ExecutionRun linkage;
- tests and fixtures;
- documentation examples.

Existing immutable issued contracts and historical evidence must remain valid and readable. Do not rewrite historical Sprint 005–009 contract artifacts.

## 13. Constitution and canonical documentation

This model is a platform governance rule and must be reflected in the Constitution.

Update the Constitution so it states, at minimum:

- every repository mutation requires one approved executable scope;
- executable scope may be Sprint or Work Item;
- an ad hoc Product Owner request must become its own approved Work Item rather than being attached to a closed Sprint;
- closed Sprint scope and evidence are immutable historical records;
- Epic is planning/orchestration scope and requires child executable contracts;
- LLM classification is advisory and deterministic policy is authoritative;
- policy may strengthen but not silently weaken governance;
- routine technical decisions remain autonomous within approved scope;
- Product Owner intervention is reserved for genuine business ambiguity, risk authorization, or required external authority.

Also update:

- `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`;
- `AGENTS.md` where permanent agent behavior changes;
- architecture documentation;
- MCP tool reference;
- AKB current state;
- roadmap;
- README only if user-visible platform behavior is described there.

## 14. Required proving executions

Sprint 010 is not complete without end-to-end proof.

### 14.1 Positive proof — ad hoc Work Item

Use a harmless, predetermined repository documentation change, such as one exact README sentence.

Prove:

1. ChatGPT or an equivalent external caller submits a bounded Product Owner execution request.
2. The semantic classifier proposes `WORK_ITEM`.
3. The deterministic resolver accepts or strengthens it.
4. A standalone approved Work Item is created under the Project, not under Sprint 009 or any other closed Sprint.
5. A durable approval reference is created.
6. Execution Context is generated from the Work Item.
7. A contract is generated, validated, issued, consumed, and started.
8. The predetermined documentation mutation occurs.
9. Required Release Gates run.
10. Evidence is written under a Work Item-specific evidence root.
11. The execution completes and binds the final commit.

### 14.2 Negative proof — closed Sprint rejection

Attempt to attach a new Work Item or new evidence-producing execution to closed Sprint 009.

Expected result:

```text
REJECTED — CLOSED_SCOPE_IMMUTABLE
```

No repository mutation or evidence write may occur under the closed Sprint root.

### 14.3 Negative proof — Epic direct mutation rejection

Attempt direct repository mutation with only Epic scope.

Expected result:

```text
REJECTED — CHILD_EXECUTABLE_SCOPE_REQUIRED
```

### 14.4 Strengthening proof

Provide a request whose LLM proposal is too weak for an explicit risk modifier.

Expected result:

```text
STRENGTHENED
```

The final policy must include the required stronger gates and evidence.

## 15. Release Gates

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
- deterministic validation;
- closed Sprint rejection;
- Epic mutation rejection;
- strengthening-only behavior;
- approved-scope contract generation for Sprint and Work Item;
- deterministic evidence roots;
- immutable historical contract compatibility;
- MCP authorization and audit events;
- end-to-end Work Item execution.

## 16. Evidence requirements

Create Sprint evidence under:

```text
docs/evidence/sprint-010-executable-scope-and-ad-hoc-work-item-governance/
```

At minimum include:

```text
ASSESSMENT.md
CLASSIFICATION_MODEL.md
MIGRATION_NOTES.md
PROVING_EXECUTION.md
NEGATIVE_PROOFS.md
RELEASE_GATES.md
CLOSURE_REPORT.md
acceptance-results.json
ISSUED_EXECUTION_CONTRACT.json
```

The proving ad hoc Work Item must have a separate Work Item evidence root and must not be nested inside Sprint 009 evidence.

## 17. Out of scope

This Sprint does not require:

- a full Jira clone;
- boards, drag-and-drop planning UI, estimation, story points, or velocity;
- mandatory Epic creation for every Work Item;
- mandatory Sprint creation for every mutation;
- independent contracts for ordinary Subtasks;
- multi-agent planning beyond the classification and policy boundary;
- the complete future Conversation Orchestrator user experience.

## 18. Definition of done

Sprint 010 is complete only when:

- Sprint-only contract assumptions are removed from the canonical execution path;
- both Sprint and Work Item executable scopes are supported;
- ad hoc requests create standalone governed Work Items;
- closed Sprint attachment is deterministically rejected;
- Epic direct mutation is deterministically rejected;
- LLM proposals are validated by deterministic policy;
- policy strengthening is proven;
- Work Item-specific evidence is deterministic and collision-free;
- historical contracts remain readable and valid;
- Constitution and all canonical documentation are synchronized;
- the positive and negative proving executions pass;
- all required gates pass;
- final evidence binds the exact `main` commit;
- `HEAD == origin/main` and the worktree is clean.

Allowed terminal states:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

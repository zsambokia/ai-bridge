# Sprint 005 — Tiered Execution Contracts and Cloudflare Host Repair

**Status:** APPROVED FOR CODEX EXECUTION  
**Execution level:** SPRINT  
**Primary task types:** SELF_DEVELOPMENT, BUGFIX  
**Target branch:** `main`

## 1. Vision

Make governed Codex work proportional to the size and risk of the requested change while preserving the control provided by `AGENTS.md`, repository-bound execution contracts, Release Gates, and evidence.

This Sprint must also prove the first lightweight execution path by repairing the current Django host configuration so the application can be reached safely through the approved Cloudflare Tunnel hostnames.

## 2. Problem

The current contract model recognizes task types such as `BUGFIX`, `FEATURE`, and `MIGRATION`, but applies nearly the same maximum governance burden to every execution. A small, well-bounded configuration repair should not require the same planning, documentation, and evidence surface as a multi-sprint Epic.

At the same time, governance must not be weakened into an informal bypass. Every mutation remains repository-bound, baseline-bound, scope-bound, testable, and evidence-backed.

The application currently rejects the Cloudflare Tunnel hosts with Django `DisallowedHost` because the relevant hostnames are not allowed:

```text
stage.artificial-software-factory.com
app.artificial-software-factory.com
```

## 3. Core model

Separate two dimensions that must not be conflated:

1. **Execution level** — the size, duration, coordination need, and expected evidence depth of the governed work unit.
2. **Task type** — the nature and risk profile of the requested change.

### 3.1 Required execution levels

The platform must support at least:

```text
HOTFIX
BUGFIX
TASK
SPRINT
EPIC
```

The implementation may add a program-level parent above `EPIC` only when it is justified by the existing architecture and does not expand this Sprint unnecessarily.

### 3.2 Required task types

Preserve and normalize the existing task types, including at least:

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

An execution level never replaces task type. For example:

```text
execution_level: BUGFIX
task_type: CONFIGURATION
```

or:

```text
execution_level: SPRINT
task_type: FEATURE
```

## 4. Minimum governance profiles

All levels must retain these non-negotiable invariants:

- explicit Project and repository identity;
- explicit target branch and integration target;
- recorded baseline commit or descendant rule;
- approved scope document;
- unique handoff identifier and immutable issued contract;
- preflight before mutation;
- preservation of unrelated work;
- relevant automated validation;
- deterministic evidence path;
- exact final commit binding;
- allowed terminal states from the Constitution;
- ordinary technical failures require diagnose, repair, and rerun.

The level changes the depth and breadth of the required artifacts, not whether governance exists.

### 4.1 HOTFIX

Intended for an urgent, narrowly bounded production or deployment repair.

Minimum expectations:

- explicit incident or failure statement;
- smallest safe scope;
- focused impact and rollback assessment;
- targeted tests and smoke validation;
- relevant repository-wide gates unless the contract explicitly records why a non-relevant gate is omitted;
- compact machine-readable evidence and closure note;
- follow-up item when a temporary mitigation remains.

Must not authorize unrelated refactoring, feature work, or architecture redesign.

### 4.2 BUGFIX

Intended for a reproducible defect with bounded correction scope.

Minimum expectations:

- reproducible failure or precise defect evidence;
- root-cause assessment;
- regression test or equivalent automated proof;
- targeted validation plus relevant repository gates;
- concise closure report;
- documentation update only where behavior, configuration, operation, or accepted knowledge changed.

### 4.3 TASK

Intended for a small, independently reviewable change that is not necessarily a defect.

Minimum expectations:

- explicit outcome and boundaries;
- acceptance checks;
- targeted implementation and tests;
- relevant Release Gates;
- compact evidence and final commit binding.

### 4.4 SPRINT

Intended for a coherent implementation increment with one primary outcome.

Minimum expectations:

- approved Sprint specification;
- assessment-first development and reuse strategy;
- explicit in-scope and out-of-scope boundaries;
- complete repository-wide and Sprint-specific Release Gates;
- acceptance scenarios;
- documentation and AKB synchronization;
- closure report and machine-readable results;
- Product Owner review handoff.

### 4.5 EPIC

Intended for a multi-sprint product or platform outcome.

An Epic contract is a planning and orchestration contract. It must not grant one unbounded Codex execution permission across the entire Epic.

Minimum expectations:

- business or platform outcome;
- architecture and invariant boundaries;
- decomposition into explicitly approved child Sprints or work units;
- dependency graph and sequencing;
- shared acceptance criteria and cumulative evidence index;
- risk, migration, compatibility, and rollback strategy where applicable;
- each code-changing child execution receives its own immutable execution contract and final evidence;
- Epic completion requires accepted evidence from every mandatory child work unit.

## 5. Contract policy resolution

Implement a canonical policy-resolution mechanism that derives contract requirements from:

```text
Project definition
+ execution level
+ task type
+ approved scope document
+ risk modifiers
```

Risk modifiers must be explicit and may only strengthen requirements. At minimum consider:

- production impact;
- security relevance;
- data or schema migration;
- authentication or authorization changes;
- external integration changes;
- public API or protocol changes;
- cross-repository impact;
- irreversible operation.

The resolved contract must state which gates, evidence artifacts, review requirements, and documentation obligations apply and why.

No profile may silently suppress a mandatory project gate. Gate omission must be explicit, justified, deterministic, and permitted by repository policy.

## 6. AGENTS.md integration

Replace the obsolete temporary Sprint 004 bootstrap section with permanent instructions for tiered governed execution.

`AGENTS.md` must remain concise and generic. It should:

- require a validated and issued contract for every mutation;
- require Codex to honor `execution_level`, `task_type`, resolved policy, scope, gates, and evidence obligations;
- prohibit Codex from upgrading or downgrading execution level on its own;
- permit Codex to request a stronger profile when detected risk exceeds the issued contract;
- prohibit using a lightweight level to hide feature work or broad refactoring;
- state that an Epic authorizes decomposition and coordination, while child code changes require child contracts;
- remove all temporary Sprint 004 exceptions after confirming they are no longer needed.

## 7. Canonical specification and schema updates

Update `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md` and the implementation so the machine-readable contract contains at least:

```yaml
execution:
  execution_level: "HOTFIX | BUGFIX | TASK | SPRINT | EPIC"
  task_type: "FEATURE | BUGFIX | MIGRATION | RECOVERY | DOCUMENTATION | RELEASE | SELF_DEVELOPMENT | ONBOARDING | SECURITY | CONFIGURATION"
  risk_modifiers: []

policy:
  profile_version: "stable version"
  resolved_profile: "profile identifier"
  required_assessment_depth: "compact | standard | extended"
  required_release_gates: []
  required_evidence_artifacts: []
  required_documentation_updates: []
  child_contract_required: false
  omission_justifications: []
```

Exact field names may follow canonical implementation conventions, but the concepts, invariants, and validation must be represented and tested.

Preserve existing contract lifecycle protection:

```text
DRAFT
VALIDATED
ISSUED
CONSUMED
COMPLETED
SUPERSEDED
REVOKED
```

## 8. Cloudflare Tunnel host repair

Implement the bounded configuration repair as the first proof of the `BUGFIX` execution level with task type `CONFIGURATION`.

Required behavior:

1. The application accepts requests for:

```text
stage.artificial-software-factory.com
app.artificial-software-factory.com
```

2. Do not use an unrestricted wildcard such as:

```python
ALLOWED_HOSTS = ["*"]
```

3. Prefer environment-driven configuration with safe, documented defaults appropriate to the repository's deployment model.
4. Preserve local development and test behavior.
5. Add automated tests proving the approved hosts are accepted and an unapproved host remains rejected where the framework permits deterministic testing.
6. Document the required environment variable or deployment configuration.
7. Do not add a login screen or unrelated authentication feature in this Sprint.

## 9. In scope

- assess the existing contract generator, validator, persistence, MCP schemas, and execution-package implementation;
- introduce execution levels and policy profiles without parallel contract systems;
- update contract validation and serialization;
- update relevant MCP request/response schemas;
- implement risk-modifier strengthening rules;
- implement Epic-to-child-contract invariants at specification and validation level;
- update `AGENTS.md` permanently;
- update canonical documentation and Project knowledge;
- implement and prove the Cloudflare host configuration repair;
- create reusable templates or examples for each required execution level;
- produce complete Sprint evidence.

## 10. Explicitly out of scope

- login or authentication UI;
- autonomous Epic decomposition by an LLM;
- organization, department, employee, or role simulation;
- a visual contract-management dashboard;
- cross-repository transaction coordination;
- weakening repository-wide quality requirements merely to make small changes pass faster;
- backward-compatibility layers that are not required by current repository consumers.

## 11. Acceptance scenarios

### A. Profile resolution

Given the same registered Project, prove deterministic policy resolution for:

1. `BUGFIX + CONFIGURATION`;
2. `SPRINT + FEATURE`;
3. `EPIC + SELF_DEVELOPMENT`.

The resulting contracts must differ in required assessment depth, evidence surface, and child-contract rules while retaining all common invariants.

### B. Lightweight bugfix proof

Issue and consume a valid `BUGFIX + CONFIGURATION` contract for the Cloudflare host repair. Prove:

- exact repository and baseline binding;
- narrow approved scope;
- regression tests;
- relevant Release Gates;
- compact but sufficient evidence;
- final commit binding and allowed closure state.

### C. Sprint profile proof

Generate a `SPRINT` profile contract and prove it requires:

- approved Sprint binding;
- assessment and reuse strategy;
- full acceptance suite;
- documentation and AKB synchronization;
- closure report and machine results.

### D. Epic guardrail proof

Generate an `EPIC` contract and prove:

- it cannot directly authorize unrestricted implementation;
- `child_contract_required` is true;
- child Sprint or work-unit identifiers are required before code-changing execution;
- cumulative evidence can reference child evidence without replacing it.

### E. Risk strengthening

Prove that a security, migration, or production-impact modifier adds requirements and cannot remove them.

### F. Host acceptance

Prove that requests using both approved Cloudflare hostnames no longer fail with `DisallowedHost`, while wildcard host acceptance is not introduced.

### G. Legacy and regression safety

Run all repository-native Release Gates and prove existing Sprint 004 MCP/context behavior still passes.

## 12. Required evidence

Evidence root:

```text
docs/evidence/sprint-005-tiered-contracts-and-cloudflare-host-repair/
```

Required artifacts:

```text
CLOSURE_REPORT.md
acceptance-results.json
profile-resolution-examples.json
cloudflare-host-validation.json
```

Evidence must include:

- preflight repository, branch, baseline, and worktree state;
- current implementation assessment;
- reuse strategy;
- schema and policy decisions;
- files changed;
- exact commands and results;
- all acceptance scenario results;
- generated example contracts for every required level;
- Cloudflare host regression proof;
- documentation and AKB updates;
- final branch and commit SHA;
- exact terminal state.

## 13. Release Gates

Run every repository-wide gate resolved from `.bridge/project.yaml`, including the complete configured gate set, plus Sprint-specific tests for:

- policy resolution;
- contract schema and lifecycle validation;
- level/task-type combinations;
- risk strengthening;
- Epic child-contract enforcement;
- MCP schema compatibility;
- Cloudflare host acceptance and rejection behavior.

Ordinary implementation, configuration, dependency, test, lint, type, evidence, or documentation failures must be diagnosed, repaired, and rerun without Product Owner intervention.

## 14. Closure requirements

Before closure:

1. update `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`;
2. update `AGENTS.md` and remove the temporary Sprint 004 exception;
3. update affected architecture and protocol documentation;
4. update `docs/akb/CURRENT_STATE.md`;
5. update `docs/roadmap/ROADMAP.md` to reflect the tiered contract capability accurately;
6. record the exact final `main` commit;
7. bind every evidence artifact to that final state;
8. close with exactly one allowed terminal state.

Allowed terminal states:

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

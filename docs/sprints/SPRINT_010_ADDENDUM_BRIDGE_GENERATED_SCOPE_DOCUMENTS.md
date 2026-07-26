# Sprint 010 Addendum — Bridge-Generated Canonical Scope Documents

**Status:** APPROVED FOR CODEX EXECUTION  
**Parent Sprint:** `docs/sprints/SPRINT_010_EXECUTABLE_SCOPE_AND_AD_HOC_WORK_ITEM_GOVERNANCE.md`  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Execution level:** SPRINT  
**Task type:** SELF_DEVELOPMENT  
**Target branch:** `main`  

This document is a binding extension of Sprint 010. Its requirements are part of the Sprint 010 scope, acceptance criteria, evidence obligations, and Definition of Done.

## 1. Product Owner decision

AI Bridge must become the authoritative producer of canonical planning and executable-scope documents.

The Product Owner or an LLM-facing conversation layer describes the intended outcome in natural language. The LLM may interpret that request and propose structured planning data, but it must not create an authoritative free-form Sprint or Work Item document by itself.

AI Bridge must validate the request, resolve the correct scope type, apply deterministic governance policy, and generate the factory-compliant Sprint or Work Item document in the canonical format required by the repository and execution system.

The intended operating model is:

```text
Product Owner natural-language request
→ LLM semantic interpretation and structured proposal
→ AI Bridge deterministic classification and policy resolution
→ AI Bridge canonical Sprint or Work Item generation
→ Product Owner approval binding where required
→ AI Bridge publication and immutable version binding
→ AI Bridge Execution Contract generation, validation, and issuance
→ Execution Provider consumption and execution
```

The long-term Product Owner experience must not require manually authoring Markdown Sprint files or remembering exact machine-sensitive status strings.

## 2. Authority boundary

### 2.1 LLM responsibilities

The LLM or semantic request layer may:

- interpret the Product Owner's natural-language intent;
- propose a title and concise problem statement;
- propose requested outcomes;
- propose `scope_kind`, work type, urgency, execution profile, parent scope, and origin;
- identify risks, constraints, dependencies, and possible missing business information;
- propose acceptance outcomes and an audit-safe rationale;
- ask the Product Owner for clarification when material business ambiguity exists.

The LLM output is advisory input. It is not an approved Sprint, Work Item, execution authorization, or authoritative repository document.

### 2.2 AI Bridge responsibilities

AI Bridge must:

- authenticate and audit the requester;
- resolve the selected Project and Project Context;
- validate or strengthen the semantic proposal deterministically;
- choose the correct canonical document type;
- allocate the stable Sprint or Work Item identifier;
- apply the canonical schema and allowed enum values;
- resolve repository, branch, parent scope, gates, evidence, and documentation obligations;
- render the canonical human-readable repository document;
- validate the complete generated document before publication;
- bind durable Product Owner approval where required;
- compute and retain the immutable scope content hash;
- publish the document through a governed repository mutation path;
- retain generation, validation, approval, publication, and supersession audit events;
- use the published immutable scope version as input to Execution Context and Execution Contract generation.

### 2.3 Execution Provider responsibilities

Codex or another Execution Provider may consume and implement an AI Bridge-generated scope document, but must not:

- create its own authoritative Sprint or Work Item authorization;
- repair invalid scope metadata by silently changing the approved meaning;
- replace the Bridge-generated document with an executor-local prompt;
- broaden the scope;
- mutate the repository before successful contract consumption.

## 3. Canonical document model

AI Bridge must maintain one structured canonical scope record and produce a repository Markdown representation from that record.

```text
AI Bridge canonical scope record
├── stable identity
├── structured metadata
├── normalized requested outcome
├── deterministic policy result
├── approval reference
├── immutable version and content hash
├── lifecycle state
└── audit history
        │
        ▼
Generated repository Markdown document
```

The Markdown document remains human-readable, reviewable, version-controlled, and binding. However, manually authored prose or a machine-sensitive status sentence alone must not be the canonical approval source.

## 4. Sprint metadata schema

Implement a versioned canonical Sprint metadata schema. YAML front matter is recommended unless the repository already contains a stronger compatible representation.

Minimum semantic fields:

```yaml
schema: "ai-bridge-sprint/v1"
sprint_id: "SPRINT_010"
title: "human-readable title"
project_id: "ai-bridge"
repository: "zsambokia/ai-bridge"
target_branch: "main"
status: "DRAFT | PROPOSED | APPROVED | ACTIVE | COMPLETED | CANCELLED | SUPERSEDED"
execution_authorization: "NONE | APPROVED_PROVIDER_EXECUTION"
execution_level: "SPRINT"
work_type: "supported work type"
execution_profile: "COMPACT | STANDARD | EXTENDED"
origin: "ROADMAP | PRODUCT_OWNER_REQUEST | RECOVERY | OTHER_APPROVED_ORIGIN"
requested_by: "auditable requester"
approval_reference: "durable Product Owner approval reference or null"
approved_at: "timestamp or null"
created_by: "AI_BRIDGE"
created_at: "timestamp"
updated_at: "timestamp"
content_hash: "canonical generated scope hash"
```

The implementation may choose equivalent field names, but it must keep lifecycle status separate from execution authorization. It must not encode both concepts only in a fragile free-text value such as:

```text
APPROVED FOR CODEX EXECUTION
```

Legacy Sprint documents using that exact status string must remain readable during migration.

## 5. Work Item document schema

The existing Sprint 010 Work Item requirements remain authoritative. AI Bridge must also generate the canonical repository representation of a Work Item from its structured record.

The generated Work Item document must contain at minimum:

- stable Work Item identifier;
- project and optional parent scope;
- origin;
- lifecycle status;
- work type, execution profile, urgency, and risks;
- requested outcome;
- in-scope and out-of-scope boundaries;
- acceptance checks;
- requester and approval reference;
- deterministic evidence root;
- immutable version or content hash;
- creation, approval, update, completion, cancellation, and supersession timestamps as applicable.

## 6. Generated document structure

For Sprint documents, AI Bridge must generate or validate a standard structure covering at minimum:

1. canonical metadata;
2. problem statement;
3. Product Owner decisions;
4. requested product outcome;
5. scope and out of scope;
6. architectural and governance requirements;
7. responsibilities and authority boundaries;
8. implementation obligations;
9. migrations and compatibility;
10. acceptance checks;
11. required proving executions;
12. Release Gates;
13. evidence requirements;
14. canonical documentation updates;
15. Definition of Done;
16. allowed terminal states.

A generated section may be empty only when the schema explicitly permits omission and a durable omission justification is recorded.

## 7. Lifecycle and operations

Implement governed capabilities equivalent to:

```text
scope.classify
sprint.propose
sprint.validate
sprint.approve
sprint.publish
sprint.get
sprint.supersede
work_item.propose
work_item.validate
work_item.approve
work_item.publish
work_item.get
work_item.supersede
```

Exact MCP or service names may differ, but the full lifecycle must exist.

Required lifecycle:

```text
natural-language request
→ semantic proposal
→ deterministic resolution
→ generated DRAFT
→ schema validation
→ PROPOSED
→ Product Owner approval binding where required
→ APPROVED
→ governed repository publication
→ immutable version/hash binding
→ eligible for Execution Context and contract generation
```

Publication and approval must be separate auditable transitions. A document may be rendered for review before approval, but it must not authorize execution until the required approval and publication rules pass.

## 8. Repository publication

AI Bridge must publish generated scope documents through a governed repository adapter.

Publication must:

- use deterministic repository paths and file names;
- reject identifier or path collisions;
- validate the current target branch and baseline rule;
- preserve unrelated repository content;
- record the resulting commit SHA;
- recompute and verify the published content hash;
- reject publication when the rendered document differs from the validated canonical payload;
- prevent an Execution Provider from publishing or approving its own authorization outside the governed Bridge flow.

The canonical Sprint path format should remain compatible with:

```text
docs/sprints/SPRINT_<number>_<UPPERCASE_SLUG>.md
```

unless a versioned migration deliberately replaces it.

## 9. Template, parser, and validation

Implement:

- a versioned Sprint schema;
- a versioned Work Item schema;
- one canonical parser per document type;
- one canonical renderer per document type;
- one shared validation service used by repository publication, Project Context resolution, Execution Context generation, contract generation, tests, and CI;
- canonical templates owned by AI Bridge;
- deterministic validation error codes;
- legacy parsing for historical documents without rewriting their immutable content.

The current independent regular-expression approval check in execution-context construction must not remain the canonical rule.

At minimum reject:

```text
INVALID_SCOPE_METADATA
UNSUPPORTED_SCOPE_SCHEMA
UNKNOWN_SCOPE_STATUS
UNKNOWN_EXECUTION_AUTHORIZATION
MISSING_PROJECT_ID
MISSING_REPOSITORY
MISSING_TARGET_BRANCH
MISSING_APPROVAL_REFERENCE
APPROVAL_REQUIRED
DUPLICATE_SCOPE_IDENTIFIER
SCOPE_PATH_COLLISION
SCOPE_HASH_MISMATCH
RENDERED_DOCUMENT_MISMATCH
```

## 10. CI and developer validation

Provide a command or equivalent automated interface for validating generated and legacy scope documents, for example:

```text
python manage.py validate_scopes
```

CI must validate every active or newly changed Sprint and Work Item document.

The validation must prove:

- schema correctness;
- enum correctness;
- identifier uniqueness;
- repository and branch consistency;
- required approval binding;
- canonical rendering consistency;
- content hash consistency;
- legacy compatibility where applicable.

An invalid generated scope document must fail before contract generation and before repository mutation is authorized.

## 11. Required proving executions

Add the following proofs to Sprint 010 evidence.

### 11.1 Natural-language Sprint generation

Use a predetermined Product Owner request describing a coordinated multi-outcome platform change.

Prove:

1. the LLM produces only a structured advisory proposal;
2. deterministic policy classifies the request as Sprint-level scope;
3. AI Bridge allocates the Sprint identifier;
4. AI Bridge renders the canonical Sprint document;
5. schema validation passes;
6. Product Owner approval is durably bound;
7. AI Bridge publishes the document;
8. the published content hash matches the canonical scope version;
9. Execution Context accepts the generated Sprint without relying on a free-text exact-status regex;
10. a contract can be generated from the published approved scope.

### 11.2 Invalid LLM-authored Markdown rejection

Submit an LLM-authored free-form Sprint Markdown document containing a semantically plausible but unsupported status value.

Expected result:

```text
REJECTED — INVALID_SCOPE_METADATA
```

It must not become executable authority merely because its prose contains the word `APPROVED`.

### 11.3 Invalid enum rejection

Attempt to publish a generated Sprint with an unknown status or execution-authorization enum.

Expected result:

```text
REJECTED — UNKNOWN_SCOPE_STATUS
```

or:

```text
REJECTED — UNKNOWN_EXECUTION_AUTHORIZATION
```

### 11.4 Renderer/parser round-trip

Prove:

```text
canonical scope record
→ generated Markdown
→ canonical parser
→ equivalent normalized scope record
```

The normalized record and content hash must remain stable.

### 11.5 Legacy compatibility

Prove that Sprint 009 and the bootstrap version of Sprint 010 remain readable under the legacy adapter without rewriting their historical content.

## 12. Documentation obligations

Update:

- the Constitution to state that AI Bridge owns canonical executable-scope generation and publication;
- `AGENTS.md` to state that executors consume Bridge-generated scopes and contracts rather than authoring their own authority;
- architecture documentation for semantic proposal, canonical generation, approval, publication, and contract issuance;
- MCP and service documentation;
- repository templates and validation commands;
- AKB current state;
- roadmap;
- README where the Product Owner flow is described.

The documentation must make clear:

> The Product Owner explains the intended outcome. The LLM proposes a structured interpretation. AI Bridge creates and validates the factory-compliant planning and execution documents. The Execution Provider implements only the issued authorization.

## 13. Additional evidence requirements

Add at minimum:

```text
CANONICAL_SCOPE_DOCUMENT_MODEL.md
SPRINT_GENERATION_PROOF.md
INVALID_SCOPE_DOCUMENT_PROOFS.md
scope-generation-results.json
```

Evidence must bind:

- original Product Owner request;
- LLM proposal;
- deterministic policy result;
- canonical scope record;
- generated Markdown hash;
- approval reference;
- publication commit;
- parsed published representation;
- Execution Context acceptance;
- generated contract identifier.

## 14. Additional Definition of Done

Sprint 010 is not complete until:

- AI Bridge can generate canonical Sprint documents from validated structured requests;
- AI Bridge can generate canonical Work Item documents from validated structured requests;
- free-form LLM or executor-authored Markdown is not authoritative;
- Sprint and Work Item schemas are versioned and centrally validated;
- lifecycle status and execution authorization are represented separately;
- publication creates a durable repository commit and immutable scope version;
- approval is durable, auditable, and validated before execution eligibility;
- Execution Context and contract generation use the canonical parser and scope record rather than an isolated exact-string regex;
- invalid metadata and unsupported enum values are deterministically rejected;
- CI validates active and changed scope documents;
- historical Sprint and contract compatibility remains intact;
- the natural-language-to-generated-Sprint proof passes;
- Constitution, AGENTS, architecture, AKB, roadmap, and user-facing documentation are synchronized;
- after this migration, normal Product Owner operation no longer requires manual Sprint Markdown authoring.

## 15. Final product outcome

The target experience is:

```text
Product Owner: explains what outcome is needed.
LLM: interprets and proposes structured intent.
AI Bridge: generates, validates, approves, publishes, versions, and contracts the work in factory-compliant form.
Execution Provider: consumes the issued contract and implements the bounded scope.
```

Sprint 010 should therefore be the final Sprint that requires manual authoring solely because AI Bridge cannot yet generate its own canonical planning and executable-scope documents.

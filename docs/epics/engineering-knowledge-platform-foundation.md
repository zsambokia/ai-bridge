# EPIC: Engineering Knowledge Platform Foundation

**Status:** Proposed / Ready for Codex audit and execution planning  
**Repository:** `zsambokia/ai-bridge`  
**Tracking issue:** GitHub Issue #10  
**Canonical specification:** this document  
**Primary owner:** Product Owner  

---

## 1. Objective

Build the Engineering Knowledge Platform as a first-class capability under the AI Bridge umbrella.

The platform must provide a structured, governed, searchable and writable engineering memory for AI Bridge itself and for every project managed through AI Bridge.

The result must support both humans and AI agents, especially ChatGPT and Orki, in:

- understanding current architecture and product state;
- planning future development;
- searching verified engineering knowledge;
- updating governed planning and design artifacts;
- connecting incidents, releases, sprints and decisions to reusable knowledge;
- proving which knowledge was used during an engineering decision.

This is not a traditional wiki project. It is a governed engineering knowledge and authoring platform.

---

## 2. Strategic vision

Everything belongs under the AI Bridge umbrella.

AI Bridge must maintain a highest-level Platform AKB containing the principles, constitution, governance model, orchestrator operating rules and reusable engineering know-how of AI Bridge.

Every project must also have its own isolated Project AKB containing application-specific knowledge.

Orki and other governed agents must consume knowledge through a deterministic and auditable Context Package composed from:

```text
Platform AKB
+ Project AKB
+ Current Work Context
+ Role Retrieval Profile
```

The knowledge platform must support two equally important capabilities:

1. **Knowledge Retrieval** — search, read, filter and assemble trusted context.
2. **Engineering Authoring** — create, modify and upsert governed planning and design artifacts through ChatGPT and MCP.

---

## 3. Mandatory knowledge scopes

### 3.1 Platform AKB

The Platform AKB is globally available within the AI Bridge umbrella and must contain at least:

- AI Bridge constitution;
- engineering principles;
- authority and approval framework;
- governance rules;
- Orki operating model;
- context isolation rules;
- provider-neutrality principles;
- release and quality gates;
- security principles;
- reusable engineering standards and know-how;
- shared runbooks and platform-level known issues.

Platform knowledge may be inherited by projects but must remain distinguishable from project-specific knowledge.

### 3.2 Project AKB

Each project has an isolated Project AKB containing at least:

- application purpose and boundaries;
- application capabilities;
- features;
- components;
- services;
- APIs;
- integrations;
- data flows;
- system designs;
- UI plans;
- roadmap items;
- architecture decisions;
- runbooks;
- known issues;
- release and operational knowledge.

Project knowledge must never leak across project contexts.

### 3.3 Work Memory

Work Memory contains evidence and temporary context associated with current engineering work, including:

- Epic;
- Sprint;
- Issue;
- Incident;
- Remediation;
- Release;
- Audit;
- Gate;
- Evidence package.

Work Memory is not automatically trusted long-term knowledge. It may generate Knowledge Candidates that must pass review before activation.

### 3.4 Role Views

The same underlying knowledge must be retrievable through role-specific views, including at least:

- PRODUCT;
- DEV;
- APP;
- SUPPORT;
- OPS.

Role Views are projections, not duplicated knowledge stores.

---

## 4. Engineering Authoring as a first-class capability

The system must explicitly support governed search, modification and upsert for the following artifact families:

### 4.1 Constitution

ChatGPT must be able to:

- search the active constitution;
- retrieve a specific section;
- propose a new section or amendment;
- modify an existing section;
- upsert a constitution section;
- show the impact of a proposed amendment;
- submit changes into the existing approval and audit process;
- preserve version history and provenance.

Constitution changes are always high-governance state changes and must never be silently activated.

### 4.2 Roadmap

Roadmap must become a first-class knowledge object rather than only a Markdown page or GitHub Issue.

ChatGPT must be able to:

- list roadmap items;
- search by application, feature, status, horizon or dependency;
- create a roadmap item;
- modify a roadmap item;
- upsert a roadmap item;
- link roadmap items to applications, features, epics, sprints and GitHub work items;
- identify gaps, duplicates and conflicts;
- assist large-scale planning;
- propose sequencing and dependencies;
- preserve Product Owner authority over activation and prioritization.

The AKB roadmap is the planning source of truth. GitHub remains the execution and tracking system.

### 4.3 UI plans

UI plans must be governable knowledge objects.

ChatGPT must be able to:

- search UI plans by application, screen, workflow or component;
- retrieve current approved UI plans;
- create or modify UI plan entries;
- upsert screen specifications;
- link UI plans to features, components, requirements and implementation issues;
- distinguish proposed, approved, implemented and obsolete designs;
- retain history and source references.

### 4.4 System designs

System and architecture designs must be governable knowledge objects.

ChatGPT must be able to:

- search and retrieve system designs;
- create a new design proposal;
- modify or upsert an existing design;
- connect designs to components, services, APIs, integrations and ADRs;
- show affected applications and work items;
- preserve review, approval, versioning and provenance;
- expose stale or conflicting designs.

---

## 5. Core platform concepts

### 5.1 KnowledgeEntry

The implementation must introduce a structured knowledge entity. The exact model may be refined during audit, but the minimum expected attributes are:

```text
id
platform_context_id
project_context_id
scope
knowledge_type
title
content
source_type
source_reference
status
verification_status
freshness_status
knowledge_owner_role
is_must_know
created_at
updated_at
verified_at
review_due_at
```

The model must support both Platform and Project scope and allow future extension without forcing a knowledge graph in Sprint 1.

### 5.2 Knowledge relationships

Sprint 1 may use targeted relations only. Sprint 2 must introduce a normalized relationship model connecting knowledge to:

- Application;
- Feature;
- Component;
- Service;
- API;
- Integration;
- Roadmap Item;
- Epic;
- Sprint;
- Incident;
- Release;
- ADR;
- UI Plan;
- System Design;
- Evidence.

### 5.3 Knowledge lifecycle

Minimum lifecycle:

```text
Candidate
-> In Review
-> Approved
-> Active
-> Watch
-> Review Due
-> Stale
-> Superseded or Archived
```

Automatic processes may create candidates, but must not publish trusted knowledge without the required review and approval.

### 5.4 Provenance and versioning

Every entry and mutation must record:

- source;
- actor;
- previous version;
- new version;
- timestamp;
- approval reference when required;
- linked work and evidence;
- reason for change.

---

## 6. Context Package

Orki must not directly assemble arbitrary knowledge through uncontrolled file reads.

The knowledge platform must provide a deterministic Context Package.

### 6.1 Input

```text
platform_context_id
project_context_id
work_context_id
role_context_id
query or task intent
```

### 6.2 Minimum output

```text
platform_must_know
project_must_know
work_related
role_relevant
stale_warnings
source_entry_ids
package_hash
generated_at
```

### 6.3 Requirements

- deterministic for equivalent inputs and repository/database state;
- context-isolated;
- auditable;
- contains source entry identifiers;
- warns about stale or unverified knowledge;
- produces a package hash so later audits can prove what Orki saw;
- supports progressive improvement of retrieval without breaking the contract.

---

## 7. MCP requirements

MCP is a mandatory delivery channel of this Epic.

The primary user experience must allow the Product Owner and other authorized users to manage engineering knowledge naturally through ChatGPT.

### 7.1 MCP design principles

- simple natural-language use through ChatGPT;
- context-bound and fail-closed;
- structured responses;
- explicit read and write separation;
- idempotent upsert where applicable;
- approval-aware state changes;
- full audit trail;
- backward compatibility where practical;
- provider-neutral backend contracts.

### 7.2 Mandatory read tools

At minimum:

```text
akb.search
akb.get_entry
akb.get_context_package
akb.list_review_queue
akb.get_application
akb.get_feature
akb.get_component
roadmap.list
roadmap.get_item
constitution.get
ui_plan.search
system_design.search
```

### 7.3 Mandatory authoring tools

At minimum:

```text
akb.create_candidate
akb.update_candidate
akb.upsert
akb.review_candidate
roadmap.create_item
roadmap.update_item
roadmap.upsert_item
roadmap.link_item
constitution.propose_amendment
constitution.upsert_section
ui_plan.create
ui_plan.update
ui_plan.upsert
system_design.create
system_design.update
system_design.upsert
```

The implementation may consolidate tools into resource-oriented operations if this improves consistency, but all listed user capabilities must remain available.

### 7.4 Required context fields

Every project-bound call must require or resolve:

```text
platform_context_id
project_context_id
```

Work-bound calls must also include:

```text
work_context_id
```

Role-specific retrieval must include:

```text
role_context_id
```

No cross-project fallback is allowed.

### 7.5 Audit event requirements

Each MCP knowledge operation must record at least:

```text
actor
tool_name
operation_type
platform_context_id
project_context_id
work_context_id
role_context_id
input_reference
returned_or_modified_entry_ids
context_package_hash
approval_reference
timestamp
result
```

### 7.6 Backward compatibility

Existing document-oriented AKB operations may remain temporarily as deprecated adapters.

They must not remain the canonical implementation for new Orki or ChatGPT flows.

---

## 8. Sprint structure

This Epic is delivered in two sequential Sprints.

Sprint 2 must not begin until Sprint 1 passes the existing Engineering Audit Gate.

The current self-healing and audit capabilities of AI Bridge must be reused. The implementation must first determine whether the required audit gate already exists and is suitable. A duplicate audit subsystem must not be created without justification.

---

# Sprint 1 — AKB Foundation and ChatGPT Management

## 9. Sprint 1 objective

Establish the smallest production-worthy vertical slice that proves:

- Platform and Project AKB separation;
- structured knowledge storage;
- deterministic Context Package generation;
- ChatGPT-compatible MCP search and authoring;
- controlled incident-to-knowledge lifecycle;
- auditability and context isolation;
- integration with the existing Engineering Audit Gate.

Sprint 1 must include an audit of any existing partial implementation before new work begins.

---

## 10. Sprint 1 mandatory work

### 10.1 Existing implementation audit

Codex must first inspect the repository and verify what already exists.

The audit must cover:

- current AKB implementation;
- current document search implementation;
- current data models and migrations;
- current MCP tools;
- current Orki context assembly;
- current audit and self-healing gates;
- current approval model;
- existing roadmap, constitution, UI and system-design representations;
- reusable concepts from the `artificial-software-factory` repository where accessible and relevant.

Codex must not assume Sprint 1 is missing or complete.

It must produce a gap matrix:

```text
Requirement
Existing implementation
Status: PASS / PARTIAL / MISSING / CONFLICTING
Required remediation
Evidence
```

### 10.2 Remediation-first rule

When an existing implementation is incomplete or inconsistent, Codex must:

1. identify the gap;
2. repair or complete the existing implementation;
3. avoid parallel duplicate subsystems;
4. run required tests and gates;
5. produce evidence;
6. re-run the audit.

### 10.3 Platform and Project scopes

Implement or verify two explicit knowledge scopes:

```text
PLATFORM
PROJECT
```

Platform knowledge must be automatically available in valid project contexts.

Project knowledge must remain strictly isolated.

### 10.4 Structured knowledge entity

Implement or verify the minimum `KnowledgeEntry` model and lifecycle fields required by this Epic.

### 10.5 Basic search

Implement metadata-filtered text search supporting at least:

- scope;
- project;
- knowledge type;
- status;
- verification status;
- freshness status;
- role profile;
- free-text query.

Sprint 1 does not require vector search or a general semantic knowledge graph.

### 10.6 Context Package

Implement `akb.get_context_package` or an equivalent MCP operation with the contract defined above.

### 10.7 Orki integration

Orki must consume the Context Package for governed engineering work.

The integration must record the resulting package hash and entry IDs.

### 10.8 Incident-to-knowledge flow

Implement one automatic knowledge acquisition flow:

```text
Incident closed
-> Knowledge Candidate
-> Review
-> Approved
-> Active KnowledgeEntry
```

No direct automatic activation is allowed.

### 10.9 ChatGPT management foundation

Through MCP, ChatGPT must be able to:

- search knowledge;
- read entries;
- create a candidate;
- modify or upsert an authorized planning/design candidate;
- list review items;
- review or submit a review decision where authorized;
- receive explicit approval requirements for protected mutations.

### 10.10 Initial Engineering Authoring support

Sprint 1 must provide a minimal but working authoring path for the four highlighted artifact families:

- Constitution;
- Roadmap;
- UI Plan;
- System Design.

It is acceptable for Sprint 1 to store these as specialized `KnowledgeEntry` types with validated schemas rather than full dedicated domain models.

The authoring path must already support:

- search;
- create;
- modify;
- idempotent upsert;
- versioning;
- provenance;
- review/approval integration.

---

## 11. Sprint 1 out of scope

Unless already present and reusable, Sprint 1 must not expand into:

- general-purpose knowledge graph;
- vector database or embeddings;
- autonomous direct publication;
- complete release ingestion;
- complete sprint ingestion;
- complete remediation ingestion;
- every possible role-specific UI;
- full knowledge freshness automation;
- duplicate Engineering Audit Gate implementation;
- broad UI redesign unrelated to proving the knowledge workflow.

---

## 12. Sprint 1 acceptance criteria

Sprint 1 is PASS only when all of the following are evidenced:

- [ ] Existing AKB and audit implementation was inspected before changes.
- [ ] A requirement gap matrix exists.
- [ ] Platform AKB and Project AKB are represented separately.
- [ ] Cross-project access fails closed.
- [ ] Structured knowledge entries exist with lifecycle and provenance.
- [ ] Metadata-filtered text search works.
- [ ] `akb.get_context_package` or equivalent works.
- [ ] Context packages include source IDs, stale warnings and a deterministic hash.
- [ ] Orki consumes the governed Context Package.
- [ ] Orki execution records the package hash.
- [ ] Incident closure can generate a Knowledge Candidate.
- [ ] Candidate publication requires review/approval.
- [ ] ChatGPT can search and read knowledge through MCP.
- [ ] ChatGPT can create, modify and upsert authorized knowledge through MCP.
- [ ] Constitution, Roadmap, UI Plan and System Design are supported as explicit knowledge types.
- [ ] Protected authoring operations are approval-aware.
- [ ] Audit events are generated for MCP reads and writes.
- [ ] Unit, integration and context-isolation tests pass.
- [ ] Existing Engineering Audit Gate returns PASS.

---

## 13. Sprint 1 gate rule

```text
Sprint 2 MUST NOT START unless Sprint 1 audit result is PASS.
```

If the audit returns PARTIAL or FAIL:

```text
1. Identify every gap.
2. Repair or complete the implementation.
3. Run tests and required gates.
4. Produce fresh evidence.
5. Re-run the Engineering Audit Gate.
6. Repeat until PASS.
7. Start Sprint 2 only after PASS.
```

The system's existing self-healing workflow should perform this remediation loop where it is already capable and authorized to do so.

---

# Sprint 2 — Engineering Memory and Planning Platform

## 14. Sprint 2 objective

Expand the validated foundation into a normalized engineering memory that actively supports product planning, application understanding and lifecycle ingestion.

---

## 15. Sprint 2 mandatory work

### 15.1 Application capability model

Introduce or verify normalized entities for:

- Application;
- Capability;
- Feature;
- Component;
- Service;
- API;
- Integration.

The model must answer questions such as:

- What can this application currently do?
- Which feature implements a capability?
- Which components and APIs support the feature?
- Which integrations are involved?
- What is planned, implemented, deprecated or missing?

### 15.2 Relationship model

Introduce typed relationships among knowledge, application entities and work items.

Examples:

```text
FEATURE IMPLEMENTED_BY COMPONENT
COMPONENT EXPOSES API
FEATURE DEPENDS_ON INTEGRATION
ROADMAP_ITEM TARGETS FEATURE
SPRINT DELIVERS ROADMAP_ITEM
INCIDENT AFFECTS COMPONENT
RUNBOOK RESOLVES KNOWN_ISSUE
UI_PLAN DESIGNS FEATURE
SYSTEM_DESIGN DEFINES COMPONENT
ADR DECIDES SYSTEM_DESIGN
```

### 15.3 Lifecycle ingestion

Add event-based ingestion from at least:

- Sprint completion;
- Release completion;
- Engineering Gate result;
- Remediation completion;
- Incident resolution.

Events should create or update candidates and relationships, not bypass governance.

### 15.4 Roadmap as a first-class domain

Implement dedicated roadmap behavior sufficient for large-scale planning:

- hierarchy and grouping;
- planning horizon;
- status;
- priority;
- dependencies;
- target application and feature;
- desired outcome;
- acceptance criteria;
- risk;
- linked GitHub epic, sprint and issue references;
- upsert and conflict detection;
- versioning and Product Owner approval.

### 15.5 Dedicated Constitution support

Promote Constitution from generic knowledge type to a governed section model if the Sprint 1 representation is insufficient.

Required capabilities:

- section-level retrieval;
- amendment proposals;
- impact analysis;
- version diff;
- approval chain;
- effective version;
- historical versions.

### 15.6 Dedicated UI Plan support

Promote UI plans into a structured model if needed, including:

- application;
- screen or workspace;
- user role;
- workflow;
- states;
- components;
- linked feature;
- design status;
- implementation status;
- source assets and references.

### 15.7 Dedicated System Design support

Promote system designs into a structured model if needed, including:

- scope and boundaries;
- components and services;
- APIs and contracts;
- data model and flows;
- integrations;
- security and operational concerns;
- alternatives and decisions;
- linked ADRs;
- implementation and review status.

### 15.8 Role-specific retrieval

Implement retrieval profiles for:

- PRODUCT;
- DEV;
- APP;
- SUPPORT;
- OPS.

Profiles influence relevance and presentation but must not bypass authorization.

### 15.9 Planning assistance

ChatGPT must be able to assist with planning by:

- comparing roadmap to current capabilities;
- identifying missing prerequisites;
- proposing Epics and Sprints;
- detecting conflicting or duplicate roadmap items;
- showing affected architecture and UI plans;
- linking proposed work to existing knowledge and evidence;
- creating or updating roadmap items through governed MCP operations.

---

## 16. Sprint 2 acceptance criteria

Sprint 2 is PASS only when:

- [ ] Application, Feature, Component, Service, API and Integration entities are queryable.
- [ ] Typed relationships are implemented and tested.
- [ ] Sprint, Release, Gate, Remediation and Incident events can create knowledge candidates.
- [ ] Roadmap is a first-class planning object.
- [ ] ChatGPT can search, create, modify and upsert roadmap items through MCP.
- [ ] ChatGPT can propose and manage Constitution amendments through MCP.
- [ ] ChatGPT can search, create, modify and upsert UI plans through MCP.
- [ ] ChatGPT can search, create, modify and upsert System Designs through MCP.
- [ ] Role-specific retrieval works without weakening context isolation.
- [ ] Current application capabilities can be queried.
- [ ] Known issues can be traced to components, runbooks and incidents.
- [ ] Roadmap items can be traced to Epics, Sprints and GitHub issues.
- [ ] All authoring operations preserve provenance, versioning and audit history.
- [ ] All protected mutations respect authority and approval rules.
- [ ] Integration and isolation test suites pass.
- [ ] Engineering Audit Gate returns PASS.

---

## 17. GitHub and repository integration

### 17.1 Source-of-truth responsibilities

```text
AKB Roadmap
= planning source of truth

GitHub Issue / Epic
= tracking, discussion and execution coordination

Repository Epic specification
= versioned canonical delivery scope

Sprint specifications
= executable delivery contracts

Evidence artifacts
= proof of completion
```

### 17.2 Required cross-links

This document must link to GitHub Issue #10.

Issue #10 must link back to:

```text
docs/epics/engineering-knowledge-platform-foundation.md
```

Future Sprint issues or documents must link to this Epic.

### 17.3 GitHub synchronization

The platform may later synchronize roadmap and work items with GitHub, but GitHub must not silently override the AKB planning source of truth.

Conflicts must be surfaced for review.

---

## 18. Non-functional requirements

### 18.1 Security and isolation

- fail-closed context resolution;
- strict project isolation;
- authority checks for writes;
- protected Constitution and roadmap operations;
- immutable audit events or equivalent tamper-evident controls;
- no silent cross-context fallback.

### 18.2 Reliability

- idempotent upserts;
- deterministic Context Packages;
- transactionally safe mutations;
- retry-safe MCP write operations;
- explicit conflict response rather than silent overwrite.

### 18.3 Maintainability

- provider-neutral domain services;
- MCP as an adapter, not the domain core;
- no duplicate AKB subsystem when existing functionality can be extended;
- migrations and contracts documented;
- tests organized by domain and context boundary.

### 18.4 Observability

- searchable audit events;
- mutation and retrieval metrics;
- failed authorization and isolation events;
- Context Package generation metrics;
- stale knowledge and review queue metrics.

### 18.5 Performance

Sprint 1 may use database-backed full-text or practical indexed text search.

The design must leave room for semantic retrieval later without making vector infrastructure a prerequisite.

---

## 19. Testing requirements

At minimum:

### Unit tests

- lifecycle transitions;
- scope rules;
- upsert idempotency;
- version creation;
- approval enforcement;
- package hashing;
- freshness classification.

### Integration tests

- ChatGPT/MCP read flows;
- ChatGPT/MCP write flows;
- Orki Context Package usage;
- incident-to-candidate flow;
- roadmap authoring flow;
- constitution amendment flow;
- UI plan authoring flow;
- system design authoring flow.

### Isolation and security tests

- cross-project search denial;
- cross-project entry access denial;
- invalid work context denial;
- unauthorized protected upsert denial;
- stale approval reference denial;
- audit event completeness.

### Regression tests

- existing AKB document operations during deprecation period;
- existing Engineering Audit Gate;
- existing Orki execution path;
- current governance and approval flows.

---

## 20. Evidence requirements

Each Sprint must produce evidence including:

- repository commit or PR references;
- migration references;
- API and MCP contracts;
- automated test results;
- context-isolation test results;
- audit event samples;
- example Context Package and hash;
- example ChatGPT search interaction;
- example ChatGPT upsert interaction;
- example approval-required response;
- Engineering Audit Gate result;
- gap matrix and remediation record.

Evidence must be sufficient for an independent reviewer to verify every acceptance criterion.

---

## 21. Codex execution rules

Codex must follow this sequence:

```text
1. Read repository instructions, including all applicable AGENTS.md files.
2. Inspect the existing AI Bridge AKB, MCP, Orki, governance and audit implementation.
3. Determine whether Sprint 1 is already partially or fully implemented.
4. Produce the Sprint 1 requirement gap matrix.
5. Repair, complete or refactor existing implementation rather than duplicating it.
6. Run all required tests and Engineering Audit Gates.
7. Continue remediation until Sprint 1 is PASS.
8. Produce evidence for Sprint 1.
9. Only then begin Sprint 2.
10. Implement Sprint 2 incrementally with tests and evidence.
11. Run the final Engineering Audit Gate.
12. Stop and report BLOCKED only when a genuine Product Owner or authority decision is required.
```

Codex must not:

- skip the existing implementation audit;
- create a second audit system without proving the current one is unsuitable;
- start Sprint 2 before Sprint 1 PASS;
- bypass approval for protected state changes;
- silently replace existing knowledge;
- treat GitHub Issue text as the only locally available specification;
- claim completion without evidence.

---

## 22. Completion definition

This Epic is complete when:

1. Sprint 1 and Sprint 2 both pass the Engineering Audit Gate.
2. AI Bridge has distinct Platform and Project AKBs.
3. Orki consumes deterministic and auditable Context Packages.
4. ChatGPT can easily search and manage the knowledge base through MCP.
5. ChatGPT can create, modify and upsert Constitution, Roadmap, UI Plan and System Design knowledge through governed operations.
6. Roadmap supports large-scale planning and links to GitHub execution objects.
7. Application capabilities and engineering relationships are queryable.
8. Lifecycle events generate governed knowledge candidates.
9. Provenance, versioning, approval and audit are enforced.
10. All required evidence is available and independently reviewable.

---

## 23. Future extensions explicitly outside this Epic

The following may be planned after this Epic:

- semantic/vector retrieval;
- knowledge graph visualization;
- automatic drift detection across code and knowledge;
- advanced planning simulation;
- automatic roadmap recommendation scoring;
- cross-project reusable pattern mining;
- external customer-facing knowledge projections;
- rich graphical AKB administration UI.

These extensions must build on the domain contracts created by this Epic rather than bypass them.

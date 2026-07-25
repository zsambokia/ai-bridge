# Sprint 004 — Basic AKB and MCP Grounded Context

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Target branch:** `main`  
**Date:** 2026-07-25

## 1. Product Owner intent

Keep AI Bridge focused on the immediate product goal:

```text
ChatGPT
→ MCP Bridge
→ basic tools and skills
→ selected Project
→ repository-backed context
→ grounded response or governed execution
```

This sprint must establish only the smallest useful AKB capability required for ChatGPT to retrieve current, project-scoped repository knowledge through MCP. It must not create a general knowledge graph, deep Discovery platform, autonomous documentation engine, organization simulator, or speculative multi-tenant abstraction.

## 2. Binding governance

Read and obey:

- `AGENTS.md`
- `docs/constitution/BRIDGE_CONSTITUTION.md`
- `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`
- `.bridge/project.yaml`
- `docs/akb/CURRENT_STATE.md`
- `docs/roadmap/ROADMAP.md`

Implementation is not completion. Execute assessment, implementation, required validation, AKB/documentation synchronization, final evidence, commit and honest closure.

## 3. Assessment-first requirement

Before writing new code, inspect the existing implementation and identify reusable AKB, Project Context, MCP, repository and search capabilities.

At minimum inspect:

- current Django applications and models;
- current MCP server and tool registration;
- existing Project Registry and Project Context implementation;
- existing AKB synchronization, storage, search and chat-context services;
- existing repository adapters;
- related tests and commands.

The evidence must state:

- what already existed;
- what was reused;
- what was repaired or extended;
- why any new component was necessary.

Creating a parallel AKB or context system is forbidden unless the assessment proves that the existing canonical responsibility cannot be safely extended.

## 4. In scope

Implement or complete the minimal project-scoped capability equivalent to:

1. **AKB synchronization** from selected Project repository documents.
2. **AKB search** restricted to the selected Project.
3. **Grounded context retrieval** for an MCP caller.
4. **Freshness reporting** against repository state.
5. **Source attribution** using repository-relative paths and commit identity.
6. **Idempotent synchronization** without duplicate indexed records.
7. **MCP exposure** through the existing canonical server and tool registration.

Prefer existing models and services. Exact public names must follow current repository conventions.

## 5. Repository remains source of truth

The repository is the canonical durable knowledge source.

The database may contain a searchable operational index, but it must not become an independently authored source of project truth.

A minimal indexed item must retain the equivalent of:

- selected Project identity;
- repository identity;
- repository-relative path;
- document type or category;
- searchable content or bounded extracted content;
- deterministic content hash;
- indexed source commit;
- successful indexed timestamp;
- active/deleted state when required by the existing design.

Do not create inferred project facts that are unsupported by repository content.

## 6. Initial document coverage

Index eligible text documentation from existing Project paths, including where present:

- `AGENTS.md`
- `.bridge/project.yaml`
- `README.md`
- `docs/constitution/**`
- `docs/roadmap/**`
- `docs/architecture/**`
- `docs/akb/**`
- `docs/sprints/**`
- `docs/workflows/**`
- `docs/contracts/**`
- `docs/operations/**`
- `docs/evidence/**`

The implementation must safely skip binary, oversized, dependency, generated and out-of-repository paths. Missing optional directories are not errors.

## 7. Synchronization contract

The project-scoped synchronization operation must:

1. require or resolve one explicit selected Project;
2. resolve its canonical repository and current HEAD;
3. discover eligible repository documents;
4. hash content deterministically;
5. create new indexed records;
6. update changed records without duplication;
7. exclude or deactivate deleted source records;
8. preserve isolation between Projects;
9. record the exact successfully indexed repository state;
10. return structured created, updated, unchanged, removed, skipped and error counts.

Running twice against unchanged content and the same repository state must produce no duplicates and no false updates.

A partial or failed synchronization must not mark the AKB current.

## 8. Freshness

Expose at least these equivalent states:

```text
CURRENT
STALE
NEVER_SYNCED
UNAVAILABLE_OR_ERROR
```

Freshness must be based on repository identity and commit evidence, not time alone.

Expose at least:

- current repository HEAD when available;
- last successfully indexed commit;
- last successful synchronization time;
- resolved freshness state.

Request-triggered or explicit synchronization is sufficient. Webhooks and background scheduling are out of scope.

## 9. MCP operations

Expose through the existing MCP surface the equivalent of:

### Project AKB synchronization

```text
project.akb_sync(project)
```

Return Project, repository, source commit, result counts, errors and final freshness.

### Project AKB search

```text
project.akb_search(project, query, limit?)
```

Return ranked Project-isolated results containing title, repository-relative path, category, relevant bounded excerpt, source commit and freshness.

Simple deterministic keyword or database full-text search is sufficient. Do not add a vector database solely for this sprint.

### Grounded Project context

```text
project.get_grounded_context(project, question, limit?)
```

Return a bounded grounding package containing:

- Project identity;
- repository identity;
- question;
- current repository HEAD when available;
- AKB freshness;
- selected source paths;
- indexed source commits;
- bounded excerpts or summaries.

The tool need not generate the final conversational answer. It must provide the trustworthy material from which ChatGPT can answer without relying on hidden model memory.

If no relevant source exists, return an honest empty result. If knowledge is stale, report that explicitly.

## 10. Out of scope

Do not implement:

- repository-wide code or component graph;
- capability or dependency knowledge graph;
- automatic architecture reconstruction;
- autonomous roadmap changes;
- automatic rewriting of Constitution, Vision or Roadmap;
- semantic embedding platform or vector database;
- webhook or scheduler infrastructure;
- general Discovery engine;
- large new UI;
- parallel project-context architecture;
- autonomous Codex dispatch beyond existing capabilities.

## 11. Required tests

Prove at least:

1. Project isolation between two Project records or repository-backed test Projects;
2. first synchronization creates expected records;
3. repeated unchanged synchronization is idempotent;
4. changed content updates without duplication;
5. deleted source content disappears from search;
6. excluded and binary files are skipped;
7. freshness moves to CURRENT only after successful synchronization;
8. failed synchronization cannot claim CURRENT;
9. search returns source path and commit metadata;
10. grounded context is bounded and source-attributed;
11. irrelevant search returns no invented content;
12. MCP operations are registered and reachable through the canonical MCP surface.

Use real service boundaries. Direct ORM fixture insertion alone is not acceptance evidence.

## 12. Acceptance scenario

Through the canonical service or MCP path:

1. select AI Bridge;
2. synchronize its AKB;
3. search for the Bridge purpose or Constitution closure requirement;
4. prove returned sources belong to `zsambokia/ai-bridge`;
5. retrieve grounded context for a Project question;
6. prove source paths and freshness are present;
7. rerun unchanged synchronization and prove idempotency;
8. prove no cross-Project records are returned.

Where a second real Project is unavailable, use a repository-backed integration test Project and report this limitation honestly.

## 13. Documentation and evidence

Update concise operational documentation for synchronization, search, freshness and MCP grounded-context use.

Create sprint evidence under:

```text
docs/evidence/sprint-004-basic-akb-mcp-context/
```

Required outputs:

- `CLOSURE_REPORT.md`
- `acceptance-results.json`

Evidence must include assessment, reuse decisions, changed components, MCP schemas or examples, exact validation commands, isolation, idempotency, freshness results, all gate results, baseline SHA, final commit SHA and final terminal state.

## 14. Required Release Gates

Repository-wide gates from `.bridge/project.yaml`:

```text
pytest
ruff check .
mypy .
```

Sprint-specific validation must include focused AKB synchronization/search tests and canonical MCP registration/integration tests.

If executable or binding content changes after a gate, rerun every invalidated gate.

## 15. Allowed terminal states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

Ordinary implementation, test, lint, type, migration, MCP or evidence failures are repair work and are not valid external blockers.

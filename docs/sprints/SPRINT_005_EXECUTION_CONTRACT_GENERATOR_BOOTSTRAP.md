# Sprint 005 — Execution Contract Generator Bootstrap

**Status:** APPROVED FOR CODEX EXECUTION  
**Project:** AI Bridge  
**Repository:** `zsambokia/ai-bridge`  
**Target branch:** `main`  
**Task type:** SELF_DEVELOPMENT  
**Date:** 2026-07-25

## 1. Purpose

Implement the smallest canonical Execution Contract Generator required to remove manual handoff ping-pong.

This sprint exists only to make the approved handoff flow executable:

```text
selected Project
+ Project definition
+ valid Project Context or explicitly supported bootstrap eligibility
+ approved Sprint
→ validate binding inputs
→ generate contract
→ issue immutable contract
→ render Codex handoff
```

After this sprint, manually composed implementation handoffs are no longer the normal execution path.

## 2. Binding context

Read before mutation:

1. `AGENTS.md`
2. `.bridge/project.yaml`
3. `docs/constitution/BRIDGE_CONSTITUTION.md`
4. `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`
5. `docs/workflows/EVIDENCE_DRIVEN_SPRINT.md`
6. `docs/akb/CURRENT_STATE.md`
7. this Sprint

## 3. Assessment first

Before writing code, inspect the current repository and identify existing reusable implementations for:

- Project Registry;
- Project definition parsing and validation;
- Project Context and immutable snapshots;
- repository identity and HEAD resolution;
- Sprint validation;
- release-gate resolution;
- evidence-path resolution;
- MCP tool registration;
- existing execution, handoff or audit models/services.

Reuse, repair or extend existing canonical responsibilities. Do not create a parallel Registry, Context or execution subsystem.

## 4. Approved scope

Implement the minimal backend capability required by `docs/contracts/HANDOFF_EXECUTION_CONTRACT.md`:

- `generate_execution_contract`;
- `validate_execution_contract`;
- `issue_execution_contract`;
- `get_execution_contract`;
- `render_execution_handoff`.

The implementation must:

1. require an explicit Project and approved Sprint path;
2. load `.bridge/project.yaml` or the canonical Project Registry configuration;
3. resolve repository, target branch and baseline commit;
4. resolve Constitution, workflow, roadmap, AKB and additional context paths;
5. resolve repository-wide and Sprint-specific release gates;
6. resolve deterministic evidence paths;
7. reject missing or contradictory binding inputs before issuance;
8. create a unique handoff identifier;
9. create a reproducible normalized contract hash;
10. store issued contracts immutably in the existing canonical persistence layer;
11. render human-readable handoff text only from the stored machine-readable payload;
12. expose the generator and contract retrieval through the existing canonical MCP surface.

## 5. Bootstrap boundary

This Sprint is authorized by a one-time Product Owner-issued Foundation Bootstrap Contract because the canonical generator does not yet exist.

This bootstrap authority applies only to implementation of the generator and its required tests, documentation and evidence. It does not authorize Sprint 004 Basic AKB work.

Once the generator passes all gates, Sprint 004 must start only from a generator-produced, validated and issued contract.

## 6. Required contract validation

Prove at least:

- repository mismatch fails closed;
- missing Sprint fails closed;
- Sprint without approved status fails closed;
- missing Constitution or workflow fails closed;
- baseline commit must exist in the target repository;
- Project and Sprint mismatch fails closed;
- required release gates are resolved from Project configuration;
- evidence paths are deterministic and collision-safe;
- issued payload is immutable;
- contract hash is reproducible;
- rendered handoff exactly reflects the stored payload;
- two requests produce unique handoff identifiers;
- the current AI Bridge Project can receive a valid issued contract for Sprint 004 after this Sprint is complete.

## 7. MCP acceptance

The canonical MCP surface must support the equivalent of:

```text
generate_execution_contract(project, sprint_path, task_type, intent)
issue_execution_contract(contract_or_draft_id)
get_execution_contract(handoff_identifier)
render_execution_handoff(handoff_identifier)
```

Exact names may follow repository conventions, but the complete flow must be testable through the same MCP server used by ChatGPT.

## 8. Out of scope

Do not implement:

- Basic AKB indexing or search from Sprint 004;
- Codex job execution itself beyond existing capabilities;
- generic workflow engine;
- new UI except minimal diagnostic/admin support when already conventional;
- webhook or scheduling infrastructure;
- speculative multi-tenant abstractions;
- unrelated platform capabilities.

## 9. Required release gates

Run and repair until PASS:

```text
pytest
ruff check .
mypy .
python -m scripts.release_gate
```

Also run focused Execution Contract service, persistence, integrity and MCP integration tests.

If repository-native commands differ after assessment, use the canonical commands and document the mapping.

## 10. Evidence

Create:

```text
docs/evidence/sprint-005-execution-contract-generator-bootstrap/CLOSURE_REPORT.md
docs/evidence/sprint-005-execution-contract-generator-bootstrap/acceptance-results.json
```

The evidence must include:

- baseline and final commit;
- existing components assessed and reused;
- final model/service/tool mapping;
- exact commands and results;
- negative validation results;
- reproducible contract hash proof;
- MCP acceptance evidence;
- a successfully generated and ISSUED Sprint 004 contract identifier and payload path;
- honest terminal state.

## 11. Completion condition

This Sprint is complete only when the generator itself produces the valid ISSUED Execution Contract for:

```text
docs/sprints/SPRINT_004_BASIC_AKB_MCP_CONTEXT.md
```

The generated Sprint 004 contract must bind the then-current valid repository baseline and must not reuse the manual bootstrap contract.

## 12. Allowed terminal states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

Ordinary code, test, lint, type, migration, configuration, evidence or malformed-handoff failures are repair work and are not valid external blockers.

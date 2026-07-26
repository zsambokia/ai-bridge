# Foundation Bootstrap Execution Contract — Sprint 005

**Lifecycle state:** ISSUED  
**Contract class:** ONE-TIME PRODUCT OWNER FOUNDATION BOOTSTRAP  
**Contract identifier:** `bridge:ai-bridge:sprint-005:foundation-bootstrap-2026-07-26`  
**Issued by:** Product Owner  
**Issued at:** 2026-07-26  
**May be consumed once:** yes

## 1. Purpose

Authorize exactly one governed Codex execution whose sole purpose is implementing and proving the canonical Execution Contract Generator defined by:

```text
docs/sprints/SPRINT_005_EXECUTION_CONTRACT_GENERATOR_BOOTSTRAP.md
```

This exceptional bootstrap authority exists because the canonical Generator does not yet exist and therefore cannot issue the contract required to implement itself.

It does not authorize Sprint 004 implementation directly.

## 2. Project binding

```yaml
project:
  id: ai-bridge
  slug: ai-bridge
  name: AI Bridge
  repository: zsambokia/ai-bridge
  definition_source: .bridge/project.yaml
  target_branch: main
  integration_target: main
```

The executor must verify that the repository-local Project definition matches these bindings before mutation.

## 3. Execution binding

```yaml
execution:
  task_type: SELF_DEVELOPMENT
  intent: Implement the smallest canonical Execution Contract Generator, expose it through the canonical MCP surface, and use it to issue the Sprint 004 contract.
  approved_sprint_path: docs/sprints/SPRINT_005_EXECUTION_CONTRACT_GENERATOR_BOOTSTRAP.md
  baseline_commit: 4a3260f25cfd2c708b4e71b5d414b4c745931345
  baseline_rule: DESCENDANT_OF
  worktree_policy: MAIN_ONLY
```

The checkout HEAD used for execution must be commit `4a3260f25cfd2c708b4e71b5d414b4c745931345` or a descendant containing this issued bootstrap contract and no contradictory binding changes.

## 4. Binding documents

Read and obey before mutation:

```text
AGENTS.md
.bridge/project.yaml
docs/constitution/BRIDGE_CONSTITUTION.md
docs/contracts/HANDOFF_EXECUTION_CONTRACT.md
docs/workflows/EVIDENCE_DRIVEN_SPRINT.md
docs/akb/CURRENT_STATE.md
docs/roadmap/ROADMAP.md
docs/sprints/SPRINT_005_EXECUTION_CONTRACT_GENERATOR_BOOTSTRAP.md
```

## 5. Required release gates

Repository-wide:

```text
pytest
ruff check .
mypy .
```

Sprint-specific:

```text
python -m scripts.release_gate
focused Execution Contract service tests
persistence and immutability tests
integrity and negative validation tests
canonical MCP registration and integration tests
```

If repository assessment proves a command name differs, use the canonical repository-native equivalent and record the mapping in evidence. No gate may be silently omitted.

## 6. Evidence binding

```text
docs/evidence/sprint-005-execution-contract-generator-bootstrap/CLOSURE_REPORT.md
docs/evidence/sprint-005-execution-contract-generator-bootstrap/acceptance-results.json
```

Evidence must bind the baseline, final commit, all gate results, generator architecture, MCP schemas, negative validation, contract hash reproducibility, and the generated Sprint 004 contract.

## 7. Mandatory completion artifact

Sprint 005 is incomplete unless the implemented Generator produces a validated and immutable `ISSUED` Execution Contract for:

```text
docs/sprints/SPRINT_004_BASIC_AKB_MCP_CONTEXT.md
```

That generated Sprint 004 contract must bind the then-current repository baseline, binding documents, gates, evidence path, contract identifier and reproducible contract hash.

## 8. Constraints

```yaml
constraints:
  preserve_unrelated_work: true
  direct_write_to_integration_target: true
  infer_active_project: false
  infer_active_sprint: false
  roadmap_authorizes_execution: false
  scope_expansion: false
  ordinary_technical_failure_is_blocker: false
```

This contract may not be reused for Sprint 004 or any other execution. It may not be interpreted as a new general contract mode. It is a one-time governance bridge authorized only for Generator self-development.

## 9. Allowed terminal states

```text
PASS — READY FOR PRODUCT OWNER REVIEW
BLOCKED — BUSINESS DECISION REQUIRED
BLOCKED — REQUIRED EXTERNAL INPUT UNAVAILABLE
```

Implementation, test, lint, type, migration, MCP registration, malformed-contract, or evidence failures are repair work and are not valid external blockers.

## 10. Consumption instruction

Codex must:

1. verify this contract is present on the execution checkout;
2. verify repository and Sprint bindings;
3. verify HEAD satisfies `DESCENDANT_OF 4a3260f25cfd2c708b4e71b5d414b4c745931345`;
4. mark this contract consumed in Sprint evidence when preflight begins;
5. execute Sprint 005;
6. finish by generating and issuing the Sprint 004 contract through the implemented Generator.

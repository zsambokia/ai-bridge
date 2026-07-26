# Sprint 004 — Manual Bootstrap Execution Contract

**Lifecycle status:** ISSUED  
**Contract mode:** FOUNDATION_BOOTSTRAP  
**Issued by:** Product Owner through repository governance  
**Handoff identifier:** `bridge:ai-bridge:sprint-004:foundation-bootstrap-20260726`  
**Issued at:** 2026-07-26  
**Single-use:** yes

## Purpose

This is a one-time repository-issued bootstrap contract for Sprint 004. It exists because Sprint 004 implements and proves the canonical Bridge context / execution-package generation path that will issue subsequent contracts. Requiring that unimplemented capability to issue its own prerequisite would create a circular dependency.

This contract does not create a reusable manual issuance path and must not be used for any other sprint.

## Execution

```yaml
contract_version: "1.0-bootstrap"
handoff_identifier: "bridge:ai-bridge:sprint-004:foundation-bootstrap-20260726"
lifecycle_status: "ISSUED"
contract_mode: "FOUNDATION_BOOTSTRAP"
requested_by: "Product Owner"
project:
  id: "ai-bridge"
  slug: "ai-bridge"
  name: "AI Bridge"
  definition_source: ".bridge/project.yaml"
execution:
  task_type: "SELF_DEVELOPMENT"
  intent: "Implement and prove ChatGPT to Bridge MCP communication, multi-turn project resolution, Bridge context generation, and Codex execution-package generation."
  target_repository: "zsambokia/ai-bridge"
  target_branch: "main"
  integration_target: "main"
  baseline_commit: "5c96ac0c51fb6f4ff2345a6a3e44d4a5d061ea2d"
  baseline_rule: "DESCENDANT_OF"
  worktree_policy: "MAIN_ONLY"
binding_documents:
  agents_path: "AGENTS.md"
  constitution_path: "docs/constitution/BRIDGE_CONSTITUTION.md"
  constitution_version: "Bridge Constitution v1.1"
  workflow_path: "docs/workflows/EVIDENCE_DRIVEN_SPRINT.md"
  approved_sprint_path: "docs/sprints/SPRINT_004_BASIC_AKB_MCP_CONTEXT.md"
  project_definition_path: ".bridge/project.yaml"
  current_state_path: "docs/akb/CURRENT_STATE.md"
  roadmap_path: "docs/roadmap/ROADMAP.md"
  handoff_platform_specification_path: "docs/contracts/HANDOFF_EXECUTION_CONTRACT.md"
release_gates:
  repository_wide:
    - id: "backend-tests"
      command: "pytest"
    - id: "lint"
      command: "ruff check ."
    - id: "type-check"
      command: "mypy ."
  sprint_specific:
    - id: "mcp-registration-and-reachability"
      requirement: "Prove the Sprint 004 MCP operations are registered and reachable through the canonical MCP surface."
    - id: "multi-turn-project-resolution"
      requirement: "Prove USER_INPUT_REQUIRED, continuation token handling, project selection, and stateful continuation."
    - id: "execution-context-generation"
      requirement: "Prove Bridge generates the bounded repository-bound Codex execution package required by Sprint 004."
evidence:
  root_path: "docs/evidence/sprint-004-chatgpt-bridge-mcp-execution"
  closure_report_path: "docs/evidence/sprint-004-chatgpt-bridge-mcp-execution/CLOSURE_REPORT.md"
  machine_results_paths:
    - "docs/evidence/sprint-004-chatgpt-bridge-mcp-execution/acceptance-results.json"
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
```

## Validity and consumption rules

Codex may consume this contract only when:

1. the checkout is `zsambokia/ai-bridge`;
2. the current branch is `main`;
3. current HEAD is the baseline commit above or a descendant of it;
4. the Sprint 004 file still has status `APPROVED FOR CODEX EXECUTION`;
5. the binding documents are readable and not materially contradictory;
6. the execution remains within Sprint 004 scope.

The contract authorizes immediate repository assessment and implementation after preflight. The absence of a running Handoff Generator is not a blocker for this single execution because implementing and proving its replacement execution-context path is part of the authorized Sprint 004 scope.

## Mandatory closure action

Sprint 004 must replace this one-time mechanism with a tested canonical Bridge-generated execution context / package flow. Closure evidence must state whether this manual bootstrap contract can be retired. It must not silently become the normal issuance mechanism.
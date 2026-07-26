# Sprint 004 — ChatGPT ↔ Bridge MCP Execution Foundation

**Status: APPROVED FOR CODEX EXECUTION**

## Purpose

Enable ChatGPT to call the Bridge through a lightweight MCP interface, resolve a
target Project from the canonical Project Registry, request an explicit choice
when resolution is ambiguous, and generate a repository-bound Execution Context
for Codex. The Context, not a hand-written handoff, is the canonical input.

## Approved scope

- registered lightweight MCP operations and reachable transport;
- Project Registry lookup through `resolve_project`;
- durable `USER_INPUT_REQUIRED` continuation tokens for ambiguous resolution;
- a Bridge Execution Context Generator based on Project Registry, Project
  Context, `.bridge/project.yaml`, and an explicit approved Sprint path;
- a machine-readable Codex execution package derived from that Context;
- tests, architecture documentation, AKB synchronization, and evidence.

## Explicit exclusions

- AKB indexing, knowledge graph, vector database, or Discovery engine;
- automatic architecture discovery, autonomous planning, or roadmap rewriting;
- a large user interface or a parallel Project/Context implementation.

## Acceptance scenarios

1. MCP operations are registered and reachable through the Bridge transport.
2. The Bridge never guesses a `project_id`; ambiguous matching returns
   `USER_INPUT_REQUIRED`, candidates, and a continuation token.
3. The continuation resumes the same persisted state and accepts only a listed
   project selection.
4. An explicit Project and approved Sprint generate an Execution Context with
   repository, branch, baseline rule, binding documents, release gates,
   evidence path, allowed terminal states, and a unique execution identifier.
5. The generated package derives from Registry, Project Context, and repository
   configuration, not conversation memory or a hand-written handoff.

## Required Release Gates

```text
pytest
ruff check .
mypy .
```

Evidence must be stored under
`docs/evidence/sprint-004-chatgpt-bridge-mcp-execution`.

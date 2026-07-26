# Sprint 004 — ChatGPT ↔ Bridge MCP Execution Foundation

**Status:** APPROVED FOR CODEX EXECUTION

## Vision
Prove the first end-to-end execution path between ChatGPT and the Bridge.

Success means:
1. ChatGPT calls the Bridge through MCP.
2. The Bridge resolves the target project (asking the user when ambiguous).
3. The Bridge generates the canonical execution context.
4. The Bridge prepares an execution package for Codex.

## In scope
- Lightweight MCP server.
- Project Registry lookup.
- resolve_project workflow.
- Multi-turn continuation tokens.
- USER_INPUT_REQUIRED interaction model.
- Context Generator.
- Execution package generation for Codex.

## Explicitly out of scope
- Full AKB indexing.
- Knowledge graph.
- Vector search.
- Autonomous planning.
- Large UI.

## Acceptance
Demonstrate:
- ChatGPT → Bridge MCP communication.
- Ambiguous project resolution.
- User selects a project.
- Bridge continues without losing state.
- Bridge generates the execution context.
- Codex receives the generated context instead of a manually written handoff.

## Evidence
Document the protocol, MCP schemas, example request/response flows and the generated execution context.
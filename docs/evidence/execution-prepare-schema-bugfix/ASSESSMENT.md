# `execution.prepare` schema bugfix assessment

## Root cause

The public MCP registry declared a bounded input schema, but the shared runtime
validator collapsed all missing and unknown fields into one generic message.
The proposal schemas also accepted unconstrained policy vocabulary.

## Repair

`projects/governed_mcp.py` now derives validation from the same `TOOLS` input
schema returned by `public_tools()`. The schema factory rejects undeclared
required fields. Runtime failures name the exact field, type, or enum violation.
Proposal vocabulary is declared from canonical contract-policy constants.

## Authority and compatibility

`execution.prepare` remains canonical-scope-only. Natural language is proposed,
validated, durably approved, and published before preparation. Legacy fields
such as `sprint_path` are rejected as unknown. No validation relaxation,
compatibility fallback, mock contract, or direct repository mutation was added.

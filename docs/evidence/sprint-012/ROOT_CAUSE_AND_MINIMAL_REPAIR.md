# Root cause and minimal repair

The repair changes only the existing public MCP boundary:

1. `scope.review` returns the required continuation data: project, scope,
   proposal review, `next_tool: conversation.confirm`, and the sole required
   user input, `confirmation_text`, when eligible.
2. `conversation.confirm` accepts only the displayed project, scope, and
   affirmative text. The service derives a deterministic binding from the
   authenticated MCP caller, exact current proposal version/hash, and accepted
   confirmation text. It supplies the resulting auditable identity,
   confirmation reference, and idempotency key to the existing orchestration.
3. `scope.confirm_and_execute` remains unchanged in authority and is described
   as the advanced structured path. `scope.approve` remains strict.

The derivation is deterministic for the same caller, scope, proposal, and
phrase, preventing retry duplication while refusing caller-supplied forged
identity/reference fields through schema validation. The service’s identity is
an authenticated MCP-caller binding, not a claim that Bearer authentication
attests an individual human. The connector must invoke this tool only after the
Product Owner’s message; standard MCP does not itself transmit per-message
human authorship.

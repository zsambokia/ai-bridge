# Negative proofs

- An unsupported provider identity is rejected during consumption; it cannot
  fall back to `codex-cli`.
- Read-only Audit completion rejects changed files outside its evidence root.
- `scope.approve` was not used for the conversational proof.
- The proof scope was newly created as `WORK_ITEM` / `AUDIT`; no new executable
  hierarchy level was introduced.

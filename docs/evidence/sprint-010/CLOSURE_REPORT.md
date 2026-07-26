# Sprint 010 closure remediation report

**Result:** PASS — READY FOR PRODUCT OWNER REVIEW
**Validated implementation commit:** `9d23d59f4b4b530ee26876ac1d71985c1a95b10a`
**Baseline before remediation:** `b5b5460b630050eb74b06a8cbd2f843aa1e21edd`

## Delivered and proven

- `ExecutableScope` is the runtime authority for executable Sprint and ad hoc
  Work Item records. Epic is not executable. `projects.scopes.close_scope` and
  public `scope.complete`, `scope.cancel`, and `scope.supersede` terminalize a
  scope; the approved-scope checks reject it from further contract lifecycle.
- Canonical scope data is validated against the versioned JSON schemas and
  published as a deterministic Markdown projection. The legacy Markdown parser
  is import/read-only; the legacy contract generator always raises
  `LEGACY_CONTRACT_GENERATION_DISABLED`.
- Only AI Bridge creates schema `2.0` contracts. Validation, issue, consume,
  and run start each recheck the scope publication and bound, non-revoked
  approval. An Execution Provider cannot issue its own contract.
- Consumption persists provider identity, exact contract hash, observed
  baseline, schema version, idempotency key, timestamp, and a unique receipt.
  A receipt and canonical validation are required before execution starts.
- Completion requires a matching `ExecutionRun` to have reached a terminal
  state at the actual checked-out final SHA, plus non-empty gates and evidence.
  Public `contract.complete` supplies all completion inputs and cannot bypass
  the run lifecycle.
- Historical Sprint 005–009 documents stay readable but are not executable
  authority. The governed MCP registry exposes the canonical scope and full
  contract lifecycle instead.

## Release gates

| Gate | Result |
| --- | --- |
| `python manage.py makemigrations --check` | PASS — no changes detected |
| `pytest` | PASS — 40 passed |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS — 55 files already formatted |
| `mypy .` | PASS — 55 source files |
| `python manage.py validate_scopes` | PASS — all canonical scopes valid |
| `git diff --check` | PASS |

The machine-readable results are in `acceptance-results.json`. The evidence
commit is intentionally separate from the validated implementation commit so
the report binds a real, immutable code revision rather than claiming a
self-referential final SHA.

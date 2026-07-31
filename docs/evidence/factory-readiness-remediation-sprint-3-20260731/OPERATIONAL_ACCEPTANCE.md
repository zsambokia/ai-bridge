# Sprint 3 operational acceptance evidence

## Controlled runtime

A fresh local Django runtime was started against an isolated SQLite database on
`127.0.0.1:8766`. It used the repository's local settings and applied the
Sprint 3 migration. This is a real HTTP runtime, not a Django test client.
Secrets, bearer tokens, and local admin credentials are intentionally omitted.

## Successful proof

1. A real authenticated HTTP MCP `conversation.confirm` created a fresh,
   governed Orki session and queued execution.
2. The resulting execution status exposed context package
   `e73b55655807e4d142f84d22fbcdfb827897430bbb62858d0d3f2914539dc755`,
   package ID `5`, source version `po-runtime-1`, session
   `c3edff2a-eef4-4e75-8b5c-ab5942840899`, decision hash, and the queued run.
3. The real HTTP MCP `akb.get_context_usage` and a direct runtime database
   inspection agreed that the same use record bound session `2`, decision `2`,
   execution contract `2`, and execution run `2`.
4. A second-project context request returned zero entries, proving no
   cross-project knowledge leakage.
5. Real HTTP MCP roadmap calls created a `PROPOSED` item, created candidate
   `1`, and only after an approval reference changed that candidate to `ACTIVE`
   and the item to `COMPLETED`. The final MCP projection reported both
   acceptance statuses `PASS`, the baseline SHA, and the evidence reference.
6. Authenticated Django Admin returned HTTP 200 for the context-package,
   context-use, roadmap-item, and roadmap-update-candidate read-only lists. The
   package list contained the exact MCP hash and the roadmap list contained the
   same item key, proving projection consistency.

The verified execution remained correctly `QUEUED`; this Sprint proves the
knowledge/roadmap feedback loop's run binding, not a new provider-completion
capability. Sprint 1 recovery remains regression-covered by the full suite.

## Runtime/API boundary

The repository's public machine API is the authenticated Streamable HTTP MCP
endpoint. No separate REST API is implemented or claimed. Admin and MCP are
therefore the applicable operational projections for this scope.

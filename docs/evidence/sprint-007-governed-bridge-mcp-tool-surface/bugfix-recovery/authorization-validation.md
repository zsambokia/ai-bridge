# Authorization validation

Prior authenticated staging probing established JSON-only `401` rejection for
both an absent Bearer token and an invalid Bearer token. No login redirect or
HTML error was observed. A valid-token rerun is pending the required staging
migration, because every valid tool call currently reaches the missing audit
table and returns HTTP 500.

Negative governed-tool checks previously reached canonical rejection paths for
unknown tools, missing lifecycle approval, and missing idempotency keys. They
must be repeated after deployment as listed in `acceptance-results.json`.

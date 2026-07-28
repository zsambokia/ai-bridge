# Compatibility validation

- Valid execution-token operations retain their existing result schemas and
  authority requirements.
- A malformed token returns `INVALID_EXECUTION_TOKEN`.
- A syntactically valid token without a canonical run returns
  `EXECUTION_NOT_FOUND` for all four affected tools.
- Cancellation still requires its approval reference before any active run can
  be changed; an already cancelled run is a safe idempotent retry.
- Full repository gates passed after the repair; see `acceptance-results.json`.

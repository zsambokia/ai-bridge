# Acceptance results

- Valid Factory execution with matching commit, scope-bound evidence, PASS audit, and acceptance: PASS.
- Incorrect commit: rejected.
- Missing evidence: rejected.
- Incorrect scope identifier: rejected.
- Repeated identical request: returns the same reconciliation record.
- Repeated request with changed evidence: rejected.
- No provider execution, execution contract consumption, or synthetic runtime event is created by the reconciliation service: PASS by implementation and audited event assertion.

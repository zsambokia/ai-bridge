# Operational Acceptance

## Acceptance scenario

A repository test constructs a governed structured decision and executes the
canonical Runtime path. Verification completes, then the Runtime creates one
explicit reflection candidate and one explicit knowledge candidate with evidence.

## Acceptance result

PASS. Candidate records contain required contract fields, preserve the
execution/goal relationship, contain no generic payload, create no KnowledgeEntry,
and cannot be modified after creation. The full suite additionally passes existing
Factory Acceptance and canonical Runtime regression tests.

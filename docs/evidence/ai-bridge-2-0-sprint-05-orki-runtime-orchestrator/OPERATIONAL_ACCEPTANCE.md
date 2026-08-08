# Operational Acceptance — AI Bridge 2.0 Sprint 05

## Intended runtime

The accepted runtime is the repository's configured Django application on
`main`, evaluated from the final reproducible working tree described in the
closure report. This Sprint adds an in-process, provider-neutral orchestration
boundary. It does not claim that a separate deployed provider, worker, or
production environment was observed.

## Runtime smoke

`projects.tests.test_structured_decision_runtime.StructuredDecisionRuntimeTests`
executes the real Django model and Runtime services with an isolated test
database. The passing scenario starts a validated `StructuredDecision.v1`,
creates the runtime goal and plan, executes through the explicit operation
gateway, verifies an evidence-bearing result, records reflection and knowledge
candidates, and completes without creating an AKB `KnowledgeEntry`.

The failure scenario raises a real operation error, records `FAILED`, and
proves recovery through `RECOVERY -> RETRYING`. The legacy mission test is also
executed to prove that the isolated compatibility adapter preserves the
existing knowledge integration path during migration.

## Result

PASS — the repository-native Runtime boundary is operational and its
recoverable canonical path has been observed. No unobserved external
environment is represented as accepted.

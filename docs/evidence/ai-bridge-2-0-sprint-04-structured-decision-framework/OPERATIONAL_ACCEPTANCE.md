# Operational Acceptance — Sprint 04

## Intended runtime

The Sprint exposes an in-process Django HTTP boundary only. Deployment,
provider invocation, and Runtime execution are explicitly out of scope.

## Runtime smoke

`StructuredDecisionFrameworkTests.test_decision_api_is_contract_only_and_auditable`
uses the configured Django request path to create a valid contract, retrieve it
by ID, and obtain the schema. The test proves the operating HTTP boundary does
not start execution; the schema declares `execution: forbidden`.

## Acceptance result

PASS for the Sprint 04 in-process API boundary. No external deployed-runtime
claim is made, because the approved scope forbids Runtime execution.

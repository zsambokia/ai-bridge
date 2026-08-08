# Architecture Validation

## Canonical flow

StructuredDecision → Planning → Execution → Verification →
RuntimeReflectionCandidate → RuntimeKnowledgeCandidate → Knowledge Pipeline.

The Runtime remains the execution implementation base. This Sprint changes only its
emitted candidate contract after verification: it introduces no autonomous
execution, Runtime business decision, AKB ownership, or vector ownership.

## Boundary validation

- projects.runtime_contract is the canonical schema and validator authority.
- The canonical Runtime validates and persists explicit candidate fields only.
- OrkiKnowledgeIntegration is isolated as a temporary compatibility adapter and is
  not called from the canonical structured-decision path.
- docs/architecture/RUNTIME_CONTRACT.md is the current architecture reference.

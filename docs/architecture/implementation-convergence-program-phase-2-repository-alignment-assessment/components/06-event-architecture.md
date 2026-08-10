# Event Architecture Assessment

## Target Architecture

Kernel Events are immutable, provider-neutral first-class Kernel Objects, correlated to execution/evidence and safe for telemetry. Domain, operational, and knowledge events retain their owners while using coherent envelopes.

## Current Repository

`ExecutionProgressEvent`, `OrkiRuntimeEvent`, `WorkflowEvent`, provider audit events, and knowledge receipts are separately persisted. `runtime_api.py` streams “runtime” SSE events; `execution.py` appends delivery events.

## Gap Analysis

**Partial:** durable append-oriented event records and sequence behaviour exist. **Missing:** one envelope/schema/versioning policy, common correlation and scope metadata, event registry, and explicit Kernel-vs-domain ownership rules. **Legacy:** event names retain Runtime and source-specific semantics.

## Migration Strategy

Define a versioned envelope and project existing streams into it. Preserve native records as sources of truth during migration; expose a neutral stream before deprecating source-specific client contracts.

## Risks and Dependencies

Event replay, ordering, and secret exposure are high-risk. Depends on Execution mapping, scope model, AKB lifecycle event design, and security policy.

## Readiness

**Partially Ready.** Existing durable signals provide migration data, but no uniform event contract exists.

## Evidence

`projects/models.py` (`ExecutionProgressEvent`, `OrkiRuntimeEvent`, `WorkflowEvent`, `ProviderAuditEvent`); `projects/execution.py`; `projects/runtime_api.py`; `projects/workflow_engine.py`.

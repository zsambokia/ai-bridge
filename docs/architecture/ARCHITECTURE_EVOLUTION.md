---
status: HISTORICAL
owner: Architecture
supersedes: []
superseded_by: Constitution Book evolution record (planned adoption)
version: 1.0.0
---

# Architecture Evolution

> **Historical architecture snapshot (2026-08-10):** This timeline preserves
> prior repository terminology and topology as evidence. Its Runtime and
> Provider Gateway labels are not target terminology; use the Constitution
> Book plan and Article III for approved target terms.

## Interpretation

Architecture status is evidence-based. A target document sets direction; it
does not prove that a current route has migrated. Individual document front
matter is the source of truth for document status.

## Current

The repository currently contains reusable delivery mechanics, including
`ExecutionRun` and `ExecutionJob`, and historical Orki/OESM-oriented
components and documentation. The approved R20-00 baseline found no proven
end-to-end target route: Factory Chat still has a synchronous workflow/provider
path, while durable Execution Request, MSM, authorized Operational Work Item,
and `MISSION_READY_FOR_PLANNING` are not established as the canonical
end-to-end implementation. See the [Runtime 2.0 Constitution](../runtime/runtime_2_0_constitution.md)
and its linked evidence.

## Transitional

Existing architecture assessments, integration plans, legacy Orki runtime
material, and compatibility names are transitional or historical according to
their front matter. They may explain migration constraints, but they do not
override a canonical constitution or create a bypass.

## Target

The target is the constitutional route:

```text
Engine → immutable Execution Request → MSM → authorized Operational Work Item
       → Operational Foundation → ExecutionRun → Provider Gateway → Provider
```

Target compliance requires separately governed migration, validation, and a
Constitution Compliance Assessment. No status changes from transitional to
canonical implementation compliance without fresh evidence.

## Migration rule

Migration SHALL be incremental and reversible where practical. Each change
shall name the legacy route, affected authority, compatibility boundary,
validation, evidence, and retirement condition. Historical records are never
silently rewritten.

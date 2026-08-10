---
status: SUPPORTING
owner: Runtime
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-016: Runtime Is the Mission Coordinator Only

**Decision:** accepted.

Runtime, represented by the MSM in the target architecture, coordinates Mission
lifecycle, authorization, and projections. It does not absorb Planning,
Workflow, Repository, Knowledge, or provider business logic. The detailed
authority model remains the [Runtime 2.0 Constitution](../../runtime/runtime_2_0_constitution.md).

---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-017: Make the Operational Foundation the Canonical Engine Boundary

**Decision:** accepted.

Domain Engines do not call each other or provider-bound infrastructure
directly. An Engine emits an immutable Execution Request; MSM may authorize an
immutable Operational Work Item; only then may the Operational Foundation
deliver the work. This makes cross-domain and provider interactions durable,
recoverable, and reconstructible.

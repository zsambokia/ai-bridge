---
status: SUPPORTING
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
---

# ADR-019: Make State-Machine Ownership Explicit

**Decision:** accepted.

Every durable lifecycle has one named state-machine owner. MSM owns Mission
state; each Domain Engine owns its own state; the Operational Foundation owns
delivery mechanics. Cross-domain progression uses durable events, requests,
results, Work Items, and evidence, never direct cross-state writes. The binding
rule is [State Machine Constitution](../STATE_MACHINE_CONSTITUTION.md).


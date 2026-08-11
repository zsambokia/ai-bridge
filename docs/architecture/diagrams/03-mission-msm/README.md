---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 03 — Mission & Mission State Machine

## Purpose

Canonical logical source: [`03_MISSION_MSM.md`](03_MISSION_MSM.md) (Mermaid). The `.drawio` file is its derived, editable visual representation.

Shows Mission as the first runtime business object and MSM as its exclusive
lifecycle authority.

## Responsibility and ownership

Mission owns identity, goal, scope, priority, correlation, and Evidence
references. MSM alone owns lifecycle transitions and may authorize an immutable
Operational Work Item; it cannot invoke Engines or Providers directly.

## Contracts, lifecycle, and rules

Mission-intake decisions enter MSM. State transitions emit attributable events;
only an authorized immutable Work Item crosses to Operational Foundation.
Commands, events, and Evidence are distinct contracts.

## Failure, evidence, and open questions

Invalid transitions are rejected and evidenced. Retry and delivery mechanics
belong to Operational Foundation. Detailed Mission states remain governed by the
Mission State Machine Constitution.

## Related authority and maintenance

Article IV and the State Machine Constitution. Update with lifecycle ownership,
Work Item, or event-contract changes.

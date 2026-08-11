---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 05 — Planning Engine

## Purpose

Canonical logical source: [`05_PLANNING_ENGINE.md`](05_PLANNING_ENGINE.md) (Mermaid). The `.drawio` file is its derived, editable visual representation.

Documents Planning Engine as a stateless Capability Engine that returns
planning results to its caller without owning Mission or Execution state.

## Responsibility and ownership

The Engine may access business data in its bounded context but keeps no
operational execution state. MSM remains lifecycle owner; Kernel owns Execution.

## Contracts, lifecycle, and rules

A scope-aware planning request, Context Package references, and policy enter;
a versioned plan, rationale, and Evidence references leave. The Engine is a
Capability implementation, not a Runtime entry point.

## Failure, evidence, and open questions

Failure is returned as attributable result or event for the caller's policy.
Planning algorithm, persistence, and capabilities require later implementation
decisions.

## Related authority and maintenance

Architecture Constitution Capability principles and Article IV. Update when
planning capability contracts or ownership change.

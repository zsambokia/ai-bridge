---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---

# Diagram 02 — Runtime Boundary

## Purpose

Canonical logical source: [`02_RUNTIME_BOUNDARY.md`](02_RUNTIME_BOUNDARY.md)
(Mermaid). The `.drawio` file is its derived, editable visual representation.

Defines Mission as the unified runtime intake while preserving Conversation as
the mandatory route for human interaction only.

## Responsibility and ownership

Conversation, API, MCP, Scheduler, Webhook, and Automation adapters submit
governed Mission-intake requests. Mission and MSM own business lifecycle; the
Runtime Boundary owns no business state.

## Contracts, lifecycle, and rules

Inputs are attributable intake requests. Outputs are accepted, rejected, or
no-action decisions and an MSM-owned Mission. Every intake has scope,
correlation, authorization, and Evidence. No adapter bypasses Mission or MSM.

## Failure, evidence, and open questions

Unauthorized or incomplete requests are rejected without Kernel work. Evidence
records source, decision, and correlation. Transport-specific API/MCP shapes
remain implementation concerns.

## Related authority and maintenance

Article IV — Conversation to Mission Architecture; Article III — AI Kernel.
Update the Mermaid source and its Diagram Impact Assessment with any
intake-boundary change. The editable `.drawio` remains aligned as a derived
visual representation.

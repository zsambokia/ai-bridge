---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 04 — Operational Foundation

## Purpose

Canonical logical source: [`04_OPERATIONAL_FOUNDATION.md`](04_OPERATIONAL_FOUNDATION.md) (Mermaid). The `.drawio` file is its derived, editable visual representation.

Defines Operational Foundation as an independent architectural layer that
admits, schedules, leases, and delivers MSM-authorized work to the AI Kernel.

## Responsibility and ownership

It owns operational handoff mechanics, not Mission intent, lifecycle, Engine
business state, or Kernel Execution. Inputs are immutable Work Items; output is
admitted work and attributable delivery events.

## Contracts, lifecycle, and rules

Admission, queueing, lease, retry, recovery, and delivery are governed
operational mechanics. The Foundation never reinterprets business intent or
writes Mission state.

## Failure, evidence, and open questions

Delivery failure follows Foundation recovery policy and emits Evidence; it does
not silently alter Mission semantics. Storage and queue products are open
implementation decisions.

## Related authority and maintenance

Operational Foundation Constitution and Article IV. Update with handoff,
admission, lease, or delivery-boundary changes.

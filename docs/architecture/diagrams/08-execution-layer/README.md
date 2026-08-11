---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 08 — Execution Layer

## Purpose

Canonical logical source: [`08_EXECUTION_LAYER.md`](08_EXECUTION_LAYER.md) (Mermaid). The `.drawio` file is its derived, editable visual representation.

Establishes `Execution` as the sole first-class, Kernel-owned target execution
object and makes its provider binding immutable during a run.

## Responsibility and ownership

Execution owns technical lifecycle, Context reference, provider binding,
events, and Evidence references. Provider Executors may be stateful but do not
own Execution. Lease and queue mechanics remain Foundation concerns.

## Contracts, lifecycle, and rules

An admitted work item creates Execution; capability/provider selection records
an immutable binding; results update Execution and emit Kernel Events. Recovery
uses the same Provider only when its Runtime Profile permits it.

## Failure, evidence, and open questions

Provider unavailability blocks, awaits, or fails according to policy; it never
silently switches Provider. `ExecutionRun` and `ExecutionJob` are dashed
Historical / Transitional implementation labels pending ADR decisions.

## Related authority and maintenance

Article III, Provider Architecture v2, ADR-034 and ADR-038.

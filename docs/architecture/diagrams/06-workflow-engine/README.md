---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 06 — Workflow Engine

## Purpose

Shows Workflow Engine as a stateless Capability Engine that interprets a
versioned workflow definition without becoming a Mission lifecycle owner.

## Responsibility and ownership

The Engine provides workflow capability; Execution and operational state remain
outside it. MSM owns Mission state, Operational Foundation owns delivery, and
Kernel owns technical Execution.

## Contracts, lifecycle, and rules

Inputs are authorized work, workflow definition reference, Context Package,
and policy. Outputs are results, events, and Evidence. Workflow definitions
are Knowledge Objects; a running workflow is not an AKB object.

## Failure, evidence, and open questions

Step failure is reported through owning operational and Mission policies; no
direct Provider invocation bypass is permitted. Concrete orchestration DSL is
not decided here.

## Related authority and maintenance

Capability, AKB, Operational Foundation, and Article IV Constitutions.

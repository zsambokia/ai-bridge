---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 12 — Reflection & Learning

## Purpose

Shows how attributable Evidence can inform governed Reflection and learning
without allowing runtime output to mutate AKB directly.

## Responsibility and ownership

Execution and domain events produce Evidence. Reflection proposes knowledge
changes; Knowledge Lifecycle Management owns planning, synchronization, and
publication. AKB owns the published Knowledge Object.

## Contracts, lifecycle, and rules

Inputs are Evidence, decision references, and policy. Outputs are a proposed
reflection, update plan, and eventually published immutable Knowledge Object
versions. No direct document modification or unreviewed knowledge write exists.

## Failure, evidence, and open questions

Low-confidence reflection remains proposal/evidence, not fact. Publication
failure leaves existing AKB versions valid. Review policy and scoring need
future ADRs where they create an authority contract.

## Related authority and maintenance

AKB Lifecycle Constitution, Evidence principles, and Article V governance.

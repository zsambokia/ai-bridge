---
architecture_status: APPROVED
owner: Product Owner and Architecture
classification: FACTORY DEVELOPMENT MODE SPRINT
language: en
baseline: 5232d7fb41c353d022184facb4f3b65250202be1
scope: documentation-and-diagrams-only
---

# Architecture Documentation & Visual Constitution Program

## Approved scope

Create and govern the canonical AI Bridge Visual Constitution. This Factory
Development Mode sprint covers Architecture Constitution updates, the visual
diagram set, its Markdown companions, cross-references, and evidence only. It
does not authorize implementation, schema, API, model, Runtime, workflow, or
provider changes.

## Binding decisions

- `Execution` is the one first-class, Kernel-owned target execution object.
  `ExecutionRun` and `ExecutionJob` remain Historical / Transitional until
  their ADRs close.
- The canonical provider route is `Execution -> Provider Integration ->
  Provider Resolver -> Provider -> Provider Executor`.
- Provider Gateway is an implementation adapter/boundary only; it is not a
  canonical architecture object.
- Mermaid in a version-controlled Markdown document is the only canonical
  logical source. `.drawio` is a derived visual representation and must not
  diverge from Mermaid; rendered assets are also derived and may be generated
  by a documentation release or CI.
- Every diagram declares an Architecture Status under ADG-107.

## Completion contract

The program closes only when the visual set, Constitution, Constitution Book
plan references, Diagram Impact Assessment, validation evidence, and closure
record are mutually consistent. Any constitutional ambiguity discovered while
drawing is recorded as an open Architecture Challenge rather than resolved by
inventing a new target model.

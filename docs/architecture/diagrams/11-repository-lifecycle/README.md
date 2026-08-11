---
architecture_status: CANONICAL
owner: Architecture
classification: VISUAL CONSTITUTION
language: en
---
# Diagram 11 — Repository Lifecycle

## Purpose

Shows Repository as a scoped resource whose changes can become governed
Knowledge Lifecycle inputs rather than uncontrolled runtime knowledge.

## Responsibility and ownership

Organization, Workspace, and Project provide scope and ownership. Repository
is a Project-owned resource. Change Detection observes repository events but
does not mutate AKB directly.

## Contracts, lifecycle, and rules

Repository change produces an attributable Knowledge Change Event; the Update
Planner decides representations and priority; publication produces immutable,
queryable AKB versions and Context invalidation when required.

## Failure, evidence, and open questions

Unavailable repository sources are evidenced; stale knowledge is measurable and
recoverable. SCM provider integration and repository policy are implementation
choices.

## Related authority and maintenance

Scope Architecture, AKB Lifecycle Constitution, and Architecture Book Part 1.

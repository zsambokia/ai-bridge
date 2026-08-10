---
status: ACCEPTED_TARGET
owner: Architecture
supersedes: []
superseded_by: null
version: 1.0.0
canonical_language: en
authority: Product Owner Decision Alignment (2026-08-10)
---

# ADR-037 -- Localization and Canonical Language

## Decision

Canonical code and technical identifiers are English, including code, APIs, schema, Capability identifiers, events, states, configuration keys and internal technical contracts. They SHALL NOT vary with active UI language.

AI Bridge SHALL provide first-class multilingual capability for eligible UI, Knowledge, Persona communication, Conversation, documentation, descriptions, generated artifacts and human-facing summaries. Complete translation coverage is not required.

Original Evidence preserves its original content and language. A translation is a separate, traceable derived representation and SHALL NOT overwrite, mutate or replace source Evidence. Knowledge localization preserves the conceptual relationship `Knowledge identity -> Knowledge Version -> language representations`; translations do not automatically create unrelated Knowledge identities.

## Deferred design

This ADR intentionally does not select a representation data model, locale standard/binding, fallback rule, publication lifecycle, inheritance or sharing semantics. Those are explicit Phase 3 implementation-design decisions.

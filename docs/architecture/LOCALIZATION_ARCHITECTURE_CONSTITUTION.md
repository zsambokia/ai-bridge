---
status: APPROVED_TARGET
owner: Architecture
version: 1.0.0
canonical_language: en
authority: Product Owner Directive (2026-08-10)
---

# Article VII — Localization Architecture

## Authority and status

This approved target Constitution Book entry defines the language boundary for
AI Bridge. It is documentation architecture only: it does not authorize a
localization framework, schema, API, migration, or runtime change.

## VII.1 Canonical machine language

Canonical code and technical identifiers SHALL be English. This includes code,
API identifiers, schema identifiers, Capability identifiers, event and state
names, configuration keys, and internal technical contracts. An active UI
language MUST NOT translate, mutate, or replace those identifiers.

Normative Constitution Book entries and ADRs are authored in English. A
localized rendering is a derived representation and SHALL retain the
canonical entry's identifier, version, provenance, and meaning.

## VII.2 Localizable content

AI Bridge SHALL provide first-class multilingual support for appropriate
user-facing and semantic content. Eligible content includes UI labels and
messages, Knowledge, Persona communication, Conversation, documentation,
descriptions, generated artifacts, and human-facing summaries.

Localization readiness requires the capability to represent language and
provenance; it does not require every item to be translated into every
language. Translation coverage and fallback behaviour are product and
implementation decisions, not an implicit English-only rule.

## VII.3 Evidence language integrity

Evidence SHALL preserve its original/source representation and language. A
translation MAY be attached as a separately attributable derived
representation, but MUST NOT overwrite, mutate, or replace the source
Evidence. Traceability from every translation to its original Evidence SHALL
be preserved.

```text
Evidence
  ├── Original representation
  └── Translated representation(s)
```

## VII.4 Knowledge localization

Knowledge is scope-aware under Article VI and localization-ready under this
Article. Translation SHALL NOT automatically create an unrelated Knowledge
identity. The target conceptual relationship is:

```text
Knowledge identity
  → Knowledge version
      → representation(s) by language
```

The representation abstraction, version binding, fallback rules, translation
lifecycle, and inheritance interaction remain open architecture questions.
They require ADR-037 before implementation. This Article preserves the AKB
distinction between Knowledge identity, immutable version, representations,
graph, embeddings, retrieval infrastructure, and Context Package selection.

## VII.5 Architectural consequences

1. Canonical technical identifiers remain language-stable across all UI and
   semantic representations.
2. Localization is not limited to UI translation.
3. No source Evidence may be silently translated or replaced.
4. Current English-only models and direct text fields are implementation gaps,
   not constraints on the approved target architecture.

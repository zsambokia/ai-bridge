# Localization Assessment

## Target Architecture

Article VII requires English canonical code and technical identifiers,
including APIs, schema, Capabilities, events, states, configuration and
internal contracts. It also requires first-class multilingual capability for
appropriate UI, Knowledge, Persona communication, Conversation, documentation,
descriptions, generated artifacts and human-facing summaries. Translation
coverage is not required to be complete.

Original Evidence preserves its content and language. A translation is a
separate, traceable derived representation and MUST NOT overwrite or replace
the source. Knowledge localization conceptually preserves `identity -> version
-> language representations`; the detailed representation mechanics remain
open in ADR-037.

## Current Repository

The inspected Django settings and application source contain no configured `LANGUAGES`, translation catalogue use, or localized domain asset model. Text content is stored directly in mission and knowledge records.

## Gap Analysis

**Missing:** platform locale policy implementation, language metadata,
canonical/source relationship, translation lifecycle, UI catalogues, localized
prompts/personas/knowledge/documentation, source/derived Evidence handling and
the ADR-037 representation design. Existing text fields are a future migration
surface.

## Migration Strategy

The constitutional boundary is approved. A Phase 3 Sprint must first resolve
ADR-037, then introduce the chosen representation model and UI support under
approved implementation authority. Migrate high-value assets by versioned,
traceable representation rather than bulk text replacement; never rewrite
source Evidence.

## Risks and Dependencies

Translation can change meaning, evidence interpretation, and policy behaviour. Depends on Knowledge Object identity, Identity & Scope, and provider prompt contracts.

## Readiness

**Not Ready.** The constitutional localization boundary is approved, but its
representation, fallback and lifecycle model remains an explicit ADR-037
decision before implementation.

## Evidence

`bridge/settings/base.py`; `projects/models.py` (`FactoryMission`, `KnowledgeEntry`); repository search for `LANGUAGES`, `gettext`, `translation`, and locale configuration.

# Localization Assessment

## Target Architecture

English is canonical for normative architecture, ADRs, capabilities, and internal identifiers. UI, prompts, personas, knowledge, documentation, and business-relevant evidence are localization-ready with attributable language/version semantics.

## Current Repository

The inspected Django settings and application source contain no configured `LANGUAGES`, translation catalogue use, or localized domain asset model. Text content is stored directly in mission and knowledge records.

## Gap Analysis

**Missing:** locale policy, language metadata, canonical/source relationship, translation lifecycle, UI catalogues, localized prompts/personas/knowledge/documentation, and evidence language criteria. Existing text fields are a future migration surface.

## Migration Strategy

Approve a localization ADR first. Add language and canonical-reference metadata to new constitutional objects; introduce UI catalogue support independently. Migrate high-value assets by versioned representation, not bulk text replacement.

## Risks and Dependencies

Translation can change meaning, evidence interpretation, and policy behaviour. Depends on Knowledge Object identity, Identity & Scope, and provider prompt contracts.

## Readiness

**Not Ready.** No foundational localization policy or model exists.

## Evidence

`bridge/settings/base.py`; `projects/models.py` (`FactoryMission`, `KnowledgeEntry`); repository search for `LANGUAGES`, `gettext`, `translation`, and locale configuration.
